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
  """Test multi-turn conversation"""
  # Create unique runtimeSessionId
  runtime_session_id = str(uuid.uuid4())
  
  print("\n" + "="*80)
  print("🚀 AutoGen Agent Multi-turn Conversation Test")
  print("="*80)
  print(f"🔑 Session ID: {runtime_session_id}")
  print("="*80 + "\n")
  
  # Define two conversation rounds
  conversation_rounds = [
    {"round": "Round 1", "prompt": "How's the weather in New York?"},
    {"round": "Round 2: Testing Memory", "prompt": "Which city's weather did I just ask about?"}
  ]
  
  try:
    responses = []
    
    for turn in conversation_rounds:
      print("="*80)
      print(f"{turn['round']}")
      print("="*80)
      print(f"📤 {turn['prompt']}")
      
      payload = json.dumps({"prompt": turn['prompt'], "streaming": False}).encode()
      
      response = await client.invoke_agent_runtime(
        agentId=os.getenv("NOVITA_AGENT_ID"),
        payload=payload,
        timeout=300,
        envVars={"OPENAI_API_KEY": os.getenv("NOVITA_API_KEY")},
        runtimeSessionId=runtime_session_id  # Use the same sessionId
      )
      
      print(f"📥 Response:")
      if isinstance(response, dict):
        result = response.get('result', response)
        print(result)
        responses.append(result)
      else:
        print(response)
        responses.append(str(response))
      print("")
      
      # Pause between rounds
      await asyncio.sleep(1)
    
    # Check memory capability
    if len(responses) >= 2 and "New York" in str(responses[1]):
      print("="*80)
      print("✅ Success! Agent remembered the previous conversation content!")
      print("="*80 + "\n")
    else:
      print("="*80)
      print("⚠️  Warning: Agent may not have remembered the previous conversation")
      print("="*80 + "\n")
    
    print("="*80)
    print("✅ Multi-turn conversation test completed")
    print("="*80 + "\n")
    
  except Exception as e:
    print("\n" + "="*80)
    print("❌ Test failed")
    print("="*80)
    print(f"Error type: {type(e).__name__}")
    print(f"Error message: {str(e)}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    print("="*80 + "\n")

if __name__ == "__main__":
  asyncio.run(main())
