"""
OpenAI Agents SDK Example Project

This example demonstrates how to use OpenAI Agents SDK to build simple and efficient Agents,
and integrate them into Novita Agent Runtime.

Features:
- Uses the official OpenAI Agent framework
- Supports function calling
- Full integration with Novita Agent Runtime
"""

import asyncio
import logging
import os
from typing import Dict, Any

# Load environment variables
from dotenv import load_dotenv

# Import Novita Agent Runtime
from novita_sandbox.agent_runtime import AgentRuntimeApp

# Load .env file
load_dotenv()

app = AgentRuntimeApp()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("openai_agents")

# Note: Since OpenAI Agents SDK is still in early development, we use a simplified version here
# For production use, please refer to the official OpenAI documentation

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False
    logger.warning("OpenAI SDK not installed, running in simulation mode")


# Define tool functions
def get_current_time(timezone: str = "UTC") -> str:
    """
    Get current time
    
    Args:
        timezone: Timezone (not implemented, returns UTC time)
        
    Returns:
        Current time string
    """
    from datetime import datetime
    now = datetime.utcnow()
    return f"Current time (UTC): {now.strftime('%Y-%m-%d %H:%M:%S')}"


def calculate(expression: str) -> str:
    """
    Calculate a mathematical expression
    
    Args:
        expression: Mathematical expression, e.g., "2 + 3 * 4"
        
    Returns:
        Calculation result
    """
    try:
        # Safely evaluate the expression
        result = eval(expression, {"__builtins__": {}}, {})
        return f"Calculation result: {expression} = {result}"
    except Exception as e:
        return f"Calculation error: {str(e)}"


def get_weather(city: str) -> str:
    """
    Get city weather (simulated)
    
    Args:
        city: City name
        
    Returns:
        Weather information
    """
    weather_data = {
        "New York": "Sunny, 15°C, good air quality",
        "London": "Cloudy, 12°C, 60% humidity",
        "Paris": "Light rain, 18°C, bring an umbrella",
        "Tokyo": "Sunny, 20°C, pleasant weather",
    }
    return weather_data.get(city, f"{city}: Sunny, 23°C")


# Tool definitions (OpenAI Function Calling format)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_current_time",
            "description": "Get current time",
            "parameters": {
                "type": "object",
                "properties": {
                    "timezone": {
                        "type": "string",
                        "description": "Timezone, e.g., 'UTC'"
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "calculate",
            "description": "Calculate a mathematical expression",
            "parameters": {
                "type": "object",
                "properties": {
                    "expression": {
                        "type": "string",
                        "description": "Mathematical expression, e.g., '2 + 3 * 4'"
                    }
                },
                "required": ["expression"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather information for a specified city",
            "parameters": {
                "type": "object",
                "properties": {
                    "city": {
                        "type": "string",
                        "description": "City name, e.g., 'New York', 'London'"
                    }
                },
                "required": ["city"]
            }
        }
    }
]

# Tool function mapping
TOOL_FUNCTIONS = {
    "get_current_time": get_current_time,
    "calculate": calculate,
    "get_weather": get_weather,
}


async def run_agent(query: str) -> str:
    """
    Run OpenAI Agent
    
    Args:
        query: User query
        
    Returns:
        Agent response
    """
    if not OPENAI_AVAILABLE:
        # Simulation mode
        return f"(Simulated response) Received query: {query}. OpenAI SDK not installed, please install for full functionality."
    
    try:
        logger.info(f"Running Agent, query: {query}")
        
        # Initialize OpenAI client
        client = AsyncOpenAI(
          base_url=os.getenv("OPENAI_API_BASE"),
          api_key=os.getenv("NOVITA_API_KEY"),
        )
        
        # First call: send user message and tool definitions
        messages = [
            {"role": "system", "content": "You are a helpful AI assistant that can get time, calculate mathematical expressions, and query weather."},
            {"role": "user", "content": query}
        ]
        
        response = await client.chat.completions.create(
            model=os.getenv("MODEL_NAME", "deepseek/deepseek-v3.1-terminus"),
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
        
        response_message = response.choices[0].message
        
        # Check if tool calls are needed
        if response_message.tool_calls:
            # Add assistant's response to message history
            messages.append(response_message)
            
            # Process each tool call
            for tool_call in response_message.tool_calls:
                function_name = tool_call.function.name
                function_args = eval(tool_call.function.arguments)
                
                logger.info(f"Calling tool: {function_name}, args: {function_args}")
                
                # Execute tool function
                function_response = TOOL_FUNCTIONS[function_name](**function_args)
                
                # Add tool response to message history
                messages.append({
                    "tool_call_id": tool_call.id,
                    "role": "tool",
                    "name": function_name,
                    "content": function_response
                })
            
            # Second call: get final response
            final_response = await client.chat.completions.create(
                model=os.getenv("MODEL_NAME", "deepseek/deepseek-v3.1-terminus"),
                messages=messages
            )
            
            result = final_response.choices[0].message.content
        else:
            result = response_message.content
        
        logger.info("Agent execution completed")
        return result
        
    except Exception as e:
        logger.error(f"Agent execution error: {e}", exc_info=True)
        raise


# Define Novita Agent Runtime entrypoint (supports async)
@app.entrypoint
async def agent_invocation(request: dict) -> dict:
    """
    OpenAI Agents SDK entrypoint
    
    Args:
        request: Request data containing the following fields:
            - prompt: User input query
            
    Returns:
        Response data dict containing result field
    """
    prompt = request.get("prompt", "Hello!")
    
    print(f"📨 Received request: {prompt}")
    
    try:
        result = await run_agent(prompt)
        
        print(f"✅ Returning response: {result[:100]}...")
        
        return {
            "result": result,
            "status": "success"
        }
        
    except Exception as e:
        error_msg = f"Error processing request: {str(e)}"
        print(f"❌ Error: {error_msg}")
        return {
            "result": error_msg,
            "status": "error"
        }


if __name__ == "__main__":
    print("🚀 Starting OpenAI Agents SDK Runtime...")
    print("🛠️  Available tools: get_current_time, calculate, get_weather")
    print("🔗 Listening on port: 8080")
    app.run()
