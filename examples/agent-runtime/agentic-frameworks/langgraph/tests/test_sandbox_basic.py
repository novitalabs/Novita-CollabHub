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
  try:
    print("\n" + "="*80)
    print("🚀 Starting Agent Invocation")
    print("="*80)
    
    payload = json.dumps({"prompt": "Hello, Agent! Tell me something about AI Agents."}).encode()
    print(f"📤 Sending Payload: {payload.decode()}")
    print(f"🎯 Agent ID: {os.getenv('NOVITA_AGENT_ID')}")
    
    response = await client.invoke_agent_runtime(
      agentId=os.getenv("NOVITA_AGENT_ID"),
      payload=payload,
      timeout=300,
      envVars={"NOVITA_API_KEY": os.getenv("NOVITA_API_KEY")},
    )
    
    print("\n" + "="*80)
    print("✅ Response Received")
    print("="*80)
    print(f"Response type: {type(response)}")
    print(f"Response: {response}")
    print("="*80 + "\n")
    
  except Exception as e:
    print("\n" + "="*80)
    print("❌ Invocation Failed")
    print("="*80)
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    print("="*80 + "\n")

if __name__ == "__main__":
  asyncio.run(main())