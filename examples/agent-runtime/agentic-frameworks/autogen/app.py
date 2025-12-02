"""
Microsoft AutoGen Agent Example Project

This example demonstrates how to use Microsoft AutoGen to build multi-agent conversation systems,
and integrate them into Novita Agent Runtime.

Features:
- Uses AutoGen to build conversational Agents
- Supports tool calling and reflection
- Full integration with Novita Agent Runtime
"""

import logging
import os

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import Novita Agent Runtime
from novita_sandbox.agent_runtime import AgentRuntimeApp, RequestContext

app = AgentRuntimeApp()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("autogen_agent")

# Initialize global conversation history - persists throughout sandbox lifecycle
# All requests to the same sandbox instance share this history
conversation_history = []

# Check if AutoGen is available
try:
    from autogen_agentchat.agents import AssistantAgent
    from autogen_agentchat.ui import Console
    from autogen_agentchat.messages import TextMessage
    from autogen_ext.models.openai import OpenAIChatCompletionClient
    from autogen_core.models import ModelFamily, ModelInfo
    from autogen_core import CancellationToken
    AUTOGEN_AVAILABLE = True
    logger.info("AutoGen imported successfully")
except ImportError as e:
    AUTOGEN_AVAILABLE = False
    logger.error(f"AutoGen import failed: {e}", exc_info=True)
    logger.warning("AutoGen not installed or import failed, running in simulation mode")


# Define tool functions
async def get_weather(city: str) -> str:
    """
    Get weather for a specified city
    
    Args:
        city: City name
        
    Returns:
        Weather information string
    """
    weather_data = {
        "New York": "Sunny, 15°C, good air quality",
        "London": "Cloudy, 12°C, 60% humidity",
        "Paris": "Light rain, 18°C, bring an umbrella",
        "Tokyo": "Sunny, 20°C, pleasant weather",
    }
    return weather_data.get(city, f"{city}: Sunny, 23°C")


async def search_information(query: str) -> str:
    """
    Search for information
    
    Args:
        query: Search query
        
    Returns:
        Search results
    """
    return f"Search results for '{query}': This is a sample search result. In production, you can integrate with a real search API."


async def calculate(expression: str) -> str:
    """
    Calculate a mathematical expression
    
    Args:
        expression: Mathematical expression
        
    Returns:
        Calculation result
    """
    try:
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Calculation result: {expression} = {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"


def _create_agent(streaming=False):
    """
    Create AutoGen Agent (reusable configuration)
    
    Args:
        streaming: Whether to enable streaming output (token level)
    """
    model_client = OpenAIChatCompletionClient(
        base_url=os.getenv("OPENAI_BASE_URL", "https://api.novita.ai/v3/openai"),
        model=os.getenv("MODEL_NAME", "deepseek/deepseek-v3.1-terminus"),
        api_key=os.getenv("OPENAI_API_KEY"),
        model_info=ModelInfo(
            vision=False,
            function_calling=True,
            json_output=True,
            family=ModelFamily.UNKNOWN,
            structured_output=True,
        ),
        # Enable token-level streaming output
        stream_options={"include_usage": True} if streaming else None,
    )
    
    agent = AssistantAgent(
        name="assistant",
        model_client=model_client,
        tools=[get_weather, search_information, calculate],
        system_message="""You are a helpful AI assistant that can:
        1. Query weather information
        2. Search for relevant information
        3. Perform mathematical calculations
        
        Please select the appropriate tool based on user requests.""",
        reflect_on_tool_use=True,
    )
    
    return agent


async def _handle_streaming():
    """
    Handle streaming requests - generator function
    
    Streams LLM response chunks in real-time and accumulates complete response
    to save in conversation history
    """
    if not AUTOGEN_AVAILABLE:
        yield {"chunk": "(Simulated response) AutoGen not installed", "type": "content"}
        yield {"chunk": "", "type": "end"}
        return
    
    try:
        agent = _create_agent(streaming=True)
        accumulated_content = ""
        
        # Convert conversation history to AutoGen message format
        messages = []
        for msg in conversation_history:
            messages.append(TextMessage(content=msg["content"], source=msg["role"]))
        
        # Create CancellationToken
        cancellation_token = CancellationToken()
        
        # Run Agent with streaming output
        async for message in agent.on_messages_stream(messages, cancellation_token):
            # Extract message content
            content = None
            
            # Handle Response type (contains chat_message)
            if hasattr(message, 'chat_message') and hasattr(message.chat_message, 'content'):
                content = message.chat_message.content
            # Handle events with direct content (e.g., ThoughtEvent)
            elif hasattr(message, 'content'):
                content = message.content
            
            # Output valid content
            if content and isinstance(content, str) and content.strip():
                accumulated_content += content
                yield {"chunk": content, "type": "content"}
        
        # Save to conversation history
        if accumulated_content:
            conversation_history.append({"role": "assistant", "content": accumulated_content})
        
        yield {"chunk": "", "type": "end"}
        
    except Exception as e:
        logger.error(f"Streaming processing error: {str(e)}", exc_info=True)
        yield {"error": str(e), "type": "error"}


async def _handle_non_streaming():
    """
    Handle non-streaming requests - returns complete response dict
    
    Invokes Agent, extracts response, and saves to conversation history
    """
    if not AUTOGEN_AVAILABLE:
        return {"result": "(Simulated response) AutoGen not installed, please install for full functionality."}
    
    try:
        agent = _create_agent()
        
        # Convert conversation history to AutoGen message format
        messages = []
        for msg in conversation_history:
            messages.append(TextMessage(content=msg["content"], source=msg["role"]))
        
        # Create CancellationToken
        cancellation_token = CancellationToken()
        # Run Agent
        response_message = await agent.on_messages(messages, cancellation_token)
        
        # Extract response content
        if response_message and hasattr(response_message, 'chat_message'):
            chat_msg = response_message.chat_message
            response = chat_msg.content if hasattr(chat_msg, 'content') else str(chat_msg)
        else:
            response = str(response_message) if response_message else "No response generated"
        
        # Save to conversation history
        conversation_history.append({"role": "assistant", "content": response})
        
        return {"result": response}
        
    except Exception as e:
        logger.error(f"Agent execution error: {str(e)}", exc_info=True)
        return {
            "error": f"Agent execution failed: {str(e)}",
            "error_type": type(e).__name__
        }


# Define Novita Agent Runtime entrypoint (supports async)
@app.entrypoint
async def agent_invocation(request: dict, context: RequestContext):
    """
    AutoGen Agent entrypoint (supports streaming and multi-turn conversation)
    
    Args:
        request: Request data containing the following fields:
            - prompt: User input query
            - streaming: Whether to use streaming output (optional, default False)
        context: Request context
            
    Returns:
        Response data dict (non-streaming) or generator (streaming)
    """
    try:
        # Get request parameters
        prompt = request.get("prompt", "Hello!")
        streaming = request.get("streaming", False)
        
        # Add new user message to global history
        conversation_history.append({"role": "user", "content": prompt})
        
        # Select handler function based on streaming parameter
        if streaming:
            return _handle_streaming()
        else:
            return await _handle_non_streaming()
    
    except Exception as e:
        logger.error(f"Agent error: {str(e)}", exc_info=True)
        return {
            "error": f"Agent error: {str(e)}",
            "error_type": type(e).__name__
        }


@app.ping
def health_check() -> dict:
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "AutoGen Agent",
        "features": ["weather", "search", "calculate", "streaming", "multi-turn"]
    }


if __name__ == "__main__":
    print("\n" + "="*80)
    print("🚀 Starting Microsoft AutoGen Agent Runtime")
    print("="*80)
    print("🛠️  Available tools: get_weather, search_information, calculate")
    print("💬 Supported features: streaming output, multi-turn conversation")
    print("🔗 Listening on port: 8080")
    print("="*80 + "\n")
    app.run(port=8080)
