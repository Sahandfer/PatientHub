from agents import BaseAgent
from utils import load_prompts
from typing import Dict, List, Any
from pydantic import BaseModel, Field
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


class Response(BaseModel):
    content: str = Field(
        description="The content of your generated response in this turn",
    )


class THUClient(BaseAgent):
    def __init__(
        self,
        model_client: BaseChatModel,
        data: Dict[str, Any],
        lang: str = "en",
        difficulty: str = "moderate",  # reserved
    ):
        self.role = "client"
        self.agent_type = "thuClient"
        self.lang = lang
        self.name = data["demographics"]["name"]
        self.model_client = model_client
        self.data = data
        self.prompts = load_prompts(
            role=self.role, agent_type=self.agent_type, lang=self.lang
        )
        self.messages = [
            SystemMessage(
                content=self.prompts["prompt"].render(
                    data=self.data, difficulty=difficulty, lang="Chinese (中文)"
                )
            )
        ]

    def generate(self, messages: List[str], response_format: BaseModel):
        model_client = self.model_client.with_structured_output(response_format)
        res = model_client.invoke(messages)
        return res

    def set_therapist(self, therapist, prev_sessions: List[Dict[str, str] | None] = []):
        self.therapist = therapist["name"]

    def generate_response(self, msg: str):
        self.messages.append(HumanMessage(content=msg))
        res = self.generate(self.messages, response_format=Response)
        self.messages.append(AIMessage(content=res.model_dump_json()))

        return res

    def reset(self):
        self.messages = []
        self.therapist = None
