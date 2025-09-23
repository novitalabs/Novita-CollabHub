import asyncio
import os
from typing import Tuple

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt

# Find the guides to use Novita Sandbox SDKs at https://novita.ai/docs/guides/sandbox-overview.
from novita_sandbox.code_interpreter import Sandbox
from browser_agent import downloading_task_for_browser_agent
from sandbox_eda import SandboxEDA
from pathlib import Path

# Load environment variables from .env file
load_dotenv()

console = Console()


def start_eda(
    model_for_eda: str,
    dataset_paths: list[str],
    dataset_file_names: list[str],
    api_key_for_sandbox_and_model: str,
    model_api_base_url: str,
    sandbox_template: str,
    sandbox_timeout: int,
):

    with Sandbox.create(
        template=sandbox_template,
        timeout=sandbox_timeout,
        api_key=api_key_for_sandbox_and_model,
    ) as sandbox:

        try:
            sandbox_eda = SandboxEDA(
                sandbox, model_api_base_url, api_key_for_sandbox_and_model
            )

            console.print(
                f"[bold cyan]Started Sandbox[/bold cyan] (id: {sandbox.sandbox_id})"
            )

            sandbox_eda.upload_files_to_sandbox(dataset_paths, dataset_file_names)

            sandbox_eda.eda_chat(dataset_file_names, model_for_eda)

            console.print(
                f"\n\n[bold cyan]------ EDA Session Completed for Sandbox (id: {sandbox.sandbox_id}) ------[/]"
            )

        finally:
            console.print(
                f"[bold cyan]----- Closed Sandbox (id: {sandbox.sandbox_id})-----[/]\n"
            )


# MAIN MENU CHOICES
async def choice_download_dataset(
    api_key: str,
    model_api_base_url: str,
    model_for_browser_agent: str,
    enable_vision_for_browser_agent: bool,
) -> None | Tuple[str, list[str]]:

    console.print(
        Panel(
            "[bold green]1.[/bold green] Give detailed instruction for browser use to locate desired dataset\n"
            "[bold green]2.[/bold green] Back to main menu",
            title="Download Menu",
            border_style="white",
        )
    )

    choice = Prompt.ask(
        "\n[bold yellow]Enter your choice[/bold yellow]", choices=["1", "2"]
    ).strip()

    if choice == "1":
        dataset_download_task = Prompt.ask(
            "\n[bold yellow]Provide detailed web navigation instructions to obtain the dataset.[/bold yellow]\n"
            "[dim yellow]Examples:\n"
            "- Go to Hugging Face, search for An-j96/SuperstoreData and open its page, then navigate to the Files tab and download the data csv file.\n"
            "- Go to google finance, search for Tesla and from that page, get their income statement for the past 4 years. Note: First switch to annual tab, then switch to a year's tab and extract its data. Output should be csv.[/dim yellow]"
            "\n\n[bold yellow]Instruction[/bold yellow]"
        )

        download_path, filenames = await downloading_task_for_browser_agent(
            dataset_download_task,
            api_key,
            model_for_browser_agent,
            model_api_base_url,
            use_vision=enable_vision_for_browser_agent,
        )

        if filenames is None:
            return  # returns to main menu

        return download_path, filenames

    elif choice == "2":
        return  # return to main menu


def choice_proceed_with_already_downloaded_datasets() -> None | list[str]:
    console.print(
        Panel(
            "[bold green]1.[/bold green] Provide path to your desired dataset(s)\n"
            "[bold green]2.[/bold green] Back to main menu",
            title="Proceed with Existing Dataset",
            border_style="white",
        )
    )

    choice = Prompt.ask(
        "\n[bold yellow]Enter choice[/bold yellow]", choices=["1", "2"]
    ).strip()

    if choice == "1":
        paths = Prompt.ask(
            "\n[bold yellow]Enter dataset path(s) - separate multiple paths with commas (e.g., ./Download/data.csv, ./Reports/summary.txt)[/bold yellow]"
            "\n[dim red]ℹ️  Note: Ensure file names are unique, so uploading doesn't overwrite[/dim red]"
        ).split(",")

        paths = [
            path.strip() for path in paths if path.strip()
        ]  # Get only non empty string paths.
    elif choice == "2":
        return

    try:

        # Validate file paths and check for duplicate filenames
        filenames = set()
        for path in paths:
            if not os.path.isfile(path):
                raise FileNotFoundError(f"Invalid path: file not found at '{path}'")

            filename = os.path.basename(path)
            if filename in filenames:
                raise ValueError(
                    f"Duplicate filename '{filename}' - files must have unique names"
                )
            filenames.add(filename)

    except FileNotFoundError as e:
        console.print(f"[bold red]{str(e)}[/bold red]\n")
        return  # return to main menu

    except ValueError as e:
        console.print(f"[bold red]{str(e)}[/bold red]\n")
        return  # return to main menu

    return paths


async def main(
    api_key_for_sandbox_and_model: str,
    model_api_base_url: str,
    model_for_browser_agent: str,
    enable_vision_for_browser_agent: bool,
    model_for_eda: str,
    sandbox_template: str,
    sandbox_timeout_seconds: int,
):

    while True:

        # Welcome Banner
        console.print(
            Panel(
                "[bold white]Welcome To Agentic Exploratory Data Analysis[/bold white]\n\n"
                "[grey]How would you like to proceed:[/grey]\n"
                "[grey]1.[/grey] Download a dataset first.\n"
                "[grey]2.[/grey] Proceed with already downloaded dataset.\n"
                "[grey]3.[/grey] Exit",
                title="MAIN MENU",
                border_style="green",
                width=70,
            )
        )

        choice = Prompt.ask(
            "\n[bold yellow]Enter your choice[/bold yellow]", choices=["1", "2", "3"]
        ).strip()

        if choice == "1":
            result = await choice_download_dataset(
                api_key_for_sandbox_and_model,
                model_api_base_url,
                model_for_browser_agent,
                enable_vision_for_browser_agent,
            )
            if result:
                download_path, filenames = result
                DATASET_PATHS = [
                    str(Path(download_path) / filename) for filename in filenames
                ]
                DATASET_FILE_NAMES = filenames
            else:
                continue  # User returned to main menu

        elif choice == "2":
            result = choice_proceed_with_already_downloaded_datasets()
            if result:
                DATASET_PATHS = result
                DATASET_FILE_NAMES = [os.path.basename(path) for path in result]
            else:
                continue  # since user click back to main menu.

        elif choice == "3":
            break

        # Start the EDA session
        start_eda(
            model_for_eda,
            DATASET_PATHS,
            DATASET_FILE_NAMES,
            api_key_for_sandbox_and_model,
            model_api_base_url,
            sandbox_template,
            sandbox_timeout_seconds,
        )


if __name__ == "__main__":
    NOVITA_API_KEY = os.getenv("NOVITA_API_KEY")
    NOVITA_BASE_URL = os.getenv("NOVITA_BASE_URL")
    NOVITA_SANDBOX_TEMPLATE = os.getenv("NOVITA_SANDBOX_TEMPLATE")
    NOVITA_MODEL_FOR_BROWSER_AGENT = "qwen/qwen3-coder-480b-a35b-instruct"
    ENABLE_VISION_FOR_BROWSER_AGENT = (
        False  # If true make sure the browser agent model has vision capabilities.
    )
    NOVITA_MODEL_FOR_EDA = "qwen/qwen3-coder-480b-a35b-instruct"
    NOVITA_SANDBOX_TIMEOUT_SECONDS = 900  # 900 seconds (15 minutes), sandbox instance will be killed automatically after.

    asyncio.run(
        main(
            NOVITA_API_KEY,
            NOVITA_BASE_URL,
            NOVITA_MODEL_FOR_BROWSER_AGENT,
            ENABLE_VISION_FOR_BROWSER_AGENT,
            NOVITA_MODEL_FOR_EDA,
            NOVITA_SANDBOX_TEMPLATE,
            NOVITA_SANDBOX_TIMEOUT_SECONDS,
        )
    )
