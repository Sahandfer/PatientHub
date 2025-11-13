from agents import BaseAgent
from pydantic import BaseModel, Field
from typing import Dict, List, Any
from langchain_core.messages import AIMessage, HumanMessage


class UserResponse(BaseModel):
    content: str = Field(description="The content of user input")


class UserTherapist(BaseAgent):
    def __init__(self, data: Dict[str, Any]):
        self.role = "therapist"
        self.agent_type = "user"
        self.name = data["name"]
        self.data = data
        self.messages = []

    def set_client(self, client, prev_sessions: List[Dict[str, str] | None] = []):
        self.client = client["name"]

    def generate(self, messages: List[str], response_format: BaseModel = UserResponse):
        res = input("Your response: ")
        return response_format(content=res)

    def generate_response(self, msg: str):
        self.messages.append(HumanMessage(content=msg))
        res = self.generate(messages=self.messages, response_format=UserResponse)
        self.messages.append(AIMessage(content=res.model_dump_json()))

        return res

    def reset(self):
        self.agent.reset()
