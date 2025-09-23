from typing import Tuple, Optional

from browser_use import Agent, BrowserProfile, BrowserSession, Controller
from browser_use.llm import ChatOpenAI
from pydantic import BaseModel, Field
from rich.console import Console
from rich.panel import Panel
from pathlib import Path

console = Console()


class TaskFile(BaseModel):
    """Represents a file generated as part of a task result e.g. scraped data or researched data."""

    filename: str = Field(..., description="Name of the file including extension")
    content: str = Field(..., description="Text content to be written into the file")


class AgentOutput(BaseModel):
    """Final aggregated output of the browser agent execution."""

    downloaded_files: Optional[list[str]] = Field(
        None, description="List of downloaded file names (with extension), if any"
    )
    task_files: Optional[list[TaskFile]] = Field(
        None,
        description="Files generated from user tasks (e.g., scraped or researched data), if any",
    )


async def downloading_task_for_browser_agent(
    task: str,
    api_key: str,
    model: str,
    model_api_base_url: str,
    use_vision: bool,
    download_dir_path: str = "./Download",
) -> Tuple[str, list[str]]:
    """
    Will perform the user's download task via browser use and return download directory path and the
    downloaded files names.

    Returns:
        Tuple of (download_directory, filenames_with_extension)
    """

    agent = Agent(
        task=task,
        llm=ChatOpenAI(
            base_url=model_api_base_url,
            model=model,
            api_key=api_key,
            max_completion_tokens=20_000,
            timeout=180,
            frequency_penalty=0,  # This penalty can slightly affect tool use; keep at 0.
        ),
        use_vision=use_vision,
        vision_detail_level="auto",  # available options ['low', 'high', 'auto']; note high detail means more token cost; low should suffice for most tasks.
        browser_session=BrowserSession(
            browser_profile=BrowserProfile(
                downloads_path=download_dir_path,
                user_data_dir=None,  # "./browser_user_data"
            )
        ),  # set the download directory path for the browser.
        controller=Controller(
            output_model=AgentOutput
        ),  # Have the agent output the task execution result according to the AgentOutput schema.
        max_failures=5,
    )

    try:
        # Run the agent and structure its output
        all_results = await agent.run()
        final_output: AgentOutput = AgentOutput.model_validate_json(
            all_results.final_result()
        )

        if final_output.task_files:
            console.print(
                Panel(
                    f"[bold yellow]Writing task results to files...[/bold yellow] {final_output.task_files}",
                    title="Task Results",
                    border_style="white",
                )
            )

        # Write each task result to a file in the download directory
        task_result_files: list[str] = []
        for task_file in final_output.task_files or []:
            file_path = Path(task_file.filename)

            # Prevent path traversal or unsafe absolute paths
            if file_path.is_absolute() or ".." in file_path.parts:
                raise ValueError(
                    f"The agent passed an unsafe file path as a filename: {file_path}"
                )

            # Point the file path inside the download directory
            file_path = Path(download_dir_path) / file_path

            # Ensure the download directory exists, else create it.
            file_path.parent.mkdir(parents=True, exist_ok=True)

            # Write task result content to a file
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(task_file.content)

            task_result_files.append(task_file.filename)

        if task_result_files:
            console.print(
                Panel(
                    f"[bold green]Task results written to files:[/bold green] {task_result_files}",
                    title="Task Results",
                    border_style="white",
                )
            )

        # Combine downloaded files with task result files
        file_results = (final_output.downloaded_files or []) + task_result_files

        if file_results:
            console.print(
                Panel(
                    f"[bold green]Files available:[/bold green] {file_results} in {download_dir_path}",
                    title="Downloaded Files",
                    border_style="green",
                )
            )
        else:
            raise RuntimeError("No files were downloaded or written.")

    except Exception as e:
        file_results = None
        console.print(
            Panel(
                f"[bold red]Error:[/bold red] {str(e)}\n",
                title="Execution Error",
                border_style="red",
            )
        )

    return (download_dir_path, file_results)
