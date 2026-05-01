# coding=utf-8
# Licensed under the MIT License;

"""ClientCast Client - Psychological profile-based client for therapist assessment.

Paper: "Towards a Client-Centered Assessment of LLM Therapists by Client Simulation"
       https://arxiv.org/pdf/2406.12266

ClientCast creates client simulations with detailed psychological profiles for
assessing LLM-based therapists. Features:

- Big Five personality traits (Openness, Conscientiousness, Extraversion, etc.)
- Validated symptom scales (PHQ-9, GAD-7, OQ-45)
- Real therapy conversation excerpts for grounding
"""

from omegaconf import DictConfig
from dataclasses import dataclass

from .base import BaseClient
from patienthub.configs import APIModelConfig
from patienthub.utils import load_json


@dataclass
class ClientCastClientConfig(APIModelConfig):
    """Configuration for ClientCast client agent."""

    agent_name: str = "clientCast"
    prompt_path: str = "data/prompts/client/clientCast.yaml"
    data_path: str = "data/characters/ClientCast.json"
    conv_path: str = "data/resources/ClientCast/human_data.json"
    symptoms_path: str = "data/resources/ClientCast/symptoms.json"
    data_idx: int = 0
    conv_id: int = 0


class ClientCastClient(BaseClient):
    def __init__(self, configs: DictConfig):
        # Load extra resources before super() so build_sys_prompt() can use them
        self.conv = load_json(configs.conv_path)[configs.conv_id]["messages"]
        self.symptoms = load_json(configs.symptoms_path)
        super().__init__(configs)

    def get_case_synopsis(self):
        case_synopsis = ""
        for key, value in self.profile.items():
            if key != "reasons":
                case_synopsis += f"- {key}: {value}\n"
        return case_synopsis, self.profile.get("reasons", "")

    def get_symptoms(self):
        client_symptoms = self.data.get("symptoms", {})
        symptom_res = ""
        for disorder, questions in client_symptoms.items():
            disorder_qs = self.symptoms.get(disorder, [])
            for q_id, details in questions.items():
                if details.get("identified", False):
                    try:
                        disorder_q = disorder_qs[int(q_id) - 1]
                    except (ValueError, IndexError):
                        continue
                    question = str(disorder_q)
                    if not question:
                        continue
                    symptom_res += (
                        f"- {question}: {details.get('severity_label', '')}\n"
                    )
        return symptom_res

    def get_appreance(self):
        personality = self.data.get("big_five", {})
        res = ""
        for trait, details in personality.items():
            res += f"- {trait}: {details.get('explanation', '')}\n"
        return res

    def build_sys_prompt(self):
        self.profile = self.data.get("basic_profile", {})
        case_synopsis, reasons = self.get_case_synopsis()
        symptoms = self.get_symptoms()
        appearance = self.get_appreance()
        conversation = "\n".join(
            [
                f"{ turn.get('role').capitalize()}: {turn.get('content')}\n"
                for turn in self.conv
            ]
        )
        sys_prompt = self.prompts["simulation"].render(
            case_synopsis=case_synopsis,
            reasons_for_visit=reasons,
            symptoms=symptoms,
            appearance=appearance,
            conversation=conversation,
        )
        self.messages = [{"role": "system", "content": sys_prompt}]

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        res = self.chat_model.generate(self.messages)
        self.messages.append({"role": "assistant", "content": res.content})

        return res
