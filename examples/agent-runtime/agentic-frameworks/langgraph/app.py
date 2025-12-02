
from typing import Annotated

from langchain_openai import ChatOpenAI
from typing_extensions import TypedDict

from langgraph.graph import StateGraph, START
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode, tools_condition

import logging
from logging.handlers import RotatingFileHandler
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
log_formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Create log directory if it doesn't exist
log_dir = "./app_logs"
if not os.path.exists(log_dir):
    os.makedirs(log_dir)

# File handler - uses RotatingFileHandler for automatic log rotation
file_handler = RotatingFileHandler(
    os.path.join(log_dir, "app.log"),
    maxBytes=10*1024*1024,  # 10MB
    backupCount=5,
    encoding='utf-8'
)
file_handler.setFormatter(log_formatter)
file_handler.setLevel(logging.DEBUG)

# Console handler
console_handler = logging.StreamHandler()
console_handler.setFormatter(log_formatter)
console_handler.setLevel(logging.INFO)

# Configure root logger
root_logger = logging.getLogger()
root_logger.setLevel(logging.DEBUG)
root_logger.addHandler(file_handler)
root_logger.addHandler(console_handler)

# Configure langchain logger
langchain_logger = logging.getLogger("langchain")
langchain_logger.setLevel(logging.DEBUG)

# Create application logger
logger = logging.getLogger(__name__)

print("\n" + "="*80, flush=True)
print("🚀 APPLICATION STARTING UP", flush=True)
print("="*80, flush=True)

logger.info("="*80)
logger.info("🚀 APPLICATION STARTING UP")
logger.info("="*80)

os.environ["LANGSMITH_OTEL_ENABLED"] = "false"

api_key = os.getenv('NOVITA_API_KEY', 'NOT_SET')
api_key_masked = api_key[:8] + "***" if len(api_key) > 8 else "***"
print(f"🔑 NOVITA_API_KEY: {api_key_masked}", flush=True)
logger.info(f"NOVITA_API_KEY (masked): {api_key_masked}")

print("🤖 Preparing LLM configuration...", flush=True)
logger.info("Preparing LLM configuration")

# LLM base configuration (streaming is not set here, decided dynamically at runtime)
llm_config = {
    "model": "deepseek/deepseek-v3-0324",
    "base_url": "https://api.novita.ai/v3/openai/",
    "api_key": api_key,
}

print("✅ LLM configuration ready", flush=True)
logger.info("LLM configuration ready")

## Define search tool
print("🔧 Setting up tools...", flush=True)
logger.info("Setting up DuckDuckGo search tool")

from langchain_community.tools import DuckDuckGoSearchRun
search = DuckDuckGoSearchRun()
tools = [search]

print("✅ Tools configured", flush=True)
logger.info("Tools configured successfully")

print("📊 Defining state...", flush=True)
logger.info("Defining state...")

## Define state
class State(TypedDict):
    messages: Annotated[list, add_messages]

# Note: We don't pre-compile the graph, but create it at runtime based on the streaming parameter
print("✅ State and tools ready", flush=True)
logger.info("State and tools ready")

print("🌐 Initializing Novita AgentRuntimeApp...", flush=True)
logger.info("Initializing Novita AgentRuntimeApp")

from novita_sandbox.agent_runtime import AgentRuntimeApp as NovitaAgentRuntimeApp, RequestContext
app = NovitaAgentRuntimeApp(debug=True)

print("✅ AgentRuntimeApp initialized", flush=True)
logger.info("AgentRuntimeApp initialized successfully")

# Initialize global conversation history - persists throughout sandbox lifecycle
# All requests to the same sandbox instance share this history
conversation_history = []
logger.info("Initialized conversation history (sandbox-scoped)")

print("="*80, flush=True)
print("✅ APPLICATION READY - Waiting for requests", flush=True)
print("="*80 + "\n", flush=True)
logger.info("Application ready - waiting for requests")

def _handle_streaming(graph, tmp_msg):
    """
    Handle streaming requests - independent generator function.
    
    Streams LLM response chunks in real-time and accumulates the complete
    response to save in conversation history.
    """
    logger.info("Using streaming mode")
    
    try:
        chunk_count = 0
        accumulated_content = ""  # Accumulate complete response
        
        # Use stream_mode="messages" to get LLM tokens
        # Reference: https://docs.langchain.com/oss/python/langgraph/streaming
        logger.debug("Starting graph.stream() iteration...")
        
        for chunk, metadata in graph.stream(tmp_msg, stream_mode="messages"):
            chunk_count += 1
            logger.debug(f"Received chunk #{chunk_count}, type: {type(chunk)}, metadata: {metadata}")
            
            # chunk is the message block returned by LLM
            if hasattr(chunk, 'content') and chunk.content:
                content = chunk.content
                accumulated_content += content  # Accumulate content
                logger.debug(f"Streaming chunk content: {content[:100]}...")
                # Yield directly, SDK will automatically handle SSE format
                yield {"chunk": content, "type": "content"}
            else:
                logger.debug(f"Chunk has no content or empty content, chunk: {chunk}")
        
        # Add complete AI response to global history
        if accumulated_content:
            conversation_history.append({"role": "assistant", "content": accumulated_content})
            logger.info(f"Added assistant message to history. Total messages: {len(conversation_history)}")
        
        # Streaming end marker
        logger.info(f"Streaming completed, total chunks: {chunk_count}")
        yield {"chunk": "", "type": "end"}
        
    except Exception as e:
        logger.error(f"Error during streaming: {str(e)}", exc_info=True)
        yield {"error": str(e), "type": "error"}


def _handle_non_streaming(graph, tmp_msg):
    """
    Handle non-streaming requests - regular function that returns a dict.
    
    Invokes the graph, extracts the response, and saves it to conversation history.
    """
    logger.info("Using non-streaming mode")
    
    try:
        logger.info("About to call graph.invoke()")
        tmp_output = graph.invoke(tmp_msg)
        
        logger.info("graph.invoke() completed successfully")
        logger.debug(f"Graph output: {tmp_output}")

        # Get the last message
        last_message = tmp_output['messages'][-1]
        logger.info(f"Last message type: {type(last_message)}")
        logger.info(f"Last message has 'content': {hasattr(last_message, 'content')}")
        
        # Check if message has content
        if hasattr(last_message, 'content') and last_message.content:
            result_content = last_message.content
            logger.info("Successfully extracted content from last message")
        else:
            # If no content, try to get information from tool call results
            # or return a default message
            result_content = "I've completed the search and gathered information. The search was successful."
            logger.warning("No content in last message, using default response")
        
        # Add AI response to global history
        conversation_history.append({"role": "assistant", "content": result_content})
        logger.info(f"Added assistant message to history. Total messages: {len(conversation_history)}")
        
        logger.info(f"Returning result (length: {len(result_content)} chars)")
        logger.debug(f"Result preview: {result_content[:200]}...")
        
        response = {"result": result_content}
        logger.info("Returning response")
        
        return response
        
    except Exception as graph_error:
        logger.error(f"Error during graph.invoke(): {str(graph_error)}", exc_info=True)
        
        error_response = {
            "error": f"Graph invocation failed: {str(graph_error)}",
            "error_type": type(graph_error).__name__
        }
        return error_response


@app.entrypoint
def agent_invocation(request: dict, context: RequestContext):
    logger.info("="*80)
    logger.info("🚀 AGENT INVOCATION STARTED")
    logger.info("="*80)
    logger.info(f"Request type: {type(request)}")
    logger.info(f"Request keys: {list(request.keys())}")
    logger.info(f"Request details: {request}")
    
    try:
        # Get prompt and streaming parameters from request
        prompt = request.get("prompt", "No prompt found in input, please guide customer as to what tools can be used")
        streaming = request.get("streaming", False)
        
        # Detailed debug information
        logger.info(f"Raw 'streaming' value from request.get('streaming'): {request.get('streaming')}")
        logger.info(f"Raw 'streaming' type: {type(request.get('streaming'))}")
        logger.info(f"After default False, streaming value: {streaming}")
        
        logger.info(f"Processing prompt: {prompt}")
        logger.info(f"Streaming mode: {streaming}, type: {type(streaming)}")
        
        # Add new user message to global history
        conversation_history.append({"role": "user", "content": prompt})
        logger.info(f"Added user message to history. Total messages: {len(conversation_history)}")
        
        # Use complete conversation history (including new user message)
        tmp_msg = {"messages": list(conversation_history)}
        logger.info(f"Using conversation history with {len(conversation_history)} messages")
        logger.debug(f"Message structure: {tmp_msg}")
        
        # Create LLM and graph based on streaming parameter
        logger.info(f"Creating LLM with streaming={streaming}")
        
        llm = ChatOpenAI(
            **llm_config,
            streaming=streaming  # Set dynamically based on request
        )
        llm_with_tools = llm.bind_tools(tools)
        
        # Build graph
        graph_builder = StateGraph(State)
        
        def chatbot(state: State):
            return {"messages": [llm_with_tools.invoke(state["messages"])]}
        
        graph_builder.add_node("chatbot", chatbot)
        tool_node = ToolNode(tools=tools)
        graph_builder.add_node("tools", tool_node)
        graph_builder.add_conditional_edges("chatbot", tools_condition)
        graph_builder.add_edge("tools", "chatbot")
        graph_builder.add_edge(START, "chatbot")
        
        graph = graph_builder.compile()
        
        logger.info("Graph created successfully")
    
        # Choose handler function based on streaming parameter
        if streaming:
            # Return generator - will be recognized as streaming response by AgentRuntimeApp
            return _handle_streaming(graph, tmp_msg)
        else:
            # Return dict - will be recognized as regular response by AgentRuntimeApp
            return _handle_non_streaming(graph, tmp_msg)
    
    except Exception as outer_error:
        # Top-level exception handling
        logger.error(f"Unhandled error in agent_invocation: {str(outer_error)}", exc_info=True)
        
        error_response = {
            "error": f"Agent error: {str(outer_error)}",
            "error_type": type(outer_error).__name__
        }
        
        return error_response

@app.ping
def health_check() -> dict:
    logger.debug("Health check endpoint called")
    return {"status": "healthy", "service": "My Agent"}

if __name__ == "__main__":
    app.run(port=8080)
