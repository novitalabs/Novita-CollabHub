import asyncio
import os
import json
from novita_sandbox.agent_runtime import AgentRuntimeClient as NovitaAgentRuntimeClient
from dotenv import load_dotenv
load_dotenv()

client = NovitaAgentRuntimeClient(
    api_key=os.getenv("NOVITA_API_KEY")
)

async def main():
    """Google ADK Agent Tests"""
    
    # Test cases
    test_cases = [
        {"name": "Simple Query", "prompt": "What is an AI Agent?"},
        {"name": "Google Search", "prompt": "Search for Google Gemini 3.0 latest features"}
    ]
    
    print("\n" + "="*80)
    print("🚀 Google ADK Agent Tests")
    print("="*80 + "\n")
    
    for i, test in enumerate(test_cases, 1):
        try:
            print("="*80)
            print(f"Test {i}: {test['name']}")
            print("="*80)
            print(f"📤 {test['prompt']}")
            
            payload = json.dumps({"prompt": test['prompt']}).encode()
            
            response = await client.invoke_agent_runtime(
                agentId=os.getenv("NOVITA_AGENT_ID"),
                payload=payload,
                timeout=300,
                envVars={"GEMINI_API_KEY": os.getenv("GEMINI_API_KEY")},
            )
            
            print(f"📥 Response:")
            if isinstance(response, dict):
                result = response.get('result', response.get('error', response))
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