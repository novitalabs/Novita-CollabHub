import os
from crewai import Agent, Crew, Process, Task, LLM
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List

@CrewBase
class ResearchCrew():
    """Three-agent research crew: researcher, outliner, writer"""

    agents: List[BaseAgent]
    tasks: List[Task]

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def researcher(self) -> Agent:
        llm = LLM(
            model="novita/deepseek/deepseek-r1-turbo",
            temperature=0.5,
            api_base="https://api.novita.ai/v3/openai",
            api_key=os.environ['NOVITA_API_KEY']
        )
        return Agent(
            config=self.agents_config['researcher'],
            llm=llm,
            verbose=True
        )

    @agent
    def outliner(self) -> Agent:
        llm = LLM(
            model="novita/meta-llama/llama-3.1-8b-instruct",
            temperature=0.4,
            api_base="https://api.novita.ai/v3/openai",
            api_key=os.environ['NOVITA_API_KEY']
        )
        return Agent(
            config=self.agents_config['outliner'],
            llm=llm,
            verbose=True
        )

    @agent
    def writer(self) -> Agent:
        llm = LLM(
            model="novita/meta-llama/llama-3.3-70b-instruct",
            temperature=0.5,
            api_base="https://api.novita.ai/v3/openai",
            api_key=os.environ['NOVITA_API_KEY']
        )
        return Agent(
            config=self.agents_config['writer'],
            llm=llm,
            verbose=True
        )

    @task
    def research_task(self) -> Task:
        return Task(config=self.tasks_config['research_task'])

    @task
    def outline_task(self) -> Task:
        return Task(config=self.tasks_config['outline_task'])

    @task
    def writing_task(self) -> Task:
        return Task(config=self.tasks_config['writing_task'])

    @crew
    def crew(self) -> Crew:
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True
        )

def main():
    research_crew = ResearchCrew()
    research_crew.crew().kickoff(inputs={"topic": "Multi-Agent Systems"})

if __name__ == '__main__':
    main()