from .base import BaseAgent
from pydantic import BaseModel, Field
from prompts import get_prompt
from utils import parse_json_response, get_model_client
from typing import Dict, List, Any
from brain import MentalState
from time import sleep
from camel.agents import ChatAgent


class Agenda(BaseModel):
    topics: List[str] = Field(
        description="List of topics to discuss in the session (1-3)",
        default_factory=list,
    )
    goals: List[str] = Field(
        description="Goals for the session (1-3)", default_factory=list
    )


class BaseTherapistResponse(BaseModel):
    # client_mental_state: Dict[str, MentalState] = Field(
    #     description="The Client's current mental state"
    # )
    reasoning: str = Field(
        description="Your reasoning about the how you should approach the client in this turn (2-4 sentences)"
    )
    response: str = Field(
        description="Your generated response based on the client's mental state and your reasoning (1-2 sentences)"
    )


class SessionSummary(BaseModel):
    summary: str = Field(
        description="A summary of the session, including key points discussed and next steps (1-3 sentences)"
    )
    next_steps: str = Field(
        description="Next steps for the client, including any homework or follow-up actions (1-3 items)"
    )


class BasicTherapist(BaseAgent):
    def __init__(self, model_name: str, data: Dict[str, Any]):
        self.role = "therapist"
        self.agent_type = "basic"
        self.data = data
        self.agenda = {}
        self.messages = []
        self.memory = []
        self.client_mental_state = MentalState().model_dump(mode="json")
        self.model_client = get_model_client(model_name)
        self.agent = self.create_agent()

    def create_agent(self):
        self.sys_prompt = get_prompt(self.role, self.agent_type).render(
            data=self.data, client={"name": "John"}, agenda=self.agenda
        )
        return ChatAgent(model=self.model_client, system_message=self.sys_prompt)

    def create_agenda(self):
        #         agenda_pt = """Before the conversation, you should prepare an agenda for the current session.
        # For instance, the agenda for the first session is usually to get to know the client, their background, and their current issues.
        #         """
        # res = self.agent.step(agenda_pt, response_format=Agenda)
        # self.agenda = parse_json_response(res.msgs[0].content)
        self.agenda = {
            "goals": [
                "Establish rapport with John",
                "Understand John's current issues and concerns",
                "Gather information about John's background and personal experiences",
            ],
            "topics": [
                "John's recent situation and behavior",
                "Personal background",
                "Past experiences affecting current concerns",
            ],
        }
        self.agent = self.create_agent()  # Recreate agent with updated agenda

    def generate_response(self, msg: str):
        res = self.agent.step(msg, response_format=BaseTherapistResponse)
        return parse_json_response(res.msgs[0].content)

    def create_summary(self):
        summary_pt = """Generate a summary of the session and next steps based on the conversation history."""
        res = self.agent.step(summary_pt, response_format=BaseTherapistResponse)
        return parse_json_response(res.msgs[0].content)

    def reset(self):
        self.agent.reset()

    # def set_sys_prompt(self, mode: str):
    #     self.sys_prompt = get_prompt(self.role, self.agent_name).render(
    #         data=self.data,
    #         response_format=self.parser.get_format_instructions(),
    #         mode=mode,
    #         client={"name": "John"},
    #         agenda=self.agenda,
    #     )

    #     self.messages = [{"role": "system", "content": self.sys_prompt}]

    # def generate(self, messages):
    #     # Retry up to 3 times in case of failure
    #     for i in range(3):
    #         try:
    #             res = self.model.invoke(messages)
    #             res = parse_json_response(res.content)
    #             print(res)
    #             return res
    #         except Exception as e:
    #             print(f"Error generating response: {e}")
    #             sleep(2)
    #     return {}

    # def generate_agenda(self):
    #     self.parser = PydanticOutputParser(pydantic_object=Agenda)
    #     self.set_sys_prompt(mode="agenda")
    #     self.agenda = self.generate(self.messages)
    #     return self.agenda

    # def generate_response(self, chat_history):
    #     self.parser = PydanticOutputParser(pydantic_object=BaseTherapistResponse)
    #     self.set_sys_prompt(mode="conversation")
    #     print("Generating Response", self.sys_prompt)

    #     msg = f"Generate your response for the next turn:\n\n{chat_history}\n\n"
    #     messages = self.messages + [{"role": "user", "content": msg}]

    #     res = self.generate(messages)

    #     self.client_mental_state = res["client_mental_state"]
    #     response = res["response"]
    #     reasoning = res["reasoning"]

    #     return response

    # def reset_agent(self):
    #     self.__init__(self.model, self.data)
    #     self.sys_prompt = ""
