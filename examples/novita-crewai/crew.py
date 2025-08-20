import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

from crewai_tools import FileWriterTool

# Instantiate tool
file_writer_tool = FileWriterTool()


@CrewBase
class CodeCrew():

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    
    @agent
    def architect(self) -> Agent:
        llm = LLM(
            model="novita/moonshotai/kimi-k2-instruct",
            temperature=0.5,
            api_base="https://api.novita.ai/v3/openai",
            api_key=os.environ['NOVITA_API_KEY']
        )
        return Agent(
            config=self.agents_config['architect'],
            llm=llm,
            verbose=True
        )

    @agent
    def coder(self) -> Agent:
        llm = LLM(
            model="novita/qwen/qwen3-coder-480b-a35b-instruct",
            temperature=0.4,
            api_base="https://api.novita.ai/v3/openai",
            api_key=os.environ['NOVITA_API_KEY']
        )
        return Agent(
            config=self.agents_config['coder'],
            llm=llm,
            verbose=True,
            tools=[file_writer_tool]
        )

    @agent
    def reviewer(self) -> Agent:
        llm = LLM(
            model="novita/moonshotai/kimi-k2-instruct",
            temperature=0.5,
            api_base="https://api.novita.ai/v3/openai",
            api_key=os.environ['NOVITA_API_KEY']
        )
        return Agent(
            config=self.agents_config['reviewer'],
            llm=llm,
            verbose=True,
        )

    @task
    def architect_task(self) -> Task:
        return Task(config=self.tasks_config['architect_task'])

    @task
    def coder_task(self) -> Task:
        return Task(config=self.tasks_config['coder_task'])

    @task
    def review_task(self) -> Task:
        return Task(config=self.tasks_config['review_task'])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

def main():
    code_crew = CodeCrew()
    code_crew.crew().kickoff(inputs={"project": "Todo App"})

if __name__ == '__main__':
    main()
