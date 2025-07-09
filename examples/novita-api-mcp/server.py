import os

from mcp.server.fastmcp import FastMCP
import requests

base_url = "https://api.novita.ai/v3"

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ['NOVITA_API_KEY']}"
}

mcp = FastMCP("Novita_API")

@mcp.tool()
def list_models() -> str:
    """
    List all available models from the Novita API.
    """

    url = base_url + "/openai/models"

    response = requests.request("GET", url, headers=headers)
    data = response.json()["data"]
    
    text = ""
    for i, model in enumerate(data, start=1):
        text += f"Model id: {model['id']}\n"
        text += f"Model description: {model['description']}\n"
        text += f"Model type: {model['model_type']}\n\n"
    
    return text

@mcp.tool()
def get_model(model_id: str, message) -> str:
    """
    Provide a model ID and a message to get a response from the Novita API.
    """

    url = base_url + "/openai/chat/completions"

    payload = {
        "model": model_id,
        "messages": [
            {
                "content": message,
                "role": "user",
            }
        ],
        "max_tokens": 200,
        "response_format": {
            "type": "text",
        },
    }

    response = requests.request("POST", url, json=payload, headers=headers)
    
    content = response.json()["choices"][0]["message"]["content"]

    return content

@mcp.tool()
def text2Image(prompt: str) -> str:
    """ 
    Generate an image from a text prompt using the Novita API.
    """

    url = base_url + "/async/txt2img"

    payload = {
        "request": {
            "model_name": "sd_xl_base_1.0.safetensors",
            "prompt": prompt,
            "width": 1024,
            "height": 1024,
            "image_num": 1,
            "steps": 20,
            "clip_skip": 1,
            "sampler_name": "Euler a",
            "guidance_scale": 7.5,
        },
        "extra": {
            "response_image_type": "jpeg"
        } 
    }

    response = requests.request("POST", url, json=payload, headers=headers)

    return response.json()["task_id"]

@mcp.tool()
def task_result(task_id: str) -> str:
    """
    Get the current status of a running task using it's task id
    """

    url = base_url + f'/async/task-result?task_id={task_id}'

    response = requests.request("GET", url, headers=headers)
    return response.json()

@mcp.tool()
def generateVideo(prompt: str) -> str:
    """
    Generate an image using a prompt
    """

    url = base_url + "/async/kling-v1.6-t2v"

    payload = {
        "mode": "Standard",
        "prompt": prompt,
        "negative_prompt": "low quality",
        "guidance_scale": 0.6
    }

    response = requests.post(url, json=payload, headers=headers)
    
    return response.json()["task_id"]

@mcp.tool()
def textToSpeech(text, voice_id) -> str:
    """
    Generate speech using text and voice id. 
    It returns the task id of the generated speech.
    
    The available voice ids are:
    - Emily
    - James
    - Olivia
    - Michael
    - Sarah
    - John
    """

    url = base_url + "/async/txt2speech"

    payload = {
        "request": {
            "voice_id": voice_id,
            "language": "en-US",
            "texts": [text]
        }
    }

    response = requests.post(url, json=payload, headers=headers)
    
    return response.json()["task_id"]

if __name__ == "__main__":
    # Run using stdio transport
    mcp.run(transport="stdio")