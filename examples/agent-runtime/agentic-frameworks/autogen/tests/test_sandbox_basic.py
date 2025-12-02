import asyncio
import os
import json
from novita_sandbox.agent_runtime import AgentRuntimeClient as NovitaAgentRuntimeClient
from dotenv import load_dotenv
load_dotenv()

print(os.getenv("NOVITA_API_KEY"))
print(os.getenv("NOVITA_DOMAIN"))
print(os.getenv("NOVITA_AGENT_ID"))

client = NovitaAgentRuntimeClient(
  api_key=os.getenv("NOVITA_API_KEY")
)

async def main():
  """Test three core tools: weather query, information search, calculation"""
  
  # Define three test cases
  test_cases = [
    {"name": "Weather Query Tool (get_weather)", "prompt": "Query the weather in New York"},
    {"name": "Information Search Tool (search_information)", "prompt": "Search for AI-related information"},
    {"name": "Calculate Tool (calculate)", "prompt": "Calculate 123 + 456"}
  ]
  
  print("\n" + "="*80)
  print("🚀 AutoGen Agent Functionality Test")
  print("="*80 + "\n")
  
  for i, test in enumerate(test_cases, 1):
    try:
      print("="*80)
      print(f"Test {i}: {test['name']}")
      print("="*80)
      print(f"📤 {test['prompt']}")
      
      payload = json.dumps({"prompt": test['prompt'], "streaming": False}).encode()
      
      response = await client.invoke_agent_runtime(
        agentId=os.getenv("NOVITA_AGENT_ID"),
        payload=payload,
        timeout=300,
        envVars={"OPENAI_API_KEY": os.getenv("NOVITA_API_KEY")},
      )
      
      print(f"📥 Response:")
      if isinstance(response, dict):
        result = response.get('result', response)
        print(result)
      else:
        print(response)
      print("")
      
    except Exception as e:
      print(f"❌ Test failed: {str(e)}")
      import traceback
      traceback.print_exc()
      print("")
  
  print("="*80)
  print("✅ All tests completed")
  print("="*80 + "\n")

if __name__ == "__main__":
  asyncio.run(main())
