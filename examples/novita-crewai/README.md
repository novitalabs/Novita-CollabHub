# Build a Multi-Agent System with Novita and CrewAI

This repository demonstrates how to build a Multi-Agent System using [Novita](https://novita.ai/) as the model provider and [CrewAI](https://docs.crewai.com/) as the multi-agent orchestration framework.

## Table of Contents

- [Overview](#overview)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [References](#references)

## Overview

This repo contains two multi-agent system implementations:
- **Research Crew**: A class-based crew of agents that perform research tasks.
- **Customer Support Flow**: A flow-based agent for customer support automation.

## Project Structure

```
crew.py                # Class-based crew for research tasks
flow.py                # Flow-based customer support agent
old_crew.py            # Legacy crew definition
config/
  ├── agents.yaml      # Agent definitions
  └── tasks.yaml       # Task definitions
README.md
CustomerSupportFlowPlot.html
```

## Prerequisites

- Python 3.11+
- [Novita API Key](https://novita.ai/)
- [CrewAI](https://pypi.org/project/crewai/)


## Installation

1. **Clone the repository:**
   ```sh
   git clone https://github.com/Studio1HQ/novita_crewai.git
   cd novita_crewai
   ```

2. **Create and activate a virtual environment:**
   ```sh
   python -m venv env
   source env/bin/activate
   ```

3. **Install dependencies:**
   ```sh
   pip install crewai novita
   ```

## Configuration

1. **Set up your Novita API key:**
   - Create a `.env` file in the project root:
     
     ```
     NOVITA_API_KEY=your_novita_api_key_here
     ```

2. **Edit agent and task configurations:**
   - `config/agents.yaml`: Define your agents and their roles.
   - `config/tasks.yaml`: Define the tasks for your agents.

---

## Usage

- **Run the research crew:**
  ```sh
  python crew.py
  ```

- **Run the customer support flow:**
  ```sh
  python flow.py
  ```

- **Legacy crew (for reference):**
  ```sh
  python old_crew.py
  ```

## References

- [CrewAI Documentation](https://docs.crewai.com/)
- [Novita API Documentation](https://novita.ai/docs/guides/introduction)
- [CrewAI Examples](https://docs.crewai.com/en/examples/example)






