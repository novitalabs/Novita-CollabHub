import json
import os
from typing import Literal, Dict, Any
from pydantic import BaseModel, ValidationError
from crewai import Agent, LLM
from crewai.flow.flow import Flow, start, router, listen

# Define the flow state
class SupportState(BaseModel):
    issue: Literal["billing", "technical", "general"] = "general"
    message: str = ""

# Define the flow class
class CustomerSupportFlow(Flow[SupportState]):

    @start()
    def classify_issue(self) -> Dict[str, Any]:
        intake_agent = Agent(
            role="User Intake Agent",
            goal="Classify user support issue and summarize the message",
            backstory="You classify the user query into billing, technical, or general categories.",
            llm=LLM(
                model="novita/qwen/qwen2.5-vl-72b-instruct",
                temperature=0.3,
                api_base="https://api.novita.ai/v3/openai",
                api_key=os.environ["NOVITA_API_KEY"]
            ),
            verbose=True
        )
        
        prompt = f"""
            A user submitted this message: "{self.state.message}"

            Your task:
            1. Identify whether the issue is "billing", "technical", or "general".
            2. Rephrase or extract the message clearly.

            Respond in valid JSON format like the example below:

            {{
                "issue": "billing",
                "message": "The user has been charged twice for their subscription and is requesting a refund."
            }}
        """

        output = intake_agent.kickoff(prompt, response_format=SupportState)
        
        try:
            # Parse the JSON string
            print(output.raw)
            parsed_json = json.loads(output.raw)

            # Validate with Pydantic
            validated = SupportState(**parsed_json)

            # Save to state
            self.state.issue = validated.issue
            self.state.message = validated.message

        except (json.JSONDecodeError, ValidationError) as e:
            print("❌ Failed to parse or validate response:", e)
            self.state.issue = "general"

    @router(classify_issue)
    def route_based_on_issue(self) -> str:
        print(f"📨 Routing to agent for issue type: {self.state.issue}")
        if self.state.issue == "billing":
            return "billing"
        if self.state.issue == "technical":
            return "technical"
        else:
            return "general"        

    @listen("billing")
    def handle_billing(self):
        agent = Agent(
            role="Billing Agent",
            goal="Handle billing questions, refunds, and invoice issues",
            backstory="You resolve billing-related queries effectively.",
            llm=LLM(
                model="novita/meta-llama/llama-3.3-70b-instruct",
                temperature=0.5,
                api_base="https://api.novita.ai/v3/openai",
                api_key=os.environ["NOVITA_API_KEY"]
            ),
            verbose=True
        )
        result = agent.kickoff(self.state.message)
        print("💰 Billing Agent Response:", result)

    @listen("technical")
    def handle_technical(self):
        agent = Agent(
            role="Technical Support Agent",
            goal="Help users resolve technical issues",
            backstory="You're a technical expert providing troubleshooting support.",
            llm=LLM(
                model="novita/meta-llama/llama-3.1-8b-instruct",
                temperature=0.5,
                api_base="https://api.novita.ai/v3/openai",
                api_key=os.environ["NOVITA_API_KEY"]
            ),
            verbose=True
        )
        result = agent.kickoff(self.state.message)
        print("🛠 Technical Agent Response:", result)

    @listen("general")
    def handle_general(self):
        agent = Agent(
            role="General Support Agent",
            goal="Provide helpful answers to non-technical and non-billing questions",
            backstory="You're friendly and well-informed about our services.",
            llm=LLM(
                model="novita/minimaxai/minimax-m1-80k",
                temperature=0.5,
                api_base="https://api.novita.ai/v3/openai",
                api_key=os.environ["NOVITA_API_KEY"]
            ),
            verbose=True
        )
        result = agent.kickoff(self.state.message)
        print("📋 General Agent Response:", result)


# Usage Example
def run():
    flow = CustomerSupportFlow()
    flow.plot("CustomerSupportFlowPlot")

    # Example input message
    example_input = {
        "message": "Hello, I was charged twice for my subscription and need a refund."
    }

    flow.kickoff(inputs=example_input)


if __name__ == "__main__":
    run()

