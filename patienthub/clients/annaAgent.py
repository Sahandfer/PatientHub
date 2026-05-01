# coding=utf-8
# Licensed under the MIT License;

"""AnnaAgent Client - Multi-session client with dynamic emotional evolution.

Paper: "Dynamic Evolution Agent System with Multi-Session Memory for Realistic
       Seeker Simulation" (ACL 2025 Findings)
       https://aclanthology.org/2025.findings-acl.1192/

AnnaAgent simulates clients with evolving emotions and multi-session memory.

1. Load profile with risk levels and complaint chains
2. Infer emotional state (28 GoEmotions categories) from therapist input
3. Check if historical context is needed for the response
4. Track progress through cognitive change chain stages
5. Generate emotionally consistent responses
"""

import random
from typing import Dict
from omegaconf import DictConfig
from dataclasses import dataclass
from pydantic import BaseModel, Field

from .base import BaseClient
from patienthub.configs import APIModelConfig
from patienthub.utils import flatten_conv
from patienthub.schemas.annaAgent import (
    EMOTION_TYPES,
    EMOTION_CATEGORIES,
    CATEGORY_DISTANCES,
    DISTANCE_WEIGHTS,
)


@dataclass
class AnnaAgentClientConfig(APIModelConfig):
    """
    Configuration for the AnnaAgentClient agent.
    """

    agent_name: str = "annaAgent"
    prompt_path: str = "data/prompts/client/annaAgent.yaml"
    data_path: str = "data/characters/AnnaAgent.json"
    data_idx: int = 0


class EmotionResponse(BaseModel):
    emotion: EMOTION_TYPES = Field(
        description="The inferred emotion category, must be one of the 28 emotions defined by GoEmotions"
    )


class IsRecognizedResponse(BaseModel):
    is_recognized: bool = Field(
        description="Based on the dialogue content and the cognitive change chain of the chief complaint, determine whether the patient has well recognized the current stage complaint."
    )


class IsNeedPreviousResponse(BaseModel):
    is_need: bool = Field(
        description="Whether the therapist's statement involves content from previous sessions"
    )


class KnowledgeResponse(BaseModel):
    knowledge: str = Field(
        description="Relevant information retrieved from historical conversations and scales"
    )


class AnnaAgentClient(BaseClient):
    def __init__(self, configs: DictConfig):
        super().__init__(configs)

    def init_session_state(self):
        self.profile = self.data.get("profile", {})
        self.profile_str = self.prompts["profile"].render(profile=self.profile)
        self.prev_conv = self.data.get("previous_conversations", [])
        self.report = self.data.get("report", "")
        self.conv_history = ""  # Flattened history without instructions
        self.chain_idx = 1

    def build_sys_prompt(self):
        self.init_session_state()
        sys_prompt = self.prompts["system_prompt"].render(
            profile=self.profile_str,
            situation=self.data.get("situation", ""),
            status=self.data.get("status", ""),
            statement="\n-".join(self.data.get("statement", [])),
            style="\n-".join(self.data.get("style", [])),
            lang=self.configs.lang,
        )
        self.messages = [{"role": "system", "content": sys_prompt}]

    def infer_emotion(self):
        prompt = self.prompts["emotion_inference"].render(
            profile=self.profile_str, conv_history=self.conv_history
        )
        res = self.chat_model.generate(
            [{"role": "system", "content": prompt}],
            response_format=EmotionResponse,
        )

        return res.emotion

    def get_emotion_weights(self, emotion_category: str):
        probabilities = {}
        total_weight = 0

        for category, emotions in EMOTION_CATEGORIES.items():
            distance = CATEGORY_DISTANCES[emotion_category][category]
            weight = DISTANCE_WEIGHTS.get(distance, 0)
            for emotion in emotions:
                if emotion != emotion_category:
                    probabilities[emotion] = weight
                    total_weight += weight

        return probabilities, total_weight

    def perturb_emotion(self, emotion: str):

        emotion_category = "Neutral"
        for category, emotions in EMOTION_CATEGORIES.items():
            if emotion in emotions:
                emotion_category = category
                break

        probabilities, total_weight = self.get_emotion_weights(emotion_category)

        if total_weight == 0:
            return emotion_category

        emotions = list(probabilities.keys())
        weights = [probabilities[e] / total_weight for e in emotions]

        return random.choices(emotions, weights=weights, k=1)[0]

    def emotion_modulation(self, emotion: str):
        if random.randint(0, 100) > 90:
            return self.perturb_emotion(emotion)
        return emotion

    def switch_complaint(self, transformed_chain: Dict[str, str]):
        prompt = self.prompts["complaint_switch"].render(
            conv_history=self.conv_history,
            transformed_chain=transformed_chain,
            current_stage_content=transformed_chain.get(self.chain_idx, ""),
        )
        res = self.chat_model.generate(
            [{"role": "system", "content": prompt}],
            response_format=IsRecognizedResponse,
        )
        if res.is_recognized:
            self.chain_idx += 1

    def is_need_previous(self, msg: str):
        prompt = self.prompts["is_need_previous"].render(utterance=msg)

        res = self.chat_model.generate(
            messages=[{"role": "system", "content": prompt}],
            response_format=IsNeedPreviousResponse,
        )

        return res.is_need

    def query_knowledge(self, msg: str):
        past_conv = flatten_conv(self.prev_conv)
        prompt = self.prompts["query_knowledge"].render(
            utterance=msg, conversations=past_conv, report=self.report
        )

        res = self.chat_model.generate(
            messages=[{"role": "system", "content": prompt}],
            response_format=KnowledgeResponse,
        )

        return res.knowledge

    def generate_response(self, msg: str):
        # 1) Infer emotions
        emotion = self.infer_emotion()
        emotion = self.emotion_modulation(emotion)

        # 2) Generate chain of complaint change
        transformed_chain = {
            node["stage"]: node["content"]
            for node in self.data.get("complaint_chain", [])
        }
        self.switch_complaint(transformed_chain)
        if transformed_chain and self.chain_idx in transformed_chain:
            complaint = transformed_chain[self.chain_idx]
        elif transformed_chain:
            max_stage = max(transformed_chain.keys())
            complaint = transformed_chain[max_stage]
        else:
            complaint = "I don't have any particular complaints right now."

        # 3) Check if previous messages exist
        need_previous = self.is_need_previous(msg)
        sup_information = "" if not need_previous else self.query_knowledge(msg)
        reminder = self.prompts["reminder"].render(
            emotion=emotion, complaint=complaint, sup_information=sup_information
        )

        self.messages.append({"role": "user", "content": msg + "\n" + reminder})
        self.conv_history += f"\ntherapist: {msg}\nclient: "

        # 4) Generate final response
        res = self.chat_model.generate(self.messages)
        self.messages.append({"role": "assistant", "content": res.content})
        self.conv_history += res.content

        return res
