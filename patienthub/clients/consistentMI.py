import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from omegaconf import DictConfig
from pydantic import BaseModel, Field
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from patienthub.base import ChatAgent
from patienthub.configs import APIModelConfig
from patienthub.utils.models import get_reranker
from patienthub.utils import get_chat_model, load_json, load_prompts


# ===== Config =====
@dataclass
class ConsistentMIClientConfig(APIModelConfig):
    """Configuration for ConsistentMI client agent."""

    agent_type: str = "consistentMI"
    data_path: str = "data/characters/ConsistentMI.json"
    topics_path: str = "data/resources/ConsistentMI_topics.json"
    topic_graph_path: str = "data/resources/ConsistentMI_topic_graph.json"
    data_idx: int = 0
    chat_model: Any = None
    model_retriever: Any = None


# ===== Response Schemas =====
class Response(BaseModel):
    content: str = Field(description="The content of your generated response")


class BinaryAnswer(BaseModel):
    answer: bool = Field(description="True if yes, False otherwise")
    rationale: Optional[str] = Field(default=None, description="Short explanation")


class ActionDistribution(BaseModel):
    Deny: int = 0
    Downplay: int = 0
    Blame: int = 0
    Inform: int = 0
    Engage: int = 0


class ContemplationActionDistribution(BaseModel):
    Inform: int = 0
    Engage: int = 0
    Hesitate: int = 0
    Doubt: int = 0
    Acknowledge: int = 0


class PreparationActionDistribution(BaseModel):
    Inform: int = 0
    Engage: int = 0
    Reject: int = 0
    Accept: int = 0
    Plan: int = 0


class ClientState:
    """Encapsulates the mutable state of the ConsistentMI client."""

    def __init__(
        self,
        stage: str = "Precontemplation",
        engagement: float = 3.0,
        receptivity: float = 3.0,
        error_topic_count: int = 0,
    ):

        self.stage = stage
        self.engagement = engagement
        self.receptivity = receptivity
        self.error_topic_count = error_topic_count

    def update(self, new_stage: str = None, beliefs: List[str] = []):
        """Update client state based on conversation."""
        if new_stage:
            self.stage = new_stage
        else:
            if self.stage == "Contemplation":
                if not beliefs:
                    self.stage = "Preparation"
                return None

            if self.stage == "Preparation":
                return None

            if not self.engaged_topics:
                return None


class ActionSelector:
    """Handles action selection logic for different stages."""

    # Receptivity distributions for Precontemplation stage
    RECEPTIVITY_DISTRIBUTIONS: Dict[str, Dict[str, int]] = {
        "very_low": {
            "Deny": 23,
            "Downplay": 28,
            "Blame": 15,
            "Engage": 11,
            "Inform": 22,
        },
        "low": {"Deny": 20, "Downplay": 25, "Blame": 10, "Engage": 15, "Inform": 30},
        "medium": {"Deny": 19, "Downplay": 21, "Blame": 11, "Engage": 13, "Inform": 36},
        "high": {"Deny": 9, "Downplay": 20, "Blame": 13, "Engage": 14, "Inform": 44},
        "very_high": {
            "Deny": 7,
            "Downplay": 13,
            "Blame": 4,
            "Engage": 16,
            "Inform": 60,
        },
    }

    @classmethod
    def get_receptivity_level(cls, receptivity: float) -> str:
        if receptivity < 2:
            return "very_low"
        if receptivity < 3:
            return "low"
        if receptivity < 4:
            return "medium"
        if receptivity < 5:
            return "high"
        return "very_high"

    @classmethod
    def get_receptivity_distribution(cls, receptivity: float) -> Dict[str, int]:
        level = cls.get_receptivity_level(receptivity)
        return cls.RECEPTIVITY_DISTRIBUTIONS[level]

    @staticmethod
    def sample_action(distribution: Dict[str, int]) -> str:
        """Sample an action from a probability distribution."""
        total = sum(distribution.values())
        if total == 0:
            return "Engage"
        actions = list(distribution.keys())
        probs = [v / total for v in distribution.values()]
        return random.choices(actions, weights=probs, k=1)[0]

    @staticmethod
    def apply_constraints(
        distribution: Dict[str, int],
        items_dict: Dict[str, bool],
        stage: str,
    ) -> Dict[str, int]:
        """Zero out invalid actions based on available data."""
        result = distribution.copy()

        if not items_dict.get("personas", False) and "Inform" in result:
            result["Inform"] = 0
        if not items_dict.get("beliefs", False):
            if "Blame" in result:
                result["Blame"] = 0
            if stage == "Contemplation" and "Hesitate" in result:
                result["Hesitate"] = 0
        if not items_dict.get("plans", False):
            if stage == "Preparation" and "Plan" in result:
                result["Plan"] = 0

        return result


class TopicMatcher:
    """Handles topic matching and graph traversal."""

    def __init__(self, configs: Dict[str, Any]):
        self.topic_graph = load_json(configs.topic_graph_path)
        self.reranker = (
            get_reranker(configs.model_retriever) if configs.model_retriever else None
        )
        self.all_topics = self.extract_all_topics()
        self.topic_passages: List[str] = []

    def extract_all_topics(self) -> List[str]:
        """Extract unique topics from graph."""
        topics = []
        for node, neighbors in self.topic_graph.items():
            topics += [] if node in topics else [node]
            for neighbor in neighbors:
                topics += [] if neighbor in topics else [neighbor]
        return topics

    def init_passages(
        self, prompts: Any, behavior: str, goal: str, topics_data: List[Dict]
    ) -> None:
        """Initialize topic passages for matching."""
        topic_to_content = {
            item.get("topic"): item.get("content", "")
            for item in topics_data
            if "topic" in item
        }

        self.topic_passages = []
        for topic in self.all_topics:
            description = prompts["topic_description_prompt"].render(
                behavior=behavior, goal=goal, topic=topic
            )
            passage = f"{description.strip()} {topic_to_content.get(topic, '')}"
            self.topic_passages.append(passage)

    def find_related_topics(self, query: str, top_k: int = 5) -> List[str]:
        """Find topics most related to query."""
        if not query:
            return []

        scores = self.score_passages(query)
        if scores is None:
            return []

        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[
            :top_k
        ]
        return [self.all_topics[i] for i in top_indices]

    def score_passages(self, query: str) -> Optional[List[float]]:
        """Score passages using reranker or lexical fallback."""
        # Try reranker first
        if self.reranker:
            scores = self.reranker.score(query, self.topic_passages)
            if scores:
                return scores

        # Lexical fallback
        lower_query = query.lower()
        return [
            sum(1 for token in lower_query.split() if token in passage.lower())
            for passage in self.topic_passages
        ]

    def compute_distance(self, start: str, target: str) -> float:
        """Compute shortest path distance using Dijkstra's algorithm."""
        if start not in self.topic_graph:
            return float("inf")

        distances = {node: float("inf") for node in self.topic_graph}
        distances[start] = 0
        visited: set = set()
        pq = [(0, start)]

        while pq:
            current_dist, current = min(pq, key=lambda x: x[0])
            pq.remove((current_dist, current))

            if current == target:
                return current_dist
            if current in visited:
                continue

            visited.add(current)

            for neighbor, weight in self.topic_graph.get(current, {}).items():
                if neighbor in visited:
                    continue
                new_dist = current_dist + weight
                if new_dist < distances.get(neighbor, float("inf")):
                    distances[neighbor] = new_dist
                    pq.append((new_dist, neighbor))

        return float("inf")


# ===== Main Client =====
class ConsistentMIClient(ChatAgent):
    """ConsistentMI client agent for motivational interviewing simulation."""

    def __init__(self, configs: DictConfig):
        self.configs = configs
        self.data = load_json(configs.data_path)[configs.data_idx]
        self.prompts = load_prompts(
            role="client", agent_type="consistentMI", lang=configs.lang
        )
        self.chat_model = get_chat_model(configs.chat_model)
        self.messages = [SystemMessage(content=self.load_sys_prompt())]

        # Additional components
        self.load_profile()
        self.state = self.load_state()
        self.topic_matcher = TopicMatcher(configs, self.reranker)

        # Load profile and initialize
        self.topic_matcher.init_passages(self.prompts, self.behavior, self.goal, [])

    def load_profile(self) -> None:
        """Load client profile from data file."""
        self.name = self.data.get("name", "ConsistentMI")
        self.goal = self.data.get("topic", "")
        self.behavior = self.data.get("Behavior", "")

        self.acceptable_plans: List[str] = self.data.get("Acceptable Plans", []).copy()

        motivation_list = self.data.get("Motivation", [])
        self.motivation_text = motivation_list[-1] if motivation_list else ""
        self.engaged_topics = motivation_list[:-1] if len(motivation_list) > 1 else []

    def load_sys_prompt(self):
        self.personas: List[str] = self.data.get("Personas", [])
        self.beliefs: List[str] = self.data.get("Beliefs", [])
        personas_and_beliefs = "\n".join(f"- {t}" for t in self.personas + self.beliefs)

        return self.prompts["client_system_prompt"].render(
            behavior=self.behavior,
            goal=self.goal,
            personas_and_beliefs=personas_and_beliefs,
        )

    def load_state(self) -> ClientState:
        suggestibilities = self.data.get("suggestibilities", [])
        initial_receptivity = (
            sum(suggestibilities) / len(suggestibilities) if suggestibilities else 3
        )
        return ClientState(
            stage=self.data.get("initial_stage", "Precontemplation"),
            receptivity=initial_receptivity,
            engagement=initial_receptivity,
        )

    def set_therapist(self, therapist: Dict) -> None:
        self.therapist = therapist.get("name", "Therapist")

    def generate(self, messages: List[Any], response_format: type[BaseModel]) -> Any:
        chat_model = self.chat_model.with_structured_output(response_format)
        return chat_model.invoke(messages)

    def verify_motivation(self) -> str:
        """Check if therapist has addressed client's motivation."""
        context_block = ""
        for msg in self.messages[max(1, len(self.messages) - 5) :]:
            role = "Therapist" if isinstance(msg, HumanMessage) else "Client"
            context_block += f"{role}: {msg.content}\n"

        prompt = self.prompts["verify_motivation_prompt"].render(
            goal=self.goal,
            context_block=context_block,
            motivation=self.motivation_text,
        )
        res = self.generate([SystemMessage(content=prompt)], BinaryAnswer)

        if res.answer:
            self.state.update(new_stage="Motivation")

        return res.rationale or ""

    def evaluate_topic_engagement(self) -> Optional[str]:
        """Evaluate how well therapist is engaging with client's topics."""
        last_utterance = self.messages[-1].content if self.messages else ""
        top_topics = self.topic_matcher.find_related_topics(last_utterance)
        predicted_topic = top_topics[0] if top_topics else self.engaged_topics[0]

        if predicted_topic == self.engaged_topics[0]:
            self.state.engagement = 4
            self.state.error_topic_count = 0
            return self.verify_motivation()

        distance = self.topic_matcher.compute_distance(
            self.engaged_topics[0], predicted_topic
        )

        if distance <= 3:
            self.state.engagement = 3
            self.state.error_topic_count = 0
        elif distance <= 5:
            self.state.engagement = 2
        else:
            self.state.engagement = 1
            if sum(1 for m in self.messages if isinstance(m, HumanMessage)) > 10:
                self.state.error_topic_count += 1

        return f"The client's perceived topic is {predicted_topic}."

    # ===== Action Selection =====
    def get_precontemplation_distribution(self, context: str) -> Dict[str, int]:
        """Get action distribution for Precontemplation stage."""
        prompt = self.prompts["select_action_prompt"].render(recent_context=context)

        try:
            res = self.generate([SystemMessage(content=prompt)], ActionDistribution)
            context_dist = {
                "Deny": res.Deny,
                "Downplay": res.Downplay,
                "Blame": res.Blame,
                "Inform": res.Inform,
                "Engage": res.Engage,
            }
        except Exception:
            context_dist = {
                "Deny": 20,
                "Downplay": 20,
                "Blame": 20,
                "Inform": 20,
                "Engage": 20,
            }

        receptivity_dist = ActionSelector.get_receptivity_distribution(
            self.state.receptivity
        )

        return {
            action: context_dist.get(action, 0) + receptivity_dist[action]
            for action in receptivity_dist
        }

    def get_contemplation_distribution(self, context: str) -> Dict[str, int]:
        """Get action distribution for Contemplation stage."""
        prompt = self.prompts["select_action_contemplation_prompt"].render(
            recent_context=context
        )

        try:
            res = self.generate(
                [SystemMessage(content=prompt)], ContemplationActionDistribution
            )
            return {
                "Inform": res.Inform,
                "Engage": res.Engage,
                "Hesitate": res.Hesitate,
                "Doubt": res.Doubt,
                "Acknowledge": res.Acknowledge,
            }
        except Exception:
            return {
                "Inform": 1,
                "Engage": 1,
                "Hesitate": 1,
                "Doubt": 1,
                "Acknowledge": 1,
            }

    def get_preparation_distribution(self, context: str) -> Dict[str, int]:
        """Get action distribution for Preparation stage."""
        prompt = self.prompts["select_action_preparation_prompt"].render(
            recent_context=context
        )

        try:
            res = self.generate(
                [SystemMessage(content=prompt)], PreparationActionDistribution
            )
            return {
                "Inform": res.Inform,
                "Engage": res.Engage,
                "Reject": res.Reject,
                "Accept": res.Accept,
                "Plan": res.Plan,
            }
        except Exception:
            return {"Inform": 1, "Engage": 1, "Reject": 1, "Accept": 1, "Plan": 1}

    # ===== Action Selection =====
    def select_action(self, stage: str) -> str:
        """Select action based on current stage."""
        context = ""
        for msg in self.messages[max(1, len(self.messages) - 5) :]:
            role = "Therapist" if isinstance(msg, HumanMessage) else "Client"
            context += f"{role}: {msg.content}\n"

        if stage == "Contemplation":
            distribution = self.get_contemplation_distribution(context)
        elif stage == "Preparation":
            distribution = self.get_preparation_distribution(context)
        else:
            distribution = self.get_precontemplation_distribution(context)

        items_dict = {
            "personas": bool(self.personas),
            "beliefs": bool(self.beliefs),
            "plans": bool(self.acceptable_plans),
        }
        distribution = ActionSelector.apply_constraints(
            distribution,
            items_dict=items_dict,
            stage=stage,
        )

        return ActionSelector.sample_action(distribution)

    def determine_action(self, stage: str) -> str:
        """Determine action for current stage."""
        if stage == "Motivation":
            return "Acknowledge"
        if stage == "Precontemplation" and self.state.error_topic_count >= 5:
            return "Terminate"
        return self.select_action(stage)

    def get_action_config(self, action: str) -> Optional[tuple]:
        """Get (source_list, prompt_key, should_consume) for action."""
        configs = {
            "Inform": (self.personas, "select_information_inform_prompt", False),
            "Downplay": (self.beliefs, "select_information_downplay_prompt", False),
            "Blame": (self.beliefs, "select_information_blame_prompt", False),
            "Hesitate": (self.beliefs, "select_information_hesitate_prompt", True),
        }
        return configs.get(action)

    # ===== Information Selection =====
    def select_information(self, action: str) -> Optional[str]:
        """Select relevant information for the action."""
        last_therapist = self.messages[-1].content
        if not last_therapist or "?" not in last_therapist:
            return None

        action_config = self.get_action_config(action)
        if not action_config:
            return None

        source_list, prompt_key, consume = action_config

        for item in source_list:
            prompt = self.prompts[prompt_key].render(persona=item)
            res = self.generate([SystemMessage(content=prompt)], BinaryAnswer)
            if res.answer:
                if consume:
                    source_list.remove(item)
                return item

        if not source_list:
            return None

        chosen = random.choice(source_list)
        if consume:
            source_list.remove(item)
        return chosen

    # ===== Reply Generation =====

    def gather_information(self, stage: str, action: str) -> Optional[str]:
        """Gather information needed for the action."""
        if action in ["Inform", "Downplay", "Blame", "Hesitate"]:
            return self.select_information(action)
        if action == "Plan" and self.acceptable_plans:
            return self.acceptable_plans.pop(0)
        return None

    def build_instruction(
        self, stage: str, action: str, information: Optional[str]
    ) -> str:
        """Build instruction for reply generation."""
        engage_instruction = ""
        if self.engaged_topics or len(self.engaged_topics) >= 3:
            engage_instruction = (
                self.prompts["engage_instruction_prompt"]
                .render(
                    engagement_level=int(self.state.engagement),
                    engagemented_topics=self.engaged_topics,
                    motivation=self.motivation_text,
                )
                .strip()
            )
        state_instruction = (
            ""
            if stage == "Motivation"
            else self.prompts["state_instruction_prompt"]
            .render(stage=self.state.stage, behavior=self.behavior, goal=self.goal)
            .strip()
        )
        action_instruction = (
            self.prompts["action_instruction_prompt"].render(action=action).strip()
        )
        instruction = self.prompts["reply_instruction_prompt"].render(
            stage=stage,
            action=action,
            engage_instruction=engage_instruction,
            state_instruction=state_instruction,
            action_instruction=action_instruction,
            information=information or "",
            motivation=self.motivation_text,
        )

        if stage == "Motivation":
            self.state.transition_to("Contemplation")

        return instruction

    def generate_response(self, msg: str) -> Response:
        self.messages.append(HumanMessage(content=msg))

        self.update_state()
        self.state.update(self.beliefs)
        self.evaluate_topic_engagement()

        stage = self.state.stage
        action = self.determine_action(stage)
        print(f"[ConsistentMIClient] stage={stage}, action={action}")

        information = self.gather_information(stage, action)
        instruction = self.build_instruction(stage, action, information)
        self.messages.append(HumanMessage(content=instruction))

        res = self.generate(self.messages, response_format=Response)
        self.messages.append(AIMessage(content=res.content))

        content = res.content.removeprefix("Client: ").strip()
        return Response(content=content)

    def reset(self) -> None:
        self.load_profile()
