import json
from typing import Dict, List
from pydantic import BaseModel, Field

from src.agents import InferenceAgent
from src.utils import load_prompts, load_json, get_model_client

from omegaconf import DictConfig
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


class Response(BaseModel):
    content: str = Field(
        description="The content of your generated response in this turn",
    )


class PsycheClient(InferenceAgent):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        all_cases = load_json(configs.data_path)
        self.data = all_cases[-1]
        self.name = "PSYCHE-SP"

        self.model_client = get_model_client(configs)
        self.prompts = load_prompts(
            role="client", agent_type="psyche", lang=configs.lang
        )

        mfc_json = json.dumps(self.data, ensure_ascii=False, indent=2)
        system_content = self.prompts["PSYCHE_SP_prompt"].render(data={"mfc": mfc_json})
        self.messages = [SystemMessage(content=system_content)]

    def generate(self, messages: List[str], response_format: BaseModel):
        model_client = self.model_client.with_structured_output(response_format)
        res = model_client.invoke(messages)
        return res

    def set_therapist(self, therapist, prev_sessions: List[Dict[str, str] | None] = []):
        self.therapist = therapist.get("name", "Therapist")

    def generate_response(self, msg: str):
        self.messages.append(HumanMessage(content=msg))
        res = self.generate(self.messages, response_format=Response)
        self.messages.append(AIMessage(content=res.model_dump_json()))

        return res

    def reset(self):
        self.therapist = None
        mfc_json = json.dumps(self.data, ensure_ascii=False, indent=2)
        system_content = self.prompts["PSYCHE_SP_prompt"].render(data={"mfc": mfc_json})
        self.messages = [SystemMessage(content=system_content)]
