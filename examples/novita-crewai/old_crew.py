import os
from crewai import Agent, Crew, Process, Task, LLM

# Define the LLMs for each agent
researcher_llm = LLM(
    model="novita/deepseek/deepseek-r1-turbo",
    temperature=0.5,
    api_base="https://api.novita.ai/v3/openai",
    api_key=os.environ['NOVITA_API_KEY']
)

outliner_llm = LLM(
    model="novita/meta-llama/llama-3.1-8b-instruct",
    temperature=0.4,
    api_base="https://api.novita.ai/v3/openai",
    api_key=os.environ['NOVITA_API_KEY']
)

writer_llm = LLM(
    model="novita/meta-llama/llama-3.3-70b-instruct",
    temperature=0.4,
    api_base="https://api.novita.ai/v3/openai",
    api_key=os.environ['NOVITA_API_KEY']
)

# Define the agents with their roles, goals, and backstories
researcher = Agent(
    role='Senior Research Specialist for {topic}',
    goal="Find comprehensive and accurate information about {topic} with a focus on recent developments and key insights",  
    backstory="""You are an experienced research specialist with a talent for finding relevant information from various sources. 
                 You excel at organizing information in a clear and structured manner, making complex topics accessible to others.""",
    llm=researcher_llm,
    verbose=True
)

outliner = Agent(
    role='Content Structuring Expert for {topic}',
    goal="""Develop a logical and engaging outline that reflects 
            the research findings and provides a solid structure 
            for writing a full article""",  
    backstory="""You are a content strategist with a background in instructional design
            and technical writing. You're known for your ability to organize complex
            material into easy-to-follow formats that improve clarity and flow.""",
    llm=outliner_llm,
    verbose=True
)

writer = Agent(
    role='Research Article Writer on {topic}',
    goal="""Write a well-structured, engaging research article using the outline 
            and research findings""",  
    backstory="""You are a skilled writer with a background in journalism and scientific
                 communication. You take pride in transforming data and outlines into
                 polished narratives that are informative and enjoyable to read.""",
    llm=writer_llm,
    verbose=True
)

research_task = Task(
    description="""
        Conduct thorough research on {topic}. Focus on:
        1. Key concepts and definitions
        2. Historical development and recent trends
        3. Major challenges and opportunities
        4. Notable applications or case studies
        5. Future outlook and potential developments

        Make sure to organize your findings in a structured format with clear sections.
    """,
    expected_output="""
        A comprehensive research document with well-organized sections covering
        all the requested aspects of {topic}. Include specific facts, figures,
        and examples where relevant.
    """,
    agent=researcher,
)

outline_task = Task(
    description="""
        Based on the research findings, create a detailed outline for a research article.
        The outline should:
        1. Include an introduction and conclusion
        2. Clearly structure the main body with logical headings and subheadings
        3. Ensure the flow of information builds progressively and coherently
        4. Align with the expected audience (e.g., technical, general)
        """,
    expected_output="""
        A clean, detailed outline with clear headings and subheadings that reflects
        the structure of the future article.
        """,
    agent=outliner,
    context=[research_task]
)

writing_task = Task(
    description="""
        Use the research findings and the outline to write a comprehensive,
        engaging, and well-structured research article on {topic}.
        """,
    expected_output="""
        A polished article written in markdown format with clear sections, strong
        narrative flow, and citations or links to data sources if applicable.
        """,
    agent=outliner,
    context=[research_task, outline_task],
    output_file="research_article.md"
)

research_crew = Crew(
    agents=[researcher, outliner, writer],
    tasks=[research_task, outline_task, writing_task],
    process=Process.sequential,
    verbose=True
)

if __name__ == "__main__":
    research_crew.kickoff(inputs={"topic": "Multi-Agent Systems"})