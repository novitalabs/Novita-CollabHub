import asyncio
import requests
import time
import re
import os
import logging
from dotenv import load_dotenv
load_dotenv()
from browser_use import Agent, BrowserSession
from browser_use.llm import ChatOpenAI
from e2b_code_interpreter import Sandbox
from playwright.async_api import Page
from urllib.parse import urlparse

LLM_BASE_URL = os.getenv("LLM_BASE_URL")
LLM_MODEL = os.getenv("LLM_MODEL")
LLM_API_KEY = os.getenv("LLM_API_KEY")

async def test_chrome_connection(host):
    """Test Chrome connection and get debug information"""
    
    print(f"\n=== Debug Chrome Connection ===")
    print(f"Test host: {host}")
    
    # Configuration to disable proxy
    proxies = {
        'http': None,
        'https': None,
    }
    
    # Test basic connection
    try:
        response = requests.get(f"https://{host}/json/version", timeout=10, proxies=proxies)
        print(f"Basic connection test: {response.status_code}")
        print(f"Response content: {response.text[:200]}...")
    except Exception as e:
        print(f"Basic connection failed: {e}")
    
    # Test /json endpoint
    try:
        response = requests.get(f"https://{host}/json", timeout=10, proxies=proxies)
        print(f"/json endpoint test: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"Found {len(data)} targets")
            for i, target in enumerate(data[:2]):  # Only show first 2
                print(f"  Target {i}: {target.get('type', 'unknown')} - {target.get('url', 'no url')}")
        else:
            print(f"Response content: {response.text[:200]}...")
    except Exception as e:
        print(f"/json endpoint failed: {e}")
    
    # Test /json/version endpoint
    try:
        response = requests.get(f"https://{host}/json/version", timeout=10, proxies=proxies)
        print(f"/json/version endpoint test: {response.status_code}")
        if response.status_code == 200:
            version_data = response.json()
            print(f"Chrome version: {version_data.get('Browser', 'unknown')}")
            print(f"WebSocket URL: {version_data.get('webSocketDebuggerUrl', 'not found')}")
        else:
            print(f"Response content: {response.text[:200]}...")
    except Exception as e:
        print(f"/json/version endpoint failed: {e}")
    
    print("=== Debug completed ===\n")

async def get_chrome_wss_url(host):
  proxies = {
      'http': None,
      'https': None,
  }
  try:
      response = requests.get(f"https://{host}/json/version", timeout=10, proxies=proxies)
      print(f"/json/version endpoint test: {response.status_code}")
      if response.status_code == 200:
          version_data = response.json()
          print(f"Chrome version: {version_data.get('Browser', 'unknown')}")
          print(f"WebSocket URL: {version_data.get('webSocketDebuggerUrl', 'not found')}")
          return version_data.get('webSocketDebuggerUrl', 'not found')
      else:
          print(f"Response content: {response.text[:200]}...")
          return None
  except Exception as e:
      print(f"/json/version endpoint failed: {e}")
      return None

async def screenshot(playwright_page: Page, session_id: str, url: str):
  print("taking screenshot...")
  screenshot_bytes = await playwright_page.screenshot(full_page=True, type='png')
  # Write screenshot_bytes to a PNG file in ./screenshots/{session_id}
  screenshots_dir = os.path.join(".", "screenshots", str(session_id))
  os.makedirs(screenshots_dir, exist_ok=True)
  # Extract the host (domain) part from the URL and escape it for safe filename usage

  parsed_url = urlparse(url)
  host = parsed_url.netloc or parsed_url.path  # fallback if netloc is empty
  # Escape host: replace any non-alphanumeric, non-dot, non-hyphen with underscore
  safe_host = re.sub(r'[^a-zA-Z0-9.-]', '_', host)
  screenshot_path = os.path.join(screenshots_dir, f"{safe_host}_{time.time()}.png")
  with open(screenshot_path, "wb") as f:
    f.write(screenshot_bytes)
  print(f"Screenshot saved to {screenshot_path}")

async def setp_end_hook(agent: Agent):
  page = await agent.browser_session.get_current_page()
  current_url = page.url
  visit_log = agent.history.urls()
  previous_url = visit_log[-2] if len(visit_log) >= 2 else None
  print(f"Agent was last on URL: {previous_url} and is now on {current_url}")
  await screenshot(page, agent.browser_session.id, current_url)

async def main():
  print(os.getenv("E2B_API_KEY"))
  print(os.getenv("E2B_DOMAIN"))
  sandbox = Sandbox(
    timeout=600,  # seconds
    template="browser-chromium",
  )
  
  try:
    # Get host and construct complete URL
    host = sandbox.get_host(9223)
    cdp_url = f"https://{host}"
    print(f"CDP URL: {cdp_url}")
    
    # Debug connection
    await test_chrome_connection(host)
    
    # Set log level for browser_use related
    logging.getLogger('browser_use').setLevel(logging.DEBUG)  # Optional: INFO, WARNING, ERROR
    
    browser_session = BrowserSession(
      cdp_url=cdp_url,
    )
    await browser_session.start()

    agent = Agent(
      task="Go to google and search for browser-use information and summarize the results",
      llm=ChatOpenAI(
        api_key=LLM_API_KEY,
        base_url=LLM_BASE_URL,
        model=LLM_MODEL,
        temperature=1.0
      ),
      browser_session=browser_session,
    )
    
    # Optional: further customize the log level for this agent instance
    agent.logger.setLevel(logging.DEBUG)

    await agent.run(
      on_step_start=setp_end_hook,
      on_step_end=setp_end_hook
    )
    await browser_session.close()
  finally:
    # Destroy sandbox
    sandbox.kill()

asyncio.run(main())