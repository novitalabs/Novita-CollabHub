# Browser Use Agent

An AI agent based on the [Browser-use](https://github.com/browser-use/browser-use) that can execute web automation tasks.

## Prerequisites

- Python 3.12+
- Novita AI account and API Key

## Installation and Setup Guide

### 1. Create Python Virtual Environment

Ensure you have Python 3.12+ installed, then create a virtual environment:

```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# macOS/Linux:
source .venv/bin/activate

# Windows:
# .venv\Scripts\activate
```

### 2. Install Dependencies

Ensure the virtual environment is activated, then install the required dependencies:

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

Copy the example environment file and rename it:

```bash
cp .env.example .env
```

Then modify the following variables in the `.env` file:

- `E2B_API_KEY`: Your Novita AI API key
- `LLM_API_KEY`: Your Novita AI API key  
- `LLM_MODEL`: The model id you want to use (e.g., `deepseek/deepseek-v3-0324`)

### 4. Run the Program

After configuration is complete, run the main program:

```bash
python agent.py
```

## Program Features

The program will:

1. Create an E2B sandbox with the template `browser-chromium`
2. Connect to the browser and execute automation tasks with Browser-use
3. Default task: Visit Google and search for "browser-use" information, then summarize the results
4. Automatically take screenshots during execution and save to `./screenshots/` directory

## Output Files

- **Screenshot files**: Saved in `./screenshots/{session_id}/` directory with filename format `{domain}_{timestamp}.png`
- **Log output**: Detailed execution logs are displayed in the console

## Troubleshooting

1. **Dependency installation failure**: Ensure you're using Python 3.12 and the latest pip version
2. **Environment variable errors**: Check that the `.env` file is correctly configured with all required environment variables
3. **E2B connection issues**: Verify that E2B API Key and domain configuration are correct
4. **LLM API errors**: Confirm that the LLM API key is valid and has sufficient quota

## Custom Template

This project uses the default Novita AI's `browser-chromium` template. If you need to customize the browser environment with additional dependencies or specific configurations, you can build your own template based on it.

### Building a Custom Template

Navigate to the [e2b-template](./e2b-template) folder and follow these steps:

1. **Modify dependencies**: Edit `e2b.Dockerfile` to add any additional packages you need
2. **Configure startup**: Modify `start-up.sh` to include custom start up scripts
3. **Build the template**: Run the build script to create your custom template:
   ```bash
   ./build.sh
   ```

After building, update your agent code to use the new template id instead of `browser-chromium`. You can find the new template id in the `e2b.toml` file in the [e2b-template](./e2b-template) folder.

```python
sandbox = Sandbox(
  timeout=600,  # seconds
  template="new_template_id",
)
```
