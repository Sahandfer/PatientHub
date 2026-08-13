import logging
from typing import Literal
from omegaconf import DictConfig
from dataclasses import dataclass
from pydantic import BaseModel, Field

from .base import BaseClient
from patienthub.configs import APIModelConfig
from patienthub.utils import flatten_conv
from patienthub.schemas.patientAct import (
    REACTIONS,
    BEHAVIORS,
    RESISTANCE_PATTERNS,
    TRUST_DELTAS,
)

logger = logging.getLogger(__name__)


@dataclass
class PatientActClientConfig(APIModelConfig):
    """Configuration for the PatientActClient agent."""

    agent_name: str = "patientAct"
    prompt_path: str = "data/prompts/client/patientAct.yaml"
    data_path: str = "data/characters/patientAct.json"
    data_idx: int = 0
    use_memory: bool = True
    use_pipeline: bool = True
    use_trust_gating: bool = True


def tag_item(field_path: str, content: str) -> str:
    """Tag a retrieved item based on its field_path
    so the reaction prompt can distinguish item types."""
    if "triggers" in field_path:
        return f"[trigger] {content}"
    elif "intermediate_beliefs" in field_path:
        return f"[belief] {content}"
    elif "automatic_thoughts" in field_path:
        return f"[thought] {content}"
    elif "perpetuating_factors" in field_path:
        return f"[pattern] {content}"
    elif "interpersonal_patterns" in field_path:
        return f"[relational pattern] {content}"
    elif "impact" in field_path:
        return f"[symptom] {content}"
    elif "predisposing_factors" in field_path:
        return f"[memory] {content}"
    return content


def has_triggers(tagged_items: list[str]) -> bool:
    """Check if any retrieved items are triggers."""
    return any(item.startswith("[trigger]") for item in tagged_items)


# ── Response Format Schemas ───────────────────────────────────────────────


class TopicExtraction(BaseModel):
    topics: list[str] = Field(
        ...,
        description="Topics from the therapist's utterance that match available activation tags.",
    )


class RetrievedContext(BaseModel):
    topics: list[str] = Field(...)
    items: list[str] = Field(
        default_factory=list,
        description="Retrieved items that passed the trust gate.",
    )
    has_triggers: bool = Field(default=False)
    blocked: list[str] = Field(
        default_factory=list,
        description="Items that matched topics but trust is insufficient and generates_discomfort=true.",
    )


class Reaction(BaseModel):
    reasoning: str = Field(
        ..., description="The reasoning behind the identified reaction."
    )
    reaction: Literal[tuple(REACTIONS.keys())] = Field(
        ...,
        description="The emotional reaction of the client.",
    )
    intensity: Literal["low", "moderate", "high"] = Field(
        ...,
        description="Low=mild, passing. Moderate=noticeable. High=strong, may trigger resistance.",
    )


class Behavior(BaseModel):
    reasoning: str = Field(..., description="The reasoning behind the chosen behavior.")
    behavior: Literal[tuple(BEHAVIORS.keys())] = Field(
        ...,
        description="The chosen behavior of the client.",
    )


class ResistancePattern(BaseModel):
    reasoning: str = Field(..., description="Why this specific form of resistance.")
    pattern: Literal[tuple(RESISTANCE_PATTERNS.keys())] = Field(
        ..., description="The specific resistance pattern."
    )


class TrustUpdate(BaseModel):
    reasoning: str = Field(
        ...,
        description="Brief reasoning for how the therapist's approach affected trust.",
    )
    direction: Literal[
        "increased_significantly",
        "increased_slightly",
        "unchanged",
        "decreased_slightly",
        "decreased_significantly",
    ] = Field(..., description="How the client's trust shifted after this exchange.")


class Response(BaseModel):
    reasoning: str = Field(
        ..., description="The reasoning/planning behind the client's next response."
    )
    content: str = Field(
        ..., description="The client's response to the therapist's latest message."
    )


class PatientActClient(BaseClient):
    def __init__(self, configs: DictConfig):
        super().__init__(configs)

    def build_sys_prompt(self):
        self.profile = self.data["profile"]
        self.memory = self.data["memory"]
        self.seed = self.data["seed"]
        self.trust_level: float = 2.5

        # Per-session state — reset here so a reused client (via reset()) does
        # not carry a previous session's behaviors/reactions into the next one.
        self.reaction: str | None = None
        self.reaction_intensity: str | None = None
        self.behavior: str | None = None
        self.recent_behaviors: list[str] = []
        self.resistance_pattern: str | None = None

        sys_prompt = self.prompts[
            "sys_prompt" + ("" if self.configs.use_memory else "_no_memory")
        ].render(profile=self.profile)
        self.messages = [{"role": "system", "content": sys_prompt}]

    def all_activation_tags(self) -> list[str]:
        """Collect all unique activation tags from memory items."""
        tags = set()
        for item in self.memory["items"]:
            tags.update(item["activation_tags"])
        return sorted(tags)

    def retrieve_context(self, topics: list[str]) -> RetrievedContext:
        """Match topics against activation tags, trust-gate items."""
        topic_set = {t.lower() for t in topics}
        retrieved = []
        blocked = []

        for item in self.memory["items"]:
            tags = {t.lower() for t in item["activation_tags"]}
            if tags & topic_set:
                if self.configs.use_trust_gating:
                    if self.trust_level >= item["disclosure_level"]:
                        tagged = tag_item(item["field_path"], item["content"])
                        retrieved.append(tagged)
                    elif item.get("generates_discomfort", False):
                        blocked.append(item["content"])
                else:
                    tagged = tag_item(item["field_path"], item["content"])
                    retrieved.append(tagged)

        return RetrievedContext(
            topics=topics,
            items=retrieved,
            has_triggers=has_triggers(retrieved),
            blocked=blocked,
        )

    def analyze_and_retrieve(self, conv_history: str) -> RetrievedContext:
        """Extract topics then retrieve relevant memory items."""
        if self.configs.use_memory:
            topic_prompt = self.prompts["topic_extraction"].render(
                msg=self.messages[-1]["content"],
                activation_tags=self.all_activation_tags(),
            )
            result = self.chat_model.generate(
                [{"role": "system", "content": topic_prompt}],
                response_format=TopicExtraction,
            )
            return self.retrieve_context(result.topics)
        else:
            return RetrievedContext(topics=[], items=[], has_triggers=False, blocked=[])

    def get_reaction(self, conv_history: str, context: RetrievedContext) -> Reaction:
        prompt = self.prompts["reaction"].render(
            reactions=REACTIONS,
            conv_history=conv_history,
            retrieved_context=context,
            prev_reaction=self.reaction,
            has_activated_content=bool(context.items or context.blocked),
        )
        return self.chat_model.generate(
            [{"role": "system", "content": prompt}],
            response_format=Reaction,
        )

    def get_behavior(self, conv_history: str, context: RetrievedContext) -> Behavior:
        prompt = self.prompts["behavior"].render(
            behaviors=BEHAVIORS,
            conv_history=conv_history,
            coping_patterns=self.profile["psychological_formulation"][
                "coping_patterns"
            ],
            current_reaction=self.reaction,
            current_reaction_desc=REACTIONS.get(self.reaction, ""),
            current_intensity=self.reaction_intensity,
            recent_behaviors=self.recent_behaviors[-3:],
            trust_level=self.trust_level,
            has_blocked_content=bool(context.blocked),
        )
        return self.chat_model.generate(
            [{"role": "system", "content": prompt}],
            response_format=Behavior,
        )

    def get_resistance_pattern(
        self, conv_history: str, context: RetrievedContext
    ) -> ResistancePattern:
        prompt = self.prompts["resistance_pattern"].render(
            resistance_patterns=RESISTANCE_PATTERNS,
            conv_history=conv_history,
            retrieved_context=context,
            coping_patterns=self.profile["psychological_formulation"][
                "coping_patterns"
            ],
            current_reaction=self.reaction,
            current_intensity=self.reaction_intensity,
            trust_level=self.trust_level,
        )
        return self.chat_model.generate(
            [{"role": "system", "content": prompt}],
            response_format=ResistancePattern,
        )

    def update_trust(self, conv_history: str) -> TrustUpdate:
        patterns = self.profile["psychological_formulation"]["interpersonal_patterns"]
        therapist_pattern = next(
            (p for p in patterns if p["domain"].lower() == "the therapist"),
            None,
        )
        trust_prompt = self.prompts["trust_update"].render(
            attachment_style=self.seed["attachment_style"],
            conv_history=conv_history,
            current_trust=self.trust_level,
            therapist_ro=(
                therapist_pattern["response_of_other"]
                if therapist_pattern
                else "unknown"
            ),
        )
        result = self.chat_model.generate(
            [{"role": "system", "content": trust_prompt}],
            response_format=TrustUpdate,
        )
        delta = TRUST_DELTAS.get(result.direction, 0.0)
        self.trust_level = max(1.0, min(4.0, self.trust_level + delta))
        logger.info(
            f"Trust update: {result.direction} ({delta:+.2f}) "
            f"→ {self.trust_level:.2f} ({result.reasoning})"
        )
        return result

    def generate_response(self, msg: str):
        self.messages.append({"role": "user", "content": msg})
        conv_history = flatten_conv(
            self.messages, roles={"user": "Therapist", "assistant": "Client"}
        )

        # 1) Retrieve relevant memory items
        context = self.analyze_and_retrieve(conv_history)
        logger.info(
            f"Retrieved: {len(context.items)} items, " f"{len(context.blocked)} blocked"
        )

        conv_with_signal = [m.copy() for m in self.messages]
        if self.configs.use_pipeline:
            # 2) Determine reaction
            reaction = self.get_reaction(conv_history, context)
            self.reaction = reaction.reaction
            self.reaction_intensity = reaction.intensity
            logger.info(
                f"Reaction: {self.reaction} (intensity={self.reaction_intensity}, "
                f"reasoning={reaction.reasoning})"
            )

            # 3) Select behavior
            behavior = self.get_behavior(conv_history, context)
            self.behavior = behavior.behavior
            self.recent_behaviors.append(self.behavior)
            self.resistance_pattern = None
            logger.info(f"Behavior: {self.behavior} — {behavior.reasoning}")

            # 4) Resistance pattern (only if behavior is resistance)
            if self.behavior == "resistance":
                resistance = self.get_resistance_pattern(conv_history, context)
                self.resistance_pattern = resistance.pattern
                logger.info(
                    f"Resistance: {self.resistance_pattern} — {resistance.reasoning}"
                )

            conv_with_signal[-1]["content"] += "\n" + self.prompts[
                "signal_prompt"
            ].render(
                reaction=self.reaction,
                reaction_desc=REACTIONS.get(self.reaction, ""),
                intensity=self.reaction_intensity,
                behavior=self.behavior,
                behavior_desc=BEHAVIORS.get(self.behavior, ""),
                resistance_pattern=self.resistance_pattern,
                resistance_desc=RESISTANCE_PATTERNS.get(self.resistance_pattern, ""),
                context=context,
            )
        else:
            # Directly append retrieved context to the message for the model to use
            context_block = ""
            if context.items:
                context_block += "\n<context>\nAvailable information about you:\n"
                for item in context.items:
                    context_block += f"- {item}\n"
                context_block += "</context>"

            if context.blocked:
                context_block += (
                    "\n<sensitive>\n"
                    "The topic approaches content you are NOT ready to share. "
                    "Respond naturally without disclosing this content.\n"
                    "</sensitive>"
                )

            if context_block:
                conv_with_signal[-1]["content"] += context_block

        # 5) Response generation
        res = self.chat_model.generate(conv_with_signal, response_format=Response)
        logger.info(f"Response reasoning: {res.reasoning}")
        self.messages.append({"role": "assistant", "content": res.content})

        # 6) Trust update
        self.update_trust(conv_history)

        return res
