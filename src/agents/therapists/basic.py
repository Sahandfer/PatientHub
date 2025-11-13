from agents import BaseAgent
from pydantic import BaseModel, Field
from utils import load_prompts
from typing import Dict, List, Any
from brain import MentalState
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


class Agenda(BaseModel):
    topics: List[str] = Field(
        description="List of topics to discuss in the session (1-3)",
        default_factory=list,
    )
    goals: List[str] = Field(
        description="Goals for the session (1-3)", default_factory=list
    )


class BaseTherapistResponse(BaseModel):
    client_mental_state: MentalState = Field(
        description="The Client's current mental state"
    )
    reasoning: str = Field(
        description="Your reasoning about the how you should approach the client in this turn (2-4 sentences)"
    )
    content: str = Field(
        description="The content of your generated response based on the client's mental state and your reasoning (1-2 sentences)"
    )


class SessionSummary(BaseModel):
    summary: str = Field(
        description="A summary of the session, including key points discussed and next steps (1-3 sentences)"
    )
    homework: str = Field(
        description="Next steps for the client, including homework or follow-up actions (1-3 items)"
    )


class BasicTherapist(BaseAgent):
    def __init__(
        self, model_client: BaseChatModel, data: Dict[str, Any], lang: str = "en"
    ):
        self.role = "therapist"
        self.agent_type = "basic"
        self.model_client = model_client
        self.name = data["demographics"]["name"]
        self.data = data
        self.prompts = load_prompts(
            role=self.role, agent_type=self.agent_type, lang=self.lang
        )
        self.client_mental_state = MentalState()
        self.agenda = Agenda()
        self.messages = [
            SystemMessage(content=self.prompts["profile"].render(data=self.data))
        ]

    def generate(self, messages: List[str], response_format: BaseModel):
        model_client = self.model_client.with_structured_output(response_format)
        res = model_client.invoke(messages)
        return res

    def set_client(self, client, prev_sessions: List[Dict[str, str] | None] = []):
        self.client = client.data["demographics"]
        self.messages[0].content += "\n" + self.prompts["client"].render(
            client=self.client, previous_sessions=prev_sessions
        )

    def generate_agenda(self):
        # pt = self.prompts["agenda"].render()
        # agenda = self.generate(
        #     messages=self.messages + [{"role": "user", "content": pt}],
        #     response_format=Agenda,
        # )
        agenda = Agenda(
            topics=[
                "John's personal and professional background",
                "Current challenges and reasons for seeking therapy",
                "John's goals and expectations for therapy",
            ],
            goals=[
                "Establish rapport with John Doe",
                "Understand John's background and current issues",
                "Identify initial areas of focus for therapy",
            ],
        )
        self.messages[0].content += "\n" + self.prompts["conversation"].render(
            data=self.data, agenda=agenda, client=self.client
        )
        return agenda.model_dump(mode="json")

    def generate_response(self, msg: str):
        self.messages.append(HumanMessage(content=msg))
        res = self.generate(
            messages=self.messages, response_format=BaseTherapistResponse
        )
        self.messages.append(AIMessage(content=res.model_dump_json()))

        return res

    def generate_summary(self):
        pt = self.prompts["summary"].render()
        summary = self.generate(
            messages=self.messages + [HumanMessage(content=pt)],
            response_format=SessionSummary,
        )
        return summary

    def reset(self):
        self.agent.reset()
