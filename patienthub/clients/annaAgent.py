import random
from typing import List, Literal, Dict
from dataclasses import dataclass
from pydantic import BaseModel, Field

from patienthub.base import ChatAgent
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, load_json, get_chat_model

from omegaconf import DictConfig
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


@dataclass
class AnnaAgentClientConfig(APIModelConfig):
    """
    Configuration for the AnnaAgentClient agent.
    """

    agent_type: str = "annaAgent"
    data_path: str = "data/characters/AnnaAgent.json"
    data_idx: int = 0


# ==================== Constants ====================

EMOTION_TYPES = Literal[
    "admiration",
    "amusement",
    "anger",
    "annoyance",
    "approval",
    "caring",
    "confusion",
    "curiosity",
    "desire",
    "disappointment",
    "disapproval",
    "disgust",
    "embarrassment",
    "excitement",
    "fear",
    "gratitude",
    "grief",
    "joy",
    "love",
    "nervousness",
    "optimism",
    "pride",
    "realization",
    "relief",
    "remorse",
    "sadness",
    "surprise",
    "neutral",
]

EMOTION_CATEGORIES = {
    "Positive": [
        "admiration",
        "amusement",
        "approval",
        "caring",
        "curiosity",
        "desire",
        "excitement",
        "gratitude",
        "joy",
        "love",
        "optimism",
        "pride",
        "realization",
        "relief",
        "surprise",
    ],
    "Neutral": ["neutral"],
    "Ambiguous": ["confusion", "disappointment", "nervousness"],
    "Negative": [
        "anger",
        "annoyance",
        "disapproval",
        "disgust",
        "embarrassment",
        "fear",
        "sadness",
        "remorse",
        "grief",
    ],
}

CATEGORY_DISTANCES = {
    "Positive": {"Positive": 0, "Neutral": 1, "Ambiguous": 2, "Negative": 3},
    "Neutral": {"Positive": 1, "Neutral": 0, "Ambiguous": 1, "Negative": 2},
    "Ambiguous": {"Positive": 2, "Neutral": 1, "Ambiguous": 0, "Negative": 1},
    "Negative": {"Positive": 3, "Neutral": 2, "Ambiguous": 1, "Negative": 0},
}

DISTANCE_WEIGHTS = {0: 10, 1: 5, 2: 2, 3: 1}


class Response(BaseModel):
    content: str = Field(description="The content of your generated response")


class EmotionResponse(BaseModel):
    emotion: EMOTION_TYPES = Field(
        description="The inferred emotion category, must be one of the 28 emotions defined by GoEmotions"
    )


class IsRecognizedResponse(BaseModel):
    """Response indicating whether the chief complaint has been recognized"""

    is_recognized: bool = Field(
        description="Based on the dialogue content and the cognitive change chain of the chief complaint, determine whether the patient has well recognized the current stage complaint."
    )


class IsNeedPreviousResponse(BaseModel):
    """Response indicating whether historical information is needed"""

    is_need: bool = Field(
        description="Whether the therapist's statement involves content from previous sessions"
    )


class KnowledgeResponse(BaseModel):
    """Response for retrieving historical knowledge"""

    knowledge: str = Field(
        description="Relevant information retrieved from historical conversations and scales"
    )


class AnnaAgentClient(ChatAgent):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.data = load_json(configs.data_path)[configs.data_idx]
        self.name = self.data.get("name", "client")

        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(
            role="client", agent_type="annaAgent", lang=configs.lang
        )

        self.load_data()
        self.load_sys_prompt()

    def load_data(self):
        self.profile = self.data.get("profile", {})
        self.profile_str = self.prompts["profile"].render(profile=self.profile)
        self.prev_conv = self.data.get("previous_conversations", [])
        self.report = self.data.get("report", "")
        self.conv_history = ""  # Flattened history without instructions
        self.chain_idx = 1

    def load_sys_prompt(self):
        sys_prompt = self.prompts["system_prompt"].render(
            profile=self.profile_str,
            situation=self.data.get("situation", ""),
            status=self.data.get("status", ""),
            statement="\n-".join(self.data.get("statement", [])),
            style="\n-".join(self.data.get("style", [])),
            lang=self.configs.lang,
        )
        self.messages = [SystemMessage(content=sys_prompt)]

    def set_therapist(self, therapist):
        self.therapist = therapist.get("name", "therapist")

    def generate(self, messages: List[str], response_format: BaseModel):
        chat_model = self.chat_model.with_structured_output(response_format)
        res = chat_model.invoke(messages)
        return res

    def infer_emotion(self):
        prompt = self.prompts["emotion_inference"].render(
            profile=self.profile_str, conv_history=self.conv_history
        )
        res = self.generate(
            [SystemMessage(content=prompt)],
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
        res = self.generate(
            [SystemMessage(content=prompt)], response_format=IsRecognizedResponse
        )
        if res.is_recognized:
            self.chain_idx += 1

    def is_need_previous(self, msg: str):
        prompt = self.prompts["is_need_previous"].render(utterance=msg)

        res = self.generate(
            messages=[SystemMessage(content=prompt)],
            response_format=IsNeedPreviousResponse,
        )

        return res.is_need

    def query_knowledge(self, msg: str):
        past_conv = "\n".join(
            [f"{conv['role']}: {conv['content']}" for conv in self.prev_conv]
        )
        prompt = self.prompts["query_knowledge"].render(
            utterance=msg, conversations=past_conv, report=self.report
        )

        res = self.generate(
            messages=[SystemMessage(content=prompt)], response_format=KnowledgeResponse
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

        self.messages.append(HumanMessage(content=msg + "\n" + reminder))
        self.conv_history += f"\ntherapist: {msg}\nclient: "

        # 4) Generate final response
        res = self.generate(self.messages, response_format=Response)
        self.messages.append(AIMessage(content=res.content))
        self.conv_history += res.content

        return res

    def reset(self):
        self.load_data()
        self.load_sys_prompt()
        self.therapist = None
