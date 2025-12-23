from dataclasses import dataclass
from typing import Dict, List
from pydantic import BaseModel, Field

from patienthub.base import ChatAgent
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, get_chat_model

from omegaconf import DictConfig


@dataclass
class ConvEvaluatorConfig(APIModelConfig):
    """Configuration for Conversation Evaluator."""

    agent_type: str = "client"
    eval_type: str = "conv"
    temperature: float = 0.4
    input_dir: str = ""
    output_dir: str = ""


class ConsistencyDimension(BaseModel):
    score: int = Field(
        ...,
        description="Score for this aspect on a scale from 1 to 10",
    )
    comments: str = Field(
        ...,
        description="Comments regarding this aspect of evaluation",
    )


class Consistency(BaseModel):
    profile_factual: ConsistencyDimension = Field(
        ...,
        description="Factual consistency with the character profile",
    )
    conv_factual: ConsistencyDimension = Field(
        ...,
        description="Factual consistency within the conversation history",
    )
    behavioral: ConsistencyDimension = Field(
        ...,
        description="Behavioral consistency between the character profile and their responses in the conversation",
    )
    emotional: ConsistencyDimension = Field(
        ...,
        description="Emotional consistency between the character profile and their responses in the conversation",
    )


class ResistanceDimension(BaseModel):
    score: int = Field(
        ...,
        description="Score for this aspect on a scale from 1 to 10",
    )
    realism: int = Field(
        ...,
        description="Compared to a human client, how realistic is the client's performance on this aspect on a scale from 1 to 10",
    )
    comments: str = Field(
        ...,
        description="Comments regarding this aspect of evaluation",
    )


class Resistance(BaseModel):
    engagement: ResistanceDimension = Field(
        ...,
        description="Client's willingness to share information from their profile (e.g., gradual vs. immediate disclosure).",
    )
    agreeableness: ResistanceDimension = Field(
        ...,
        description="Client's agreeableness with/reception of the therapist's suggestions (e.g., reluctance to adopt coping strategies).",
    )
    self_curing: ResistanceDimension = Field(
        ...,
        description="Client's tendency to self-cure without therapist intervention (e.g., downplaying issues) or rushing to find a solution to their problem (e.g., avoidance of deep exploration).",
    )


class PedagogicalDimension(BaseModel):
    score: int = Field(
        ...,
        description="Score for this aspect on a scale from 1 to 10",
    )
    realism: int = Field(
        ...,
        description="Compared to a human simulated patient (human SP), how realistic is the client's performance on this aspect on a scale from 1 to 10",
    )
    comments: str = Field(
        ...,
        description="Comments regarding this aspect of evaluation",
    )


class PedagogicalValue(BaseModel):
    displayed_cues: PedagogicalDimension = Field(
        ...,
        description="The extent to which the client displays symptoms and cues from their profile (e.g., emotional expressions, behavioral patterns).",
    )
    feedback_usefulness: PedagogicalDimension = Field(
        ...,
        description="Usefulness of the client's feedback to the therapist for improving their skills (e.g., clarity, relevance).",
    )


class EmotionalDimension(BaseModel):
    score: int = Field(
        ...,
        description="Score for this aspect on a scale from 1 to 10",
    )
    realism: int = Field(
        ...,
        description="Compared to a human simulated patient (human SP), how realistic is the client's performance on this aspect on a scale from 1 to 10",
    )
    comments: str = Field(
        ...,
        description="Comments regarding this aspect of evaluation",
    )


class Feedback(BaseModel):
    consisteny: Consistency = Field(
        ...,
        description="Evaluation of the client's consistency",
    )
    resistance: Resistance = Field(
        ...,
        description="Evaluation of the client's resistance behaviors",
    )
    pedagogical_value: PedagogicalValue = Field(
        ...,
        description="Evaluation of the client's pedagogical value",
    )
    emotional_depth: EmotionalDimension = Field(
        ...,
        description="Evaluation of the client's emotional depth. Does the client deeply describe their emotions and their impact on their life or are they simply stating surface-level feelings?",
    )
    total_score: int = Field(
        ...,
        description="Overall score for the client's performance in this session (1-10)",
    )


class TurnLevelFeedback(BaseModel):
    reasoning: str = Field(
        ...,
        description="Reasoning behind the evaluation of this turn",
    )
    inconsistencies: List[str] = Field(
        ...,
        description="A list of items in the response that are inconsistent with the profile",
    )
    consistency: int = Field(
        ...,
        description="Evaluation of the client's consistency with the profile in this turn (1-10)",
    )
    resistance: int = Field(
        ...,
        description="Evaluation of the client's engagement with the therapist in this turn (1-10)",
    )
    pedagogical_value: int = Field(
        ...,
        description="Evaluation of the client's pedagogical value in this turn (1-10)",
    )
    emotional_depth: int = Field(
        ...,
        description="Evaluation of the client's emotional depth in this turn (1-10)",
    )
    total_score: int = Field(
        ...,
        description="Overall score for the client's performance in this turn (1-10)",
    )


class ConvEvaluator(ChatAgent):
    def __init__(self, configs: DictConfig):
        self.configs = configs
        self.chat_model = get_chat_model(configs)
        self.prompt = load_prompts(
            role="evaluator/client", agent_type="conv", lang=configs.lang
        )

    def generate(self, prompt, response_format=None):
        if response_format:
            chat_model = self.chat_model.with_structured_output(response_format)
            res = chat_model.invoke(prompt)
        else:
            res = self.chat_model.invoke(prompt)

        return res

    def evaluate(self, data: Dict):

        # Overall
        # self.prompt = self.prompt["prompt"].render(
        #     conv_history="\n".join(
        #         [f"{msg['role']}: {msg['content']}" for msg in data["messages"]]
        #     ),
        #     profile=data["profile"],
        # )
        # res = self.generate(Feedback).model_dump()

        # Aspect based
        # res = {}
        # for feedback in [Consistency, Resistance, PedagogicalValue, EmotionalDimension]:
        #     aspect_res = self.generate(feedback)
        #     res[feedback.__name__.lower()] = aspect_res.model_dump()

        res = {}
        for i in range(1, len(data["messages"]), 2):
            conv_history = data["messages"][0:i]
            prompt = self.prompt["relevant_info"].render(
                conv_history="\n".join(
                    [f"{msg['role']}: {msg['content']}" for msg in conv_history]
                ),
                profile=data["profile"],
                response=data["messages"][i]["content"],
            )
            relevant_info = self.generate(prompt)

            prompt = self.prompt["prompt_turn"].render(
                conv_history="\n".join(
                    [f"{msg['role']}: {msg['content']}" for msg in conv_history]
                ),
                profile=relevant_info,
                response=data["messages"][i]["content"],
            )
            turn_res = self.generate(prompt, TurnLevelFeedback).model_dump()
            res[i] = turn_res
            print(prompt)
            print(turn_res)
            break

        return res

    def reset(self):
        self.prompt = load_prompts(
            role="evaluator/client", agent_type="conv", lang="en"
        )["prompt"]
