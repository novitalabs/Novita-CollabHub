from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.tools import google_search
from google.genai import types
from dotenv import load_dotenv
load_dotenv()
import os

APP_NAME = "google_search_agent"
USER_ID = "user1234"

# Agent Definition
root_agent = LlmAgent(
    model=os.getenv("GEMINI_MODEL", "gemini-2.5-flash"), 
    name=APP_NAME,
    instruction="I can answer your questions by searching the internet. Just ask me anything!",
    tools=[google_search]
)

# Session and Runner
session_service = InMemorySessionService()
runner = Runner(
    agent=root_agent, 
    app_name=APP_NAME, 
    session_service=session_service
)

# Agent Interaction
async def call_agent_async(query, user_id, session_id):
    """Call the agent with the given query"""
    try:
        # Get or create session
        try:
            session = await session_service.get_session(
                app_name=APP_NAME,
                user_id=user_id,
                session_id=session_id
            )
        except:
            session = await session_service.create_session(
                app_name=APP_NAME, 
                user_id=user_id, 
                session_id=session_id
            )
        
        # Create message
        user_content = types.Content(role='user', parts=[types.Part(text=query)])
        
        # Run agent
        final_response_content = "No response received."
        async for event in runner.run_async(
            user_id=user_id, 
            session_id=session_id, 
            new_message=user_content
        ):
            if event.is_final_response() and event.content and event.content.parts:
                final_response_content = event.content.parts[0].text
        
        return final_response_content
        
    except Exception as e:
        # Fallback to direct Gemini API call
        if "Session not found" in str(e) or "app name" in str(e).lower():
            try:
                from google.genai import Client
                
                gemini_client = Client(api_key=os.getenv("GEMINI_API_KEY"))
                response = gemini_client.models.generate_content(
                    model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash"),
                    contents=query
                )
                return response.text
            except:
                pass
        
        return f"Error: {str(e)}"


from novita_sandbox.agent_runtime import AgentRuntimeApp
import asyncio
import uuid

app = AgentRuntimeApp()

@app.entrypoint
def agent_invocation(payload, context):
    """Novita Agent Runtime entrypoint"""
    prompt = payload.get("prompt", "Tell me something about AI Agent?")
    user_id = payload.get("user_id", USER_ID)
    session_id = getattr(context, 'session_id', None) or str(uuid.uuid4())
    
    result = asyncio.run(call_agent_async(prompt, user_id, session_id))
    return result

@app.ping
def health_check() -> dict:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "Google ADK Agent",
        "features": ["google_search"]
    }

if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 Google ADK Agent Runtime")
    print("="*80)
    print(f"🤖 Model: {os.getenv('GEMINI_MODEL', 'gemini-2.0-flash')}")
    print(f"🛠️  Tools: Google Search")
    print(f"🔗 Port: 8080")
    print("="*80 + "\n")
    app.run(port=8080)