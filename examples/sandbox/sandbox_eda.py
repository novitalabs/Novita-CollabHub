import base64
import io
import json
import time

import matplotlib.pyplot as plt
from openai import OpenAI
from PIL import Image
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table
import shutil
from pathlib import Path

# Find the guides to use Novita Sandbox SDKs at https://novita.ai/docs/guides/sandbox-overview.
from novita_sandbox.code_interpreter import Sandbox, FileType

from prompts.system_prompt import SYSTEM_PROMPT

console = Console()

AVAILABLE_FUNCTION_CALL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "run_python_code",
            "description": "Runs the python code and returns the result if any.",
            "parameters": {
                "type": "object",
                "properties": {
                    "python_code": {
                        "type": "string",
                        "description": "The Python code to run.",
                    }
                },
                "required": ["python_code"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_on_command_line",
            "description": "Runs the command on the command line and returns the result if any.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to run on the command line.",
                    }
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sync_with_user",
            "description": "Will sync a file or directory on sandbox, to the sync folder on the user's computer",
            "parameters": {
                "type": "object",
                "properties": {
                    "sandbox_path": {
                        "type": "string",
                        "description": "Path to the file or directory on the sandbox.",
                    },
                    "path_on_user_sync_folder": {
                        "type": "string",
                        "description": "Relative path where the file or directory will be placed inside the user's sync folder. For example, '/hello.txt' goes directly in the sync folder, while '/run1/hello.txt' will be placed in a 'run1' subfolder within the sync folder.",
                    },
                },
                "required": ["sandbox_path", "path_on_user_sync_folder"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "delete_from_user_sync_folder",
            "description": "Will delete a file or directory from the sync folder on the user's computer",
            "parameters": {
                "type": "object",
                "properties": {
                    "path_on_user_sync_folder": {
                        "type": "string",
                        "description": "Relative path to the file or directory on the user's sync folder. For example, '/hello.txt' will delete it directly from the sync folder, while '/run1/hello.txt' will delete it directly from 'run1' subfolder within the sync folder.",
                    }
                },
                "required": ["path_on_user_sync_folder"],
            },
        },
    },
]


def display_sandbox_code_output(code_result: dict):
    """
    Beautifully display the output from sandbox code execution.

    Args:
        code_result (dict): Sandbox execution results with structure:
            {
                "image_outputs": list[base64 images],
                "other_outputs": {
                    "outputs": list[str],
                    "logs": list[str],
                    "error": list[str]
                }
            }
    """

    if code_result["image_outputs"]:
        console.print(
            Panel(
                "[bold cyan]Image Outputs Displayed Below (if possible otherwise check temp-*.png files):[/bold cyan]",
                title="Image Output",
                border_style="green",
            )
        )
        display_images_if_possible(code_result["image_outputs"])

    output_table = Table(show_header=True, header_style="bold magenta")
    output_table.add_column("Code Execution Output")

    output_table.add_row(str(code_result["other_outputs"]))

    console.print(output_table)

    if code_result["other_outputs"]["error"]:
        console.print(
            Panel(
                f"[bold red]Error:[/bold red] {code_result['other_outputs']['error']}",
                title="Execution Error",
                border_style="red",
            )
        )


def display_sandbox_command_output(command_result: dict):
    """
    Beautifully display the output from sandbox command execution.

    Args:
        command_result (dict): Sandbox command results with structure:
            {
                "output": str,
                "execution error": str
            }
    """

    if command_result["output"]:
        output_table = Table(show_header=True, header_style="bold magenta")
        output_table.add_column("Command Execution Output")
        output_table.add_row(str(command_result["output"]))
        console.print(output_table)

    if command_result["execution error"]:
        console.print(
            Panel(
                f"[bold red]Error:[/bold red] {command_result['execution error']}",
                title="Execution Error",
                border_style="red",
            )
        )


def display_images_if_possible(image_outputs):
    """
    Displays the images on stdout or matplotlib figure viewer if possible.

    Args:
        image_outputs (list): The base64 encoded images.
    """

    for i, b64image in enumerate(image_outputs):
        image_data = base64.b64decode(b64image)
        image = Image.open(io.BytesIO(image_data))

        plt.figure()  # create a new figure for each image
        plt.imshow(image)  # display the image
        plt.axis("off")  # turn off axis
        plt.show(block=False)  # continue running the program while the plot is open


class SandboxEDA:

    def __init__(
        self,
        sandbox: Sandbox,
        model_api_base_url: str,
        model_api_key: str,
        max_consecutive_function_calls_allowed: int = 30,
    ):
        self.sandbox = sandbox
        self.model_api_base_url = model_api_base_url
        self.model_api_key = model_api_key
        self.max_consecutive_function_calls_allowed = (
            max_consecutive_function_calls_allowed
        )

    def upload_files_to_sandbox(
        self, file_paths: list[str], file_names_in_sandbox: list[str]
    ):
        """
        Uploads files to the sandbox.

        Args:
            file_paths (list[str]): File paths of the files to upload (eg ["./Download/data.csv", "./Download/data2.csv"]).
            file_names_in_sandbox (list[str]): The names the files will take in the sandbox (eg ["data.csv", "data2.csv"]).

        Note:
            The files will be uploaded to the sandbox's /home/user directory (e.g ./home/user/data.csv, ./home/user/data2.csv).
        """

        console.print(
            f"[yellow]Uploading files(s) at {file_paths} to Sandbox[/yellow] (id: {self.sandbox.sandbox_id})"
        )

        for file_path, file_name_in_sandbox in zip(file_paths, file_names_in_sandbox):
            with open(file_path, "rb") as file:
                self.sandbox.files.write(file_name_in_sandbox, file)

        console.print(
            f"[bold cyan]Files(s) {file_paths} uploaded to Sandbox[/bold cyan] (id: {self.sandbox.sandbox_id})"
        )

    def run_python_code(self, python_code: str) -> dict:
        """
        Runs the python code on the sandbox, and if there are any images save them locally.

        Args:
            python_code (str): The python code to run.

        Returns:
            dict: Containing the base64 image outputs and other outputs (stdout, logs, error, etc).
        """
        execution = self.sandbox.run_code(python_code, language="python")

        image_outputs = [result.png for result in execution.results if result.png]

        # Iterate through the base64 encoded images and save them to a file with name format: temp-{timestamp}.png to ./temp_image_output dir
        for b64_image in image_outputs:
            timestamp = int(time.time_ns())
            image_filename = Path(f"./temp_image_output/temp-{timestamp}.png")

            # Will create the temp_image_output directory if it doesn't exist already.
            image_filename.parent.mkdir(parents=True, exist_ok=True)

            with open(image_filename, "wb") as f:
                f.write(base64.b64decode(b64_image))

        return {
            "image_outputs": image_outputs,
            "other_outputs": {
                "outputs": [result for result in execution.results if not result.png],
                "logs": execution.logs,
                "error": execution.error,
            },
        }

    def run_on_command_line(self, command: str) -> dict:
        """
        Runs the command on the sandbox.

        Args:
            command (str): The command to run.

        Returns:
            dict: Containing the output of the command and the execution error if any.
        """

        try:
            result = self.sandbox.commands.run(command)
            return {
                "output": {
                    "stdout": result.stdout,
                    "stderr": result.stderr,
                    "exit_code": result.exit_code,
                    "error": result.error,
                },
                "execution error": None,
            }

        except Exception as e:
            return {"output": None, "execution error": str(e)}

    def sync_with_user(self, sandbox_path, path_on_user_sync_folder):
        """
        Downloads a file or directory from the sandbox to the user's sync folder.

        Args:
            sandbox_path (str): The path of the file or directory to sync in the sandbox.
            path_on_user_sync_folder (str): The relative destination path of the file or directory in the user's sync folder.

        Returns:
            str: "Sync Successful" if the file or directory was synced successfully, otherwise an error message.
        """

        try:
            path_info = self.sandbox.files.get_info(sandbox_path)

            if path_info.type == FileType.DIR:
                # If its a directory loop through the contents and download them.
                dir_contents = self.sandbox.files.list(sandbox_path)
                for content in dir_contents:
                    path_to_content_in_sync_folder = Path(
                        path_on_user_sync_folder
                    ).joinpath(content.name)
                    self.sync_with_user(content.path, path_to_content_in_sync_folder)

            elif path_info.type == FileType.FILE:
                # Ensure the file is always inside ./sync_folder.
                sandbox_path_obj = Path(path_on_user_sync_folder)

                # Make the path relative by stripping any root or drive component
                relative_path = sandbox_path_obj.relative_to(
                    sandbox_path_obj.anchor or "."
                )

                # Final path inside sync_folder
                file_path = Path("sync_folder") / relative_path

                # Will create any directory in the path that doesn't exist already.
                file_path.parent.mkdir(parents=True, exist_ok=True)

                # Download the file to sync folder.
                file_content = self.sandbox.files.read(sandbox_path, "bytes")
                with open(file_path, "wb") as f:
                    f.write(file_content)

            return "Sync Successful"

        except Exception as e:
            return str(e)

    def delete_from_user_sync_folder(self, path_on_user_sync_folder):
        """
        Deletes a file or directory from the user sync folder.

        Args:
            path_on_user_sync_folder (str): The path of the file or directory to delete in the user sync folder.

        Returns:
            str: "Deletion Successful" if the file or directory was deleted successfully, otherwise an error message.
        """
        # Ensure the file is always inside ./sync_folder.
        sandbox_path_obj = Path(path_on_user_sync_folder)

        # Make the path relative by stripping any root or drive component
        relative_path = sandbox_path_obj.relative_to(sandbox_path_obj.anchor or ".")

        # Final path inside sync_folder
        delete_path = Path("sync_folder") / relative_path

        try:
            if not delete_path.exists():
                raise Exception(
                    f"File or Directory does not exist at {path_on_user_sync_folder} in sync folder."
                )

            if delete_path.is_file():
                delete_path.unlink()

            elif delete_path.is_dir():
                shutil.rmtree(str(delete_path))

            return "Deletion Successful"

        except Exception as e:
            return str(e)

    def list_files_in_sandbox_main_dir(self) -> list[str]:
        return [i.name for i in self.sandbox.files.list("/home/user")]

    def eda_chat(
        self,
        downloaded_dataset_names: list[str],
        model_for_eda: str,
    ):
        """
        Interactive EDA session with AI agent capable of code execution and terminal commands

        Args:
            downloaded_dataset_names (list[str]): The names of the downloaded datasets.
            model_for_eda (str, optional): The underlying model to use.
        """

        console.print(
            Panel(
                "[bold green]EDA Session Started[/bold green]\nType 'quit()' to exit.",
                title="Exploratory Data Analysis",
                border_style="green",
            )
        )

        client = OpenAI(
            base_url=self.model_api_base_url,
            api_key=self.model_api_key,
        )

        # Initialize conversation with system prompt
        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT.format(
                    downloaded_dataset_names=str(downloaded_dataset_names),
                    list_sandbox_files=str(self.list_files_in_sandbox_main_dir()),
                    available_function_calls_schema=str(
                        AVAILABLE_FUNCTION_CALL_SCHEMAS
                    ),
                    max_consecutive_function_calls_allowed=self.max_consecutive_function_calls_allowed,
                ),
            }
        ]

        # Main chat loop
        while True:
            user_input = Prompt.ask("\n[bold yellow]>>> User Message[/bold yellow]")
            if user_input.lower().strip() == "quit()":
                break

            messages.append({"role": "user", "content": user_input})

            # Handle potential consecutive tool calls with a safety limit to avoid infinite loops
            for i in range(self.max_consecutive_function_calls_allowed + 1):

                if i == self.max_consecutive_function_calls_allowed:
                    raise Exception(
                        f"Consecutive tool calls from the Agent must not exceed {self.max_consecutive_function_calls_allowed}."
                    )

                response = client.chat.completions.create(
                    model=model_for_eda,
                    messages=messages,
                    tools=AVAILABLE_FUNCTION_CALL_SCHEMAS,
                    frequency_penalty=0,  # This penalty can slightly affect tool use; keep at 0.
                )

                response_message = response.choices[0].message
                tool_calls = response_message.tool_calls

                if tool_calls:

                    messages.append(
                        response_message
                    )  # Add assistant message that triggered tool calls

                    # Execute each requested tool call
                    for tool_call in tool_calls:
                        name = tool_call.function.name
                        args = json.loads(tool_call.function.arguments)

                        if name == "run_python_code":
                            console.print(
                                Panel(
                                    args["python_code"],
                                    title="Agent Executing Python Code",
                                    border_style="blue",
                                )
                            )

                            code_result = self.run_python_code(args["python_code"])
                            messages.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",
                                    "name": name,
                                    # If there are any image outputs (e.g data visualization), as it is not yet possible to return images
                                    # from a tool call just inform the Agent that the image has been shown to the user.
                                    "content": [
                                        {
                                            "type": "text",
                                            "text": (
                                                f"THE IMAGES HAS ALREADY BEEN SHOW TO THE USER ON THE TERMINAL AND SAVED TO TEMP FILES eg temp-{{timestamp}}.png on the user's computer in ./temp_image_output dir, THE OTHER OUTPUTS ARE BELOW\n{code_result['other_outputs']}"
                                                if code_result["image_outputs"]
                                                else f"{code_result['other_outputs']}"
                                            ),
                                        }
                                    ],
                                }
                            )

                            display_sandbox_code_output(code_result)

                        elif name == "run_on_command_line":
                            console.print(
                                Panel(
                                    args["command"],
                                    title="Agent Executing Command On Terminal",
                                    border_style="blue",
                                )
                            )

                            command_result = self.run_on_command_line(args["command"])
                            messages.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",  # Indicates this message is from tool use
                                    "name": name,
                                    "content": str(command_result),
                                }
                            )

                            display_sandbox_command_output(command_result)

                        elif name == "sync_with_user":
                            console.print(
                                Panel(
                                    f"[bold yellow]Agent Started Syncing {args['sandbox_path']} To User's Sync Folder ({args['path_on_user_sync_folder']})[/bold yellow]",
                                    title="File Syncing",
                                    border_style="white",
                                )
                            )

                            sync_result = self.sync_with_user(
                                args["sandbox_path"], args["path_on_user_sync_folder"]
                            )
                            messages.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",  # Indicates this message is from tool use
                                    "name": name,
                                    "content": sync_result,
                                }
                            )

                            if sync_result == "Sync Successful":
                                console.print(
                                    Panel(
                                        f"[bold green]Agent Successfully Synced File(s) To User's Sync Folder ({args['path_on_user_sync_folder']})[/bold green]",
                                        title="File Syncing",
                                        border_style="white",
                                    )
                                )
                            else:
                                console.print(
                                    Panel(
                                        f"[bold red]Agent Failed To Sync File(s) To User's Sync Folder: {sync_result}[/bold red]",
                                        title="File Syncing",
                                        border_style="white",
                                    )
                                )

                        elif name == "delete_from_user_sync_folder":
                            console.print(
                                Panel(
                                    f"[bold yellow]Agent Deleting File(s) From User's Sync Folder ({args['path_on_user_sync_folder']})[/bold yellow]",
                                    title="File Syncing",
                                    border_style="white",
                                )
                            )

                            delete_result = self.delete_from_user_sync_folder(
                                args["path_on_user_sync_folder"]
                            )
                            messages.append(
                                {
                                    "tool_call_id": tool_call.id,
                                    "role": "tool",  # Indicates this message is from tool use
                                    "name": name,
                                    "content": delete_result,
                                }
                            )

                            if delete_result == "Deletion Successful":
                                console.print(
                                    Panel(
                                        f"[bold green]Agent Successfully Deleted File(s) From User's Sync Folder ({args['path_on_user_sync_folder']})[/bold green]",
                                        title="File Syncing",
                                        border_style="white",
                                    )
                                )
                            else:
                                console.print(
                                    Panel(
                                        f"[bold red]Agent Failed To Delete File(s) From User's Sync Folder: {delete_result}[/bold red]",
                                        title="File Syncing",
                                        border_style="white",
                                    )
                                )

                        else:
                            raise ValueError(f"Unknown Function Call: {name}")

                else:
                    # No tool calls just display assistant response after adding it to the messages.
                    messages.append(
                        {"role": "assistant", "content": response_message.content}
                    )
                    console.print(
                        f"[bold green]>>> Assistant Response: {response_message.content} [/]"
                    )
                    break
