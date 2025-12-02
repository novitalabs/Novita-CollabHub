import asyncio
import os
import json
import uuid
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
  # Create unique runtimeSessionId
  runtime_session_id = str(uuid.uuid4())
  
  print("\n" + "="*80)
  print("🔑 Generating Session ID")
  print("="*80)
  print(f"Runtime Session ID: {runtime_session_id}")
  print("="*80 + "\n")
  
  # Define multi-turn conversation content
  conversation_rounds = [
    "Hello, agent! My name is Jason.",
    "Tell me something about AI Agents.",
    "What's my name? Can you remember it?"
  ]
  
  try:
    for round_num, prompt in enumerate(conversation_rounds, 1):
      print("\n" + "="*80)
      print(f"🚀 Round {round_num}")
      print("="*80)
      
      payload = json.dumps({"prompt": prompt}).encode()
      print(f"📤 Sending Payload: {payload.decode()}")
      print(f"🎯 Agent ID: {os.getenv('NOVITA_AGENT_ID')}")
      print(f"🔑 Session ID: {runtime_session_id}")
      
      response = await client.invoke_agent_runtime(
        agentId=os.getenv("NOVITA_AGENT_ID"),
        payload=payload,
        timeout=300,
        envVars={"NOVITA_API_KEY": os.getenv("NOVITA_API_KEY")},
        runtimeSessionId=runtime_session_id  # Use the same sessionId
      )
      
      print("\n" + "-"*80)
      print(f"✅ Round {round_num} Response")
      print("-"*80)
      print(f"Response type: {type(response)}")
      print(f"Response: {response}")
      print("-"*80)
      
      # Pause before next round
      if round_num < len(conversation_rounds):
        print("\n⏳ Waiting 2 seconds before next round...")
        await asyncio.sleep(2)
    
    print("\n" + "="*80)
    print("✅ All conversation rounds completed")
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

