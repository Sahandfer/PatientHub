from omegaconf import DictConfig
from dataclasses import dataclass
from pydantic import BaseModel, Field

from .base import BaseTherapist
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, get_chat_model


class ResponseWithCOT(BaseModel):
    reasoning: str = Field(
        description="Chain-of-thought reasoning behind the therapist's response."
    )
    content: str = Field(description="Therapist's response to the patient's message.")


@dataclass
class BasicTherapistConfig(APIModelConfig):
    """Configuration for Basic Therapist agent."""

    agent_type: str = "basic"
    prompt_path: str = "data/prompts/therapist/CBT.yaml"
    use_cot: bool = False


class BasicTherapist(BaseTherapist):
    def __init__(self, configs: DictConfig):
        self.configs = configs
        self.name = "Basic Therapist"
        self.use_cot = configs.use_cot

        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(path=configs.prompt_path, lang=configs.lang)
        self.build_sys_prompt()

    def build_sys_prompt(self):
        self.messages = [{"role": "system", "content": self.prompts["system"].render()}]

    def generate_response(self, msg: str):

        self.messages.append({"role": "user", "content": msg})
        res = self.chat_model.generate(
            self.messages,
            response_format=ResponseWithCOT if self.use_cot else None,
        )
        self.messages.append({"role": "assistant", "content": res.content})

        return res

    def reset(self):
        self.build_sys_prompt()
        self.client = None
