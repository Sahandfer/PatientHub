import random
from typing import Any, Dict, List, Optional

from omegaconf import DictConfig
from pydantic import BaseModel, Field

from src.agents import InferenceAgent
from src.utils import (
    get_model_client,
    get_reranker_model,
    load_json,
    load_prompts,
    rerank_query_passages,
)

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage


class Response(BaseModel):
    content: str = Field(description="The content of your generated response in this turn")


class ActionDistribution(BaseModel):
    Deny: int
    Downplay: int
    Blame: int
    Inform: int
    Engage: int


class ContemplationActionDistribution(BaseModel):
    Inform: int
    Engage: int
    Hesitate: int
    Doubt: int
    Acknowledge: int


class PreparationActionDistribution(BaseModel):
    Inform: int
    Engage: int
    Reject: int
    Accept: int
    Plan: int


class BinaryAnswer(BaseModel):
    answer: bool = Field(description="True if the answer is yes, false otherwise")
    rationale: Optional[str] = Field(default=None, description="Short explanation for the decision")


class consistentMIClient(InferenceAgent):
    def __init__(self, configs: DictConfig):
        self.configs = configs
        self.prompts = load_prompts(role="client", agent_type="consistentMI", lang=configs.lang)
        self.model_client = get_model_client(configs.model_client)
        (
            self.retriever_tokenizer,
            self.retriever_model,
            self.retriever_device,
        ) = get_reranker_model(configs.model_retriever)

        self.data = {}
        self.name = "ConsistentMI"
        self.therapist: Optional[str] = None

        self.topic_graph: Dict[str, Dict[str, int]] = {}
        self.all_topics: List[str] = []
        self.topic_passages: List[str] = []

        self.messages: List[Any] = []

        self._load_profile()
        self._init_topic_graph()
        self._init_topics()
        self._init_conversation()

    def generate(self, messages: List[Any], response_format: BaseModel):
        model_client = self.model_client.with_structured_output(response_format)
        res = model_client.invoke(messages)
        return res

    def set_therapist(self, therapist, prev_sessions: Optional[List[Dict[str, str]]] = None):
        self.therapist = therapist.get("name", "Therapist")

    def generate_response(self, msg: str):
        # Treat incoming message as therapist utterance
        self.messages.append(HumanMessage(content=msg))

        client_text = self.reply()

        # Persist clean conversation history for subsequent turns
        self.messages.append(AIMessage(content=client_text))

        content = client_text[len("Client: ") :].strip() if client_text.startswith("Client: ") else client_text
        return Response(content=content)

    def reset(self):
        # Keep model_client and prompts; reload profile-dependent state
        self._load_profile()
        self._init_topics()
        self._init_conversation()

    # ===== Internal helpers =====
    def _load_profile(self):
        profiles = load_json(self.configs.data_path)
        index = getattr(self.configs, "data_index", 0)
        self.data = profiles[index] if isinstance(profiles, list) else profiles
        self.name = self.data.get("name", "ConsistentMI")

        self.goal = self.data.get("topic", "")
        self.behavior = self.data.get("Behavior", "")
        self.personas: List[str] = self.data.get("Personas", [])
        self.beliefs: List[str] = self.data.get("Beliefs", [])
        self.acceptable_plans: List[str] = self.data.get("Acceptable Plans", []).copy()
        motivation_list = self.data.get("Motivation", [])
        self.motivation_text = motivation_list[-1] if motivation_list else ""
        self.engagemented_topics = motivation_list[:-1] if len(motivation_list) > 1 else []
        self.initial_stage = self.data.get("initial_stage", "Precontemplation")
        suggestibilities = self.data.get("suggestibilities", [])
        self.receptivity = (
            sum(suggestibilities) / len(suggestibilities) if suggestibilities else 3
        )
        self.engagement = self.receptivity
        self.state = self.initial_stage
        self.error_topic_count = 0

    def _init_topic_graph(self):
        # Copied from the original ConsistentMI simulator
        self.topic_graph = {
            "Health": {
                "Mental Disorders": 2,
                "Diseases": 2,
                "Sexual Health": 2,
                "Fitness": 2,
                "Health Care": 2,
                "Workplace Wellness": 1,
                "Interpersonal Relationships": 3,
                "Law": 3,
                "Economy": 3,
                "Education": 3,
            },
            "Interpersonal Relationships": {
                "Parenting": 2,
                "Family": 2,
                "Health": 3,
                "Law": 3,
                "Economy": 3,
            },
            "Parenting": {
                "Interpersonal Relationships": 2,
                "Family": 2,
                "Health": 3,
                "Education": 2,
                "Role Model": 1,
                "Child Development": 1,
                "Paternal Bond": 1,
                "Child Care": 1,
                "Habituation": 1,
            },
            "Family": {
                "Interpersonal Relationships": 2,
                "Parenting": 2,
                "Law": 2,
                "Health": 3,
                "Family Estrangement": 1,
                "Family Disruption": 1,
                "Divorce": 1,
            },
            "Mental Disorders": {
                "Health": 2,
                "Diseases": 3,
            },
            "Diseases": {
                "Health": 2,
                "Mental Disorders": 3,
                "Infection": 1,
                "Hypertension": 1,
                "Flu": 1,
                "Inflammation": 1,
                "Liver Disease": 1,
                "Lung Cancer": 1,
                "COPD": 1,
                "Asthma": 1,
                "Stroke": 1,
                "Diabetes": 1,
            },
            "Sexual Health": {
                "Health": 2,
                "Maternal Health": 1,
                "Safe Sex": 1,
                "Preterm Birth": 1,
                "Miscarriage": 1,
                "Birth Defects": 1,
            },
            "Fitness": {
                "Health": 2,
                "Physical Activity": 1,
                "Sport": 1,
                "Physical Fitness": 1,
                "Strength": 1,
                "Flexibility": 1,
                "Endurance": 1,
            },
            "Health Care": {
                "Health": 2,
                "Dentistry": 1,
                "Caregiver Burden": 1,
                "Independent Living": 1,
                "Human Appearance": 1,
            },
            "Economy": {
                "Health": 3,
                "Interpersonal Relationships": 3,
                "Law": 2,
                "Education": 2,
                "Employment": 1,
                "Personal Finance": 1,
                "Cost of Living": 1,
            },
            "Law": {
                "Health": 3,
                "Interpersonal Relationships": 3,
                "Economy": 2,
                "Education": 2,
                "Criminal Law": 1,
                "Family Law": 1,
                "Traffic Law": 1,
            },
            "Education": {
                "Health": 3,
                "Interpersonal Relationships": 3,
                "Law": 2,
                "Economy": 2,
                "Student Affairs": 1,
                "Academic Achievement": 1,
            },
            "Employment": {
                "Economy": 1,
                "Productivity": 1,
                "Absenteeism": 1,
                "Workplace Relationships": 1,
                "Career Break": 1,
                "Career Assessment": 1,
                "Absence Rate": 1,
                "Salary": 1,
                "Workplace Wellness": 2,
                "Workplace Incivility": 2,
            },
            "Personal Finance": {
                "Economy": 1,
                "Cost of Living": 1,
                "Personal Budget": 1,
                "Debt": 1,
                "Income Deficit": 1,
            },
            "Student Affairs": {
                "Education": 1,
                "Attendance": 1,
                "Suspension": 1,
                "Scholarship": 1,
            },
            "Academic Achievement": {
                "Education": 1,
                "Exam": 1,
            },
            "Criminal Law": {
                "Law": 1,
                "Arrest": 1,
                "Imprisonment": 1,
                "Complaint": 1,
            },
            "Family Law": {
                "Law": 1,
                "Family": 1,
                "Child Custody": 1,
            },
            "Traffic Law": {
                "Law": 1,
                "Traffic Ticket": 1,
            },
            "Workplace Wellness": {
                "Health": 1,
                "Employment": 2,
            },
            "Workplace Incivility": {
                "Employment": 2,
            },
            "Productivity": {
                "Employment": 1,
            },
            "Absenteeism": {
                "Employment": 1,
            },
            "Workplace Relationships": {
                "Employment": 1,
            },
            "Career Break": {
                "Employment": 1,
            },
            "Career Assessment": {
                "Employment": 1,
            },
            "Absence Rate": {
                "Employment": 1,
            },
            "Salary": {
                "Employment": 1,
            },
            "Cost of Living": {
                "Economy": 1,
                "Personal Finance": 1,
            },
            "Personal Budget": {
                "Personal Finance": 1,
            },
            "Debt": {
                "Personal Finance": 1,
            },
            "Income Deficit": {
                "Personal Finance": 1,
            },
            "Role Model": {
                "Parenting": 1,
            },
            "Child Development": {
                "Parenting": 1,
            },
            "Paternal Bond": {
                "Parenting": 1,
            },
            "Child Care": {
                "Parenting": 1,
            },
            "Habituation": {
                "Parenting": 1,
            },
            "Family Estrangement": {
                "Family": 1,
            },
            "Family Disruption": {
                "Family": 1,
            },
            "Divorce": {
                "Family": 1,
            },
            "Arrest": {
                "Criminal Law": 1,
            },
            "Imprisonment": {
                "Criminal Law": 1,
            },
            "Complaint": {
                "Criminal Law": 1,
            },
            "Child Custody": {
                "Family Law": 1,
            },
            "Traffic Ticket": {
                "Traffic Law": 1,
            },
            "Attendance": {
                "Student Affairs": 1,
            },
            "Suspension": {
                "Student Affairs": 1,
            },
            "Scholarship": {
                "Student Affairs": 1,
            },
            "Exam": {
                "Academic Achievement": 1,
            },
            "Infection": {
                "Diseases": 1,
            },
            "Hypertension": {
                "Diseases": 1,
            },
            "Flu": {
                "Diseases": 1,
            },
            "Inflammation": {
                "Diseases": 1,
            },
            "Liver Disease": {
                "Diseases": 1,
            },
            "Lung Cancer": {
                "Diseases": 1,
            },
            "COPD": {
                "Diseases": 1,
            },
            "Asthma": {
                "Diseases": 1,
            },
            "Stroke": {
                "Diseases": 1,
            },
            "Diabetes": {
                "Diseases": 1,
            },
        }

        self.all_topics = []
        for node in self.topic_graph:
            if node not in self.all_topics:
                self.all_topics.append(node)
            for neighbor in self.topic_graph[node]:
                if neighbor not in self.all_topics:
                    self.all_topics.append(neighbor)

    def _init_topics(self):
        topics_path = getattr(self.configs, "topics_path", None)
        topics_data = load_json(topics_path) if topics_path else []
        topic_to_content = {
            item.get("topic"): item.get("content", "") for item in topics_data if "topic" in item
        }

        self.topic_passages = []
        for topic in self.all_topics:
            description = self.prompts["topic_description_prompt"].render(
                behavior=self.behavior, goal=self.goal, topic=topic
            )
            passage = description.strip() + " " + topic_to_content.get(topic, "")
            self.topic_passages.append(passage)

    def _init_conversation(self):
        personas_and_beliefs = "\n".join(
            f"- {text}" for text in (self.personas + self.beliefs)
        )
        system_prompt = self.prompts["consistentmi_client_system_prompt"].render(
            behavior=self.behavior,
            goal=self.goal,
            personas_and_beliefs=personas_and_beliefs,
        )

        self.messages = [
            SystemMessage(content=system_prompt),
            HumanMessage(content="Hello. How are you?"),
            AIMessage(content="Client: I am good. What about you?"),
        ]

    # ===== Core reasoning blocks =====
    def verify_motivation(self):
        context_block = "\n- ".join(self._get_recent_context(5))
        prompt = self.prompts["verify_motivation_prompt"].render(
            goal=self.goal,
            context_block=context_block,
            motivation=self.motivation_text,
        )
        res = self.generate([SystemMessage(content=prompt)], response_format=BinaryAnswer)
        if res.answer:
            self.state = "Motivation"
        return res.rationale or ""

    def top_related_topics(self) -> List[str]:
        last_therapist = self._get_last_therapist_utterance()
        if not last_therapist:
            return []

        # Use cross-encoder reranker when available
        if self.retriever_model is not None and self.retriever_tokenizer is not None:
            scores = rerank_query_passages(
                self.retriever_tokenizer,
                self.retriever_model,
                self.retriever_device,
                last_therapist,
                self.topic_passages,
            )
            if scores is not None:
                indices = sorted(
                    range(len(scores)), key=lambda i: scores[i], reverse=True
                )[: min(5, len(scores))]
                return [self.all_topics[i] for i in indices]

        # Lightweight lexical fallback
        lower_query = last_therapist.lower()
        scores: List[int] = []
        for passage in self.topic_passages:
            score = sum(1 for token in lower_query.split() if token in passage.lower())
            scores.append(score)

        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[
            : min(5, len(scores))
        ]
        return [self.all_topics[index] for index in top_indices]

    def dijkstra(self, graph: Dict[str, Dict[str, int]], start_node: str, target_node: str):
        distances = {node: float("inf") for node in graph}
        distances[start_node] = 0
        pq = [(0, start_node)]
        visited = set()

        while pq:
            current_distance, current_node = min(pq, key=lambda x: x[0])
            pq.remove((current_distance, current_node))

            if current_node == target_node:
                return current_distance
            if current_node in visited:
                continue

            visited.add(current_node)
            for neighbor, weight in graph.get(current_node, {}).items():
                if neighbor in visited:
                    continue
                distance = current_distance + weight
                if distance < distances.get(neighbor, float("inf")):
                    distances[neighbor] = distance
                    pq.append((distance, neighbor))

        return float("inf")

    def update_state(self):
        if self.state == "Contemplation":
            if not self.beliefs:
                self.state = "Preparation"
            return None
        elif self.state == "Preparation":
            return None

        if not self.engagemented_topics:
            return None

        top_topics = self.top_related_topics()
        predicted_topic = top_topics[0] if top_topics else self.engagemented_topics[0]

        if predicted_topic == self.engagemented_topics[0]:
            self.engagement = 4
            self.error_topic_count = 0
            return self.verify_motivation()

        distance = self.dijkstra(self.topic_graph, self.engagemented_topics[0], predicted_topic)
        if distance <= 3:
            self.engagement = 3
            self.error_topic_count = 0
            return f"The client's perceived topic is {predicted_topic}."
        if distance <= 5:
            self.engagement = 2
            return f"The client's perceived topic is {predicted_topic}."

        self.engagement = 1
        # Approximate long conversations by number of therapist utterances
        if len([m for m in self.messages if isinstance(m, HumanMessage)]) > 10:
            self.error_topic_count += 1
        return f"The client's perceived topic is {predicted_topic}."

    def select_action(self, stage: str) -> str:
        # Shared recent context rendering
        recent_context = "\n".join(self._get_recent_context(3)).replace(
            "Client:", "**Client**:"
        ).replace("Counselor:", "**Counselor**:")

        # Contemplation: LLM-only distribution over allowed actions
        if stage == "Contemplation":
            prompt = self.prompts["select_action_contemplation_prompt"].render(
                recent_context=recent_context
            )
            try:
                res = self.generate(
                    [SystemMessage(content=prompt)],
                    response_format=ContemplationActionDistribution,
                )
                action_distribution = {
                    "Inform": res.Inform,
                    "Engage": res.Engage,
                    "Hesitate": res.Hesitate,
                    "Doubt": res.Doubt,
                    "Acknowledge": res.Acknowledge,
                }
            except Exception:
                action_distribution = {
                    "Inform": 1,
                    "Engage": 1,
                    "Hesitate": 1,
                    "Doubt": 1,
                    "Acknowledge": 1,
                }

        # Preparation: LLM-only distribution over allowed actions
        elif stage == "Preparation":
            prompt = self.prompts["select_action_preparation_prompt"].render(
                recent_context=recent_context
            )
            try:
                res = self.generate(
                    [SystemMessage(content=prompt)],
                    response_format=PreparationActionDistribution,
                )
                action_distribution = {
                    "Inform": res.Inform,
                    "Engage": res.Engage,
                    "Reject": res.Reject,
                    "Accept": res.Accept,
                    "Plan": res.Plan,
                }
            except Exception:
                action_distribution = {
                    "Inform": 1,
                    "Engage": 1,
                    "Reject": 1,
                    "Accept": 1,
                    "Plan": 1,
                }

        # Precontemplation: keep original context + receptivity logic
        else:
            prompt = self.prompts["select_action_prompt"].render(
                recent_context=recent_context
            )

            try:
                res = self.generate(
                    [SystemMessage(content=prompt)],
                    response_format=ActionDistribution,
                )
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

            if self.receptivity < 2:
                receptivity_dist = {"Deny": 23, "Downplay": 28, "Blame": 15, "Engage": 11, "Inform": 22}
            elif self.receptivity < 3:
                receptivity_dist = {"Deny": 20, "Downplay": 25, "Blame": 10, "Engage": 15, "Inform": 30}
            elif self.receptivity < 4:
                receptivity_dist = {"Deny": 19, "Downplay": 21, "Blame": 11, "Engage": 13, "Inform": 36}
            elif self.receptivity < 5:
                receptivity_dist = {"Deny": 9, "Downplay": 20, "Blame": 13, "Engage": 14, "Inform": 44}
            else:
                receptivity_dist = {"Deny": 7, "Downplay": 13, "Blame": 4, "Engage": 16, "Inform": 60}

            action_distribution = {
                action: context_dist.get(action, 0) + receptivity_dist[action]
                for action in receptivity_dist
            }

        # Shared post-processing for all stages
        if not self.personas and "Inform" in action_distribution:
            action_distribution["Inform"] = 0
        if not self.beliefs and "Blame" in action_distribution:
            action_distribution["Blame"] = 0
        if stage == "Contemplation" and not self.beliefs and "Hesitate" in action_distribution:
            action_distribution["Hesitate"] = 0
        if stage == "Preparation" and not self.acceptable_plans and "Plan" in action_distribution:
            action_distribution["Plan"] = 0

        total = sum(action_distribution.values())
        if total == 0:
            return "Engage"
        actions = list(action_distribution.keys())
        probs = [v / total for v in action_distribution.values()]
        return random.choices(actions, weights=probs, k=1)[0]

    def select_information(self, action: str) -> Optional[str]:
        last_therapist = self._get_last_therapist_utterance()
        if not last_therapist or "?" not in last_therapist:
            return None

        if action == "Inform":
            personas = self.personas
            prompt_template = self.prompts["select_information_inform_prompt"]
        elif action == "Downplay":
            personas = self.beliefs
            prompt_template = self.prompts["select_information_downplay_prompt"]
        elif action == "Blame":
            personas = self.beliefs
            prompt_template = self.prompts["select_information_blame_prompt"]
        elif action == "Hesitate":
            personas = self.beliefs
            prompt_template = self.prompts["select_information_hesitate_prompt"]
        else:
            return None

        for persona in personas:
            prompt = prompt_template.render(persona=persona)
            res = self.generate([SystemMessage(content=prompt)], response_format=BinaryAnswer)
            if res.answer:
                # For Hesitate, consume this belief so it won't be reused,
                # mirroring the original ConsistentMI simulator behavior.
                if action == "Hesitate":
                    try:
                        self.beliefs.remove(persona)
                    except ValueError:
                        # Persona may already have been removed; ignore.
                        pass
                return persona

        if not personas:
            return None

        chosen = random.choice(personas)
        if action == "Hesitate":
            try:
                self.beliefs.remove(chosen)
            except ValueError:
                pass
        return chosen

    def get_engage_instruction(self):
        if not self.engagemented_topics or len(self.engagemented_topics) < 3:
            return ""
        return self.prompts["engage_instruction_prompt"].render(
            engagement_level=int(self.engagement),
            engagemented_topics=self.engagemented_topics,
            motivation=self.motivation_text,
        ).strip()

    def _render_state_instruction(self):
        return self.prompts["state_instruction_prompt"].render(
            stage=self.state, behavior=self.behavior, goal=self.goal
        ).strip()

    def _render_action_instruction(self, action: str):
        return self.prompts["action_instruction_prompt"].render(action=action).strip()

    def _get_recent_context(self, n: int) -> List[str]:
        """Return recent conversation as prefixed text lines: 'Counselor: ...' / 'Client: ...'."""
        lines: List[str] = []
        # Skip initial system message
        for msg in self.messages[1:]:
            if isinstance(msg, HumanMessage):
                lines.append(f"Counselor: {msg.content}")
            elif isinstance(msg, AIMessage):
                content = msg.content
                if not content.startswith("Client:"):
                    content = f"Client: {content}"
                lines.append(content)
        return lines[-n:] if n > 0 else lines

    def _get_last_therapist_utterance(self) -> Optional[str]:
        """Return raw text of the last therapist (Human) utterance."""
        for msg in reversed(self.messages):
            if isinstance(msg, HumanMessage):
                return msg.content
        return None

    def reply(self) -> str:
        engagement_analysis = self.update_state()
        engage_instruction = self.get_engage_instruction()
        information = None
        state_for_action = self.state

        if self.state == "Motivation":
            action = "Acknowledge"
            state_instruction = ""
            action_instruction = self._render_action_instruction(action)
            instruction = self.prompts["reply_instruction_prompt"].render(
                stage="Motivation",
                action=action,
                engage_instruction=engage_instruction,
                state_instruction=state_instruction,
                action_instruction=action_instruction,
                information="",
                motivation=self.motivation_text,
            )
            self.state = "Contemplation"
        elif self.state == "Precontemplation":
            action = (
                "Terminate"
                if self.error_topic_count >= 5
                else self.select_action("Precontemplation")
            )
            state_instruction = self._render_state_instruction()
            action_instruction = self._render_action_instruction(action)
            if action in ["Inform", "Downplay", "Blame"]:
                information = self.select_information(action)
            instruction = self.prompts["reply_instruction_prompt"].render(
                stage="Precontemplation",
                action=action,
                engage_instruction=engage_instruction,
                state_instruction=state_instruction,
                action_instruction=action_instruction,
                information=information or "",
                motivation=self.motivation_text,
            )
        elif self.state == "Contemplation":
            action = self.select_action("Contemplation")
            state_instruction = self._render_state_instruction()
            action_instruction = self._render_action_instruction(action)
            if action in ["Hesitate", "Inform"]:
                information = self.select_information(action)
            instruction = self.prompts["reply_instruction_prompt"].render(
                stage="Contemplation",
                action=action,
                engage_instruction=engage_instruction,
                state_instruction=state_instruction,
                action_instruction=action_instruction,
                information=information or "",
                motivation=self.motivation_text,
            )
        else:  # Preparation
            action = self.select_action("Preparation")
            state_instruction = self._render_state_instruction()
            action_instruction = self._render_action_instruction(action)
            if action == "Inform":
                information = self.select_information(action)
            elif action == "Plan" and self.acceptable_plans:
                information = self.acceptable_plans.pop(0)
            instruction = self.prompts["reply_instruction_prompt"].render(
                stage="Preparation",
                action=action,
                engage_instruction=engage_instruction,
                state_instruction=state_instruction,
                action_instruction=action_instruction,
                information=information or "",
                motivation=self.motivation_text,
            )

        print(f"[consistentMIClient.reply] state={state_for_action}, action={action}")

        # Build model call with conversation history and inline instruction
        last_therapist = self._get_last_therapist_utterance() or ""
        user_message = f"{last_therapist} {instruction.replace(chr(10), ' ')}"
        messages_for_model = list(self.messages) + [HumanMessage(content=user_message)]
        res = self.generate(messages_for_model, response_format=Response)

        patient_text = res.content.strip()
        if not patient_text.startswith("Client:"):
            patient_text = f"Client: {patient_text}"
        if "Counselor:" in patient_text:
            patient_text = patient_text.split("Counselor:")[0].strip()

        return patient_text
