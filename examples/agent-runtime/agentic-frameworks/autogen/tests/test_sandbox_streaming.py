import asyncio
import os
import json
import time
import sys
from novita_sandbox.agent_runtime import AgentRuntimeClient as NovitaAgentRuntimeClient
from dotenv import load_dotenv
load_dotenv()

# Force disable stdout buffering to ensure real-time output
sys.stdout.reconfigure(line_buffering=True)

# Debug mode: Display detailed information and timestamps for each chunk
DEBUG_MODE = False

print(os.getenv("NOVITA_API_KEY"))
print(os.getenv("NOVITA_DOMAIN"))
print(os.getenv("NOVITA_AGENT_ID"))

client = NovitaAgentRuntimeClient(
  api_key=os.getenv("NOVITA_API_KEY")
)

async def main():
  """Test streaming output"""
  try:
    print("\n" + "="*80)
    print("🚀 AutoGen Agent Streaming Output Test")
    print("="*80)
    
    # Streaming test case
    request_dict = {"prompt": "Query the weather in New York and calculate 25 + 15", "streaming": True}
    payload = json.dumps(request_dict).encode()
    print(f"📤 {request_dict['prompt']}")
    print(f"🎯 Agent ID: {os.getenv('NOVITA_AGENT_ID')}")
    
    print("\n⏱️  Calling Agent...")
    invoke_start_time = time.time()
    
    response = await client.invoke_agent_runtime(
      agentId=os.getenv("NOVITA_AGENT_ID"),
      payload=payload,
      timeout=300,
      envVars={"OPENAI_API_KEY": os.getenv("NOVITA_API_KEY")},
    )
    
    first_response_time = time.time() - invoke_start_time
    print(f"✅ Response object received, time elapsed: {first_response_time:.3f}s")
    
    print("\n" + "="*80)
    print("📡 Streaming response:")
    print("="*80 + "\n")
    
    # Handle streaming response
    if hasattr(response, '__aiter__'):
      print("-" * 80)
      chunk_count = 0
      content_count = 0
      
      start_time = time.time()
      last_chunk_time = start_time
      
      print(f"⏱️  Starting to iterate response stream, current timestamp: {time.time():.3f}")
      iteration_start = time.time()
      
      async for chunk in response:
        chunk_count += 1
        current_time = time.time()
        time_since_start = current_time - start_time
        time_since_last = current_time - last_chunk_time
        last_chunk_time = current_time
        
        # Special log for first chunk arrival
        if chunk_count == 1:
          time_to_first_chunk = current_time - iteration_start
          if DEBUG_MODE:
            sys.stdout.write(f"\n🎉 First chunk arrived! Time elapsed: {time_to_first_chunk:.3f}s\n")
            sys.stdout.write(f"   Total call time: {current_time - invoke_start_time:.3f}s\n\n")
            sys.stdout.flush()
        
        if DEBUG_MODE:
          # Use sys.stdout.write and immediate flush to ensure real-time output
          debug_msg = f"\n[Chunk #{chunk_count}] +{time_since_last:.3f}s | Type: {type(chunk).__name__}\n"
          sys.stdout.write(debug_msg)
          sys.stdout.flush()
        
        # Helper function to parse chunk
        def parse_and_print(data):
          nonlocal content_count
          if isinstance(data, dict):
            if data.get('type') == 'content':
              content = data.get('chunk', '')
              if content:
                content_count += 1
                # Use sys.stdout.write instead of print to ensure real-time output
                sys.stdout.write(content)
                sys.stdout.flush()
                
                if DEBUG_MODE:
                  sys.stdout.write(f" [{len(content)} chars]")
                  sys.stdout.flush()
            elif data.get('type') == 'end':
              sys.stdout.write(f"\n{'-' * 80}\n")
              sys.stdout.write(f"✅ Streaming output completed\n")
              if DEBUG_MODE:
                sys.stdout.write(f"   Total chunks: {chunk_count}\n")
                sys.stdout.write(f"   Content chunks: {content_count}\n")
                sys.stdout.write(f"   Total time: {time_since_start:.2f}s\n")
              sys.stdout.flush()
            elif data.get('type') == 'error':
              sys.stdout.write(f"\n❌ Error: {data.get('error')}\n")
              sys.stdout.flush()
          else:
            sys.stdout.write(str(data))
            sys.stdout.flush()
        
        # Handle different chunk formats
        if isinstance(chunk, str):
          # String format: might be JSON string
          try:
            data = json.loads(chunk)
            parse_and_print(data)
          except json.JSONDecodeError:
            # Not JSON, output directly
            sys.stdout.write(chunk)
            sys.stdout.flush()
        
        elif isinstance(chunk, dict):
          # Dict format: might be data directly, or contain nested 'chunk' key
          if 'chunk' in chunk and isinstance(chunk['chunk'], str):
            # SDK wrapper format: {'chunk': '...', ...}
            try:
              inner_data = json.loads(chunk['chunk'])
              parse_and_print(inner_data)
            except (json.JSONDecodeError, TypeError):
              # Not JSON, output directly
              sys.stdout.write(chunk['chunk'])
              sys.stdout.flush()
          else:
            # Direct data format
            parse_and_print(chunk)
        
        else:
          # Other types, output directly
          sys.stdout.write(str(chunk))
          sys.stdout.flush()
      
      if chunk_count == 0:
        print("⚠️ No data received")
        
    elif isinstance(response, dict):
      # If it's a regular response (non-streaming)
      print("\n💬 Agent response (non-streaming):")
      print(json.dumps(response, indent=2, ensure_ascii=False))
    else:
      # Other types
      print("\n💬 Agent response (unknown format):")
      print(response)
    
    print("\n" + "="*80)
    print("✅ Streaming test completed")
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
