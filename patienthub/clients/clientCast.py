from dataclasses import dataclass
from typing import Dict, List
from pydantic import BaseModel, Field

from patienthub.base import ChatAgent
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, load_json, get_chat_model

from omegaconf import DictConfig
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


@dataclass
class ClientCastClientConfig(APIModelConfig):
    """Configuration for ClientCast client agent."""

    agent_type: str = "clientCast"
    data_path: str = "data/characters/ClientCast.json"
    conv_path: str = "data/resources/ClientCast/human_data.json"
    symptoms_path: str = "data/resources/ClientCast/symptoms.json"
    data_idx: int = 0
    conv_id: int = 0


class Response(BaseModel):
    content: str = Field(
        description="The content of your generated response in this turn",
    )


class ClientCastClient(ChatAgent):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.data = load_json(configs.data_path)[configs.data_idx]
        self.conv = load_json(configs.conv_path)[configs.conv_id]["messages"]
        self.symptoms = load_json(configs.symptoms_path)
        self.name = self.data.get("name", "client")

        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(
            role="client", agent_type="clientCast", lang=configs.lang
        )
        self.messages = self.render_sys_prompt()

    def get_case_synopsis(self):
        profile = self.data.get("basic_profile", {})
        case_synopsis = ""
        for key, value in profile.items():
            if key != "reasons":
                case_synopsis += f"- {key}: {value}\n"
        return case_synopsis, profile.get("reasons", "")

    def get_symptoms(self):
        client_symptoms = self.data.get("symptoms", {})
        symptom_res = ""
        for disorder, questions in client_symptoms.items():
            disorder_qs = self.symptoms.get(disorder, [])
            for q_id, details in questions.items():
                if details.get("identified", False):
                    disorder_q = disorder_qs[int(q_id)]
                    symptom_res += f"- {disorder_q['question']}: {details.get('severity_label', '')}\n"
        return symptom_res

    def get_appreance(self):
        personality = self.data.get("big_five", {})
        res = ""
        for trait, details in personality.items():
            res += f"- {trait}: {details.get('explanation', '')}\n"
        return res

    def render_conv(self):
        return "\n".join(
            [
                f"{ turn.get('role').capitalize()}: {turn.get('content')}\n"
                for turn in self.conv
            ]
        )

    def render_sys_prompt(self):
        case_synopsis, reasons = self.get_case_synopsis()
        symptoms = self.get_symptoms()
        appearance = self.get_appreance()
        conversation = self.render_conv()
        system_prompt = self.prompts["simulation"].render(
            case_synopsis=case_synopsis,
            reasons_for_visit=reasons,
            symptoms=symptoms,
            appearance=appearance,
            conversation=conversation,
        )
        return [SystemMessage(content=system_prompt)]

    def generate(self, messages: List[str], response_format: BaseModel):
        chat_model = self.chat_model.with_structured_output(response_format)
        res = chat_model.invoke(messages)
        return res

    def set_therapist(self, therapist, prev_sessions: List[Dict[str, str] | None] = []):
        self.therapist = therapist.get("name", "therapist")

    def generate_response(self, msg: str):
        self.messages.append(HumanMessage(content=msg))
        res = self.generate(self.messages, response_format=Response)
        self.messages.append(AIMessage(content=res.content))

        return res

    def reset(self):
        self.messages = self.render_sys_prompt()
        self.therapist = None
