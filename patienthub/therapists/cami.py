from typing import Dict, List, Literal, Optional
from omegaconf import DictConfig
from pydantic import BaseModel, ConfigDict, Field
from dataclasses import dataclass

from .base import BaseTherapist
from patienthub.configs import APIModelConfig
from patienthub.utils import load_prompts, load_json, get_chat_model


@dataclass
class CamiTherapistConfig(APIModelConfig):
    """Configuration for the CamiTherapist agent."""

    agent_type: str = "cami"
    prompt_path: str = "data/prompts/therapist/cami.yaml"
    topic_graph: str = "data/resources/CAMI/topic_graph.json"
    goal: str = "reducing drug use"  # client aimed at achieving
    behavior: str = "drug use"  # client's behavior (usually negative)


CamiStage = Literal["Precontemplation", "Contemplation", "Preparation"]

CamiStrategy = Literal[
    "Advise",
    "Affirm",
    "Direct",
    "Emphasize Control",
    "Facilitate",
    "Inform",
    "Closed Question",
    "Open Question",
    "Raise Concern",
    "Confront",
    "Simple Reflection",
    "Complex Reflection",
    "Reframe",
    "Support",
    "Warn",
    "Structure",
    "No Strategy",
]

CamiExplorationAction = Literal["Step Into", "Switch", "Step Out", "Stay"]


class _CamiBaseModel(BaseModel):
    model_config = ConfigDict(populate_by_name=True)


class InferStatePromptOutput(_CamiBaseModel):
    analysis: str = Field(description="Step-by-step analysis for state inference.")
    stage: CamiStage = Field(description="Inferred client stage/state.")


class SelectStrategyPromptOutput(_CamiBaseModel):
    analysis: str = Field(description="Rationale for selecting strategies.")
    strategies: List[CamiStrategy] = Field(
        description="Selected strategies for next response (no more than 2)."
    )


class InitializeTopicAnalysisPromptOutput(_CamiBaseModel):
    analysis: str = Field(description="Analysis for which topics engage the client.")


class InitializeTopicJsonPromptOutput(_CamiBaseModel):
    economy: int = Field(ge=0, le=100, alias="Economy")
    interpersonal_relationships: int = Field(
        ge=0, le=100, alias="Interpersonal Relationships"
    )
    health: int = Field(ge=0, le=100, alias="Health")
    law: int = Field(ge=0, le=100, alias="Law")
    education: int = Field(ge=0, le=100, alias="Education")


class ExplorePromptOutput(_CamiBaseModel):
    analysis: str = Field(description="Natural language analysis of engagement.")
    action: CamiExplorationAction = Field(description="Recommended exploration action.")
    topic: str = Field(description="Recommended next topic/subtopic to explore.")


class TopicStackPromptOutput(ExplorePromptOutput):
    pass


class FeedbackPromptOutput(_CamiBaseModel):
    topic_alignment_score: int = Field(ge=0, le=5, description="0-5 topic alignment.")
    topic_alignment_feedback: str = Field(description="Feedback on topic alignment.")
    strategy_adherence_score: int = Field(
        ge=0, le=5, description="0-5 strategy adherence."
    )
    strategy_adherence_feedback: str = Field(description="Feedback on strategy use.")
    total_score: Optional[int] = Field(
        default=None, ge=0, le=10, description="Optional total score (0-10)."
    )
    suggestions: List[str] = Field(
        description="Concrete recommendations to improve the response."
    )


class RefinePromptOutput(_CamiBaseModel):
    content: str = Field(description="Refined counselor response (<= 50 words).")


class ResponseSelectPromptOutput(_CamiBaseModel):
    response_id: int = Field(ge=1, description="Chosen response ID (1-indexed).")


class CamiTherapist(BaseTherapist):
    def __init__(self, configs: DictConfig):
        self.configs = configs

        self.name = "Cami"
        self.goal: str = configs.goal
        self.behavior: str = configs.behavior
        self._has_greeted: bool = False

        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(path=configs.prompt_path, lang=configs.lang)
        self.topic_graph: Dict[str, Dict[str, List[str]]] = load_json(
            configs.topic_graph
        )["topic_graph"]

        self.initialized: bool = False
        self.topic_stack: List[str] = []
        self.explored_topics: List[str] = []
        self.build_sys_prompt()

    def build_sys_prompt(self):
        sys_prompt = self.prompts["sys_prompt"].render(
            goal=self.goal,
            behavior=self.behavior,
        )
        self.messages = [{"role": "system", "content": sys_prompt}]

    def set_client(self, client, prev_sessions: List[Dict[str, str] | None] = []):
        self.client = client.get("name", "client")

    def _conv_context(self, max_turns: int = 10) -> str:
        turns = [m for m in self.messages if m.get("role") != "system"]
        turns = turns[-max_turns:]
        lines: List[str] = []
        for t in turns:
            role = t.get("role")
            content = (t.get("content") or "").strip()
            if not content:
                continue
            speaker = "Client" if role == "user" else "Counselor"
            lines.append(f"{speaker}: {content}")
        return "\n".join(lines)

    def _current_topics_str(self) -> str:
        return " -> ".join(self.topic_stack) if self.topic_stack else ""

    def _stage_text(self, stage: CamiStage) -> str:
        desc = self.prompts["stage_description_prompt"].render(stage=stage).strip()
        return f"{stage}: {desc}" if desc else stage

    def _topic_desc(self, topic: str) -> str:
        template = self.prompts["topic_description_prompt"].get(topic)
        if not template:
            return ""
        return template.render(goal=self.goal, behavior=self.behavior).strip()

    def _strategy_desc(self, strategy: str) -> str:
        template = self.prompts["strategy_description_prompt"].get(strategy)
        return template.render().strip() if template else ""

    def _postprocess_counselor_text(self, text: str) -> str:
        cleaned = " ".join((text or "").split()).strip()
        if "Client:" in cleaned:
            cleaned = cleaned.split("Client:", 1)[0].strip()
        for prefix in ("Counselor:", "Assistant:"):
            if cleaned.lower().startswith(prefix.lower()):
                cleaned = cleaned[len(prefix) :].strip()
        return cleaned

    def state_infer(self) -> InferStatePromptOutput:
        prompt = self.prompts["infer_state_prompt"].render(context=self._conv_context())
        return self.chat_model.generate(
            messages=[{"role": "system", "content": prompt}],
            response_format=InferStatePromptOutput,
        )

    def select_strategy(self, stage: CamiStage) -> SelectStrategyPromptOutput:
        prompt = self.prompts["select_strategy_prompt"].render(
            context=self._conv_context(max_turns=12),
            stage=self._stage_text(stage),
        )
        res = self.chat_model.generate(
            messages=[{"role": "system", "content": prompt}],
            response_format=SelectStrategyPromptOutput,
        )
        if not res.strategies:
            res.strategies = ["Open Question"]
        res.strategies = res.strategies[:2]
        return res

    def initialize_topic(self) -> tuple[str, str, str]:
        context = self._conv_context(max_turns=8)
        response = (self.messages[-1].get("content") or "").strip()

        analysis_prompt = self.prompts["initialize_topic_analysis"].render(
            context=context,
            goal=self.goal,
            behavior=self.behavior,
            topics=self._current_topics_str(),
            response=response,
        )
        analysis_res = self.chat_model.generate(
            messages=[{"role": "system", "content": analysis_prompt}],
            response_format=InitializeTopicAnalysisPromptOutput,
        )

        json_prompt = self.prompts["initialize_topic_json"].render(
            context=context,
            goal=self.goal,
            behavior=self.behavior,
            topics=self._current_topics_str(),
            response=response,
            analysis=analysis_res.analysis,
        )
        dist_res = self.chat_model.generate(
            messages=[{"role": "system", "content": json_prompt}],
            response_format=InitializeTopicJsonPromptOutput,
        )
        dist = dist_res.model_dump(by_alias=True)
        topic = max(dist, key=dist.get)
        score = dist.get(topic, 0)

        non_system_turns = len([m for m in self.messages if m.get("role") != "system"])
        if score > 50 or non_system_turns > 10:
            self.initialized = True
            self.topic_stack = [topic]

        return analysis_res.analysis, "Switch", topic

    def _topic_options(self) -> tuple[List[str], List[str], List[str]]:
        step_in_topics: List[str] = []
        switch_topics: List[str] = []
        step_out_topics: List[str] = []

        if not self.topic_stack:
            return step_in_topics, switch_topics, step_out_topics

        if len(self.topic_stack) == 1:
            step_in_topics = list(
                self.topic_graph.get(self.topic_stack[0], {}).get("Children", [])
            )
            switch_topics = [
                "Health",
                "Interpersonal Relationships",
                "Law",
                "Economy",
                "Education",
            ]
            return step_in_topics, switch_topics, step_out_topics

        if len(self.topic_stack) == 2:
            step_in_topics = list(
                self.topic_graph.get(self.topic_stack[1], {}).get("Children", [])
            )
            switch_topics = list(
                self.topic_graph.get(self.topic_stack[0], {}).get("Children", [])
            )
            step_out_topics = [
                "Health",
                "Interpersonal Relationships",
                "Law",
                "Economy",
                "Education",
            ]
            return step_in_topics, switch_topics, step_out_topics

        if len(self.topic_stack) >= 3:
            switch_topics = list(
                self.topic_graph.get(self.topic_stack[1], {}).get("Children", [])
            )
            step_out_topics = list(
                self.topic_graph.get(self.topic_stack[0], {}).get("Children", [])
            )
            return step_in_topics, switch_topics, step_out_topics

        return step_in_topics, switch_topics, step_out_topics

    def topic_explore(self) -> TopicStackPromptOutput:
        if not self.topic_stack:
            analysis, action, topic = self.initialize_topic()
            return TopicStackPromptOutput(analysis=analysis, action=action, topic=topic)

        step_in_topics, switch_topics, step_out_topics = self._topic_options()
        topic_stack_len = len(self.topic_stack)
        has_step_out_topics = bool(step_out_topics)

        options_prompt = self.prompts["topic_stack_prompt"].render(
            topic_stack_len=topic_stack_len,
            has_step_out_topics=has_step_out_topics,
            step_in_topics=(
                "\n        - ".join(step_in_topics) if step_in_topics else ""
            ),
            switch_topics="\n        - ".join(switch_topics) if switch_topics else "",
            step_out_topics=(
                "\n        - ".join(step_out_topics) if step_out_topics else ""
            ),
        )

        base_prompt = self.prompts["explore_prompt"].render(
            context=self._conv_context(max_turns=8),
            goal=self.goal,
            behavior=self.behavior,
            topics=self._current_topics_str(),
            response=(self.messages[-1].get("content") or "").strip(),
        )
        prompt = f"{base_prompt.rstrip()}\n\n{options_prompt}"
        res = self.chat_model.generate(
            messages=[{"role": "system", "content": prompt}],
            response_format=TopicStackPromptOutput,
        )

        candidates: List[str] = []
        if res.action == "Step Into":
            candidates = step_in_topics
        elif res.action == "Switch":
            candidates = switch_topics
        elif res.action == "Step Out":
            candidates = step_out_topics

        topic = res.topic
        if candidates and topic not in candidates:
            topic = candidates[0]

        if res.action == "Step Into" and step_in_topics and topic in step_in_topics:
            self.topic_stack.append(topic)
        elif res.action == "Switch" and switch_topics and topic in switch_topics:
            self.topic_stack = self.topic_stack[:-1] + [topic]
        elif res.action == "Step Out" and step_out_topics and topic in step_out_topics:
            if len(self.topic_stack) == 2:
                self.topic_stack = [topic]
            else:
                self.topic_stack = self.topic_stack[:1] + [topic]

        return TopicStackPromptOutput(
            analysis=res.analysis, action=res.action, topic=topic
        )

    def _feedback_to_text(self, fb: FeedbackPromptOutput) -> str:
        parts = [
            f"Alignment score: {fb.topic_alignment_score}/5. {fb.topic_alignment_feedback}",
            f"Strategy score: {fb.strategy_adherence_score}/5. {fb.strategy_adherence_feedback}",
        ]
        if fb.suggestions:
            parts.append("Suggestions:\n- " + "\n- ".join(fb.suggestions))
        return "\n".join(parts)

    def refine_response(self, response: str, topic: str, strategies: List[str]) -> str:
        context = self._conv_context(max_turns=8)
        topic_text = f"{topic}: {self._topic_desc(topic)}".strip()
        strategy_text = "\n".join(
            f"- {s}: {self._strategy_desc(s)}".strip() for s in strategies
        ).strip()

        current = response
        for _ in range(3):
            feedback_prompt = self.prompts["feedback_prompt"].render(
                context=context,
                response=f"Counselor: {current}",
                topic=topic_text,
                strategy=strategy_text,
            )
            fb = self.chat_model.generate(
                messages=[{"role": "system", "content": feedback_prompt}],
                response_format=FeedbackPromptOutput,
            )
            score = fb.total_score
            if score is None:
                score = fb.topic_alignment_score + fb.strategy_adherence_score
            if score > 7:
                break

            refine_prompt = self.prompts["refine_prompt"].render(
                context=context,
                response=f"Counselor: {current}",
                topic=topic_text,
                strategy=strategy_text,
                feedback=self._feedback_to_text(fb),
            )
            refined = self.chat_model.generate(
                messages=[{"role": "system", "content": refine_prompt}],
                response_format=RefinePromptOutput,
            )
            current = self._postprocess_counselor_text(refined.content)

        return current

    def _generate_candidates(
        self, last_utterance: str, topic: str, stage: CamiStage, strategies: List[str]
    ) -> List[str]:
        topic_desc = self._topic_desc(topic)
        stage_text = self._stage_text(stage)

        candidates: List[str] = []
        for s in strategies:
            strategy_desc = self._strategy_desc(s)
            prompt = self.prompts["candidate_prompt_single"].render(
                last_utterance=last_utterance,
                stage=stage_text,
                topic=topic,
                topic_desc=topic_desc,
                strategy=s,
                strategy_desc=strategy_desc,
            )
            msgs = self.messages[:-1] + [{"role": "user", "content": prompt}]
            res = self.chat_model.generate(msgs).content
            candidates.append(self._postprocess_counselor_text(res))

        if len(strategies) >= 2:
            strategies_with_desc = [
                {"name": s, "desc": self._strategy_desc(s)} for s in strategies
            ]
            prompt = self.prompts["candidate_prompt_combine"].render(
                last_utterance=last_utterance,
                stage=stage_text,
                topic=topic,
                topic_desc=topic_desc,
                strategies=strategies_with_desc,
            )
            msgs = self.messages[:-1] + [{"role": "user", "content": prompt}]
            res = self.chat_model.generate(msgs).content
            candidates.append(self._postprocess_counselor_text(res))

        return [c for c in candidates if c]

    def _select_response(self, candidates: List[str]) -> int:
        conversation = "\n".join(
            f"- {l}" for l in self._conv_context(max_turns=14).splitlines()
        )
        responses = "\n".join(f"{i+1}. {r}" for i, r in enumerate(candidates))
        prompt = self.prompts["response_select_prompt"].render(
            goal=self.goal,
            behavior=self.behavior,
            conversation=conversation,
            responses=responses,
        )
        res = self.chat_model.generate(
            messages=[{"role": "system", "content": prompt}],
            response_format=ResponseSelectPromptOutput,
        )
        return res.response_id

    def generate_response(self, msg: str):
        if not self._has_greeted:
            self._has_greeted = True
            greeting = self.prompts["greeting"].render()
            self.messages.append({"role": "assistant", "content": greeting})
            return greeting

        self.messages.append({"role": "user", "content": msg})

        state_res = self.state_infer()
        stage = state_res.stage

        if not self.initialized:
            _, _, topic = self.initialize_topic()
        else:
            explore_res = self.topic_explore()
            topic = explore_res.topic

        self.explored_topics.append(topic)

        strategy_res = self.select_strategy(stage)
        selected_strategies = strategy_res.strategies

        last_utterance = (self.messages[-1].get("content") or "").strip()
        candidates = self._generate_candidates(
            last_utterance, topic, stage, selected_strategies
        )
        if not candidates:
            res = self.chat_model.generate(self.messages).content
            final_text = self._postprocess_counselor_text(res)
        else:
            response_id = self._select_response(candidates)
            idx = max(0, min(response_id - 1, len(candidates) - 1))
            final_text = candidates[idx]
            final_text = self.refine_response(final_text, topic, selected_strategies)

        self.messages.append({"role": "assistant", "content": final_text})
        return final_text

    def reset(self):
        self.build_sys_prompt()
        self.client = None
        self._has_greeted = False
        self.initialized = False
        self.topic_stack = []
        self.explored_topics = []
