from dataclasses import dataclass
from typing import Dict, List
from patienthub.brain import MentalState
from patienthub.utils import load_prompts, load_json, get_chat_model
from patienthub.base import ChatAgent
from patienthub.configs import APIModelConfig
from pydantic import BaseModel, Field

from omegaconf import DictConfig
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


@dataclass
class BasicTherapistConfig(APIModelConfig):
    """Configuration for BasicTherapist agent."""

    agent_type: str = "basic"
    data_path: str = "data/characters/therapists.json"
    data_idx: int = 0


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


class BasicTherapist(ChatAgent):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.data = load_json(configs.data_path)[configs.data_idx]
        self.name = self.data["demographics"]["name"]

        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(
            role="therapist", agent_type="basic", lang=configs.lang
        )
        self.client_mental_state = MentalState()
        self.agenda = Agenda()
        self.messages = [
            SystemMessage(content=self.prompts["profile"].render(data=self.data))
        ]

    def generate(self, messages: List[str], response_format: BaseModel):
        chat_model = self.chat_model.with_structured_output(response_format)
        res = chat_model.invoke(messages)
        return res

    def set_client(self, client, prev_sessions: List[Dict[str, str] | None] = []):
        self.client = client["name"]
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
