from dataclasses import dataclass
from colorama import Fore, Style, init
from typing import TypedDict, List, Dict, Any, Optional

from patienthub.utils import save_json

from langgraph.graph import StateGraph, START, END

init(autoreset=True)


@dataclass
class TherapySessionConfig:
    """Configuration for a therapy session."""

    event_type: str = "therapySession"
    reminder_turn_num: int = 5
    max_turns: int = 30
    langfuse: bool = False
    recursion_limit: int = 1000
    output_dir: str = "data/sessions/default/session_1.json"


class TherapySessionState(TypedDict):
    messages: List[Dict[str, Any]]
    summary: Optional[str]
    homework: Optional[List[str]]
    msg: Optional[str]


class TherapySession:
    def __init__(self, configs: Dict[str, Any]):
        self.configs = configs

        self.num_turns = 0
        self.graph = self.build_graph()

    def set_characters(self, characters: Dict[str, Any]):
        try:
            self.client = characters["client"]
            self.therapist = characters["therapist"]
            self.evaluator = characters.get("evaluator", None)
        except KeyError as e:
            raise ValueError(f"Missing character in session: {e}")

    def build_graph(self):
        # The session graph
        graph = StateGraph(TherapySessionState)

        # Nodes for the graph
        graph.add_node("initiate_session", self.init_session)
        graph.add_node("generate_therapist_response", self.generate_therapist_response)
        graph.add_node("generate_client_response", self.generate_client_response)
        graph.add_node("give_reminder", self.give_reminder)
        graph.add_node("end_session", self.end_session)

        # Edges for the graph
        graph.add_edge(START, "initiate_session")
        graph.add_edge("initiate_session", "generate_therapist_response")
        graph.add_edge("generate_therapist_response", "generate_client_response")
        graph.add_conditional_edges(
            "generate_client_response",
            self.check_session_end,
            {
                "END": "end_session",
                "CONTINUE": "generate_therapist_response",
                "REMIND": "give_reminder",
            },
        )
        graph.add_edge("give_reminder", "generate_therapist_response")
        graph.add_edge("end_session", END)

        return graph.compile()

    def init_session(self, state: TherapySessionState):
        # Introduce characters together
        self.therapist.set_client({"name": self.client.name})
        self.client.set_therapist({"name": self.therapist.name})

        print("=" * 50)
        return {
            "msg": "[Moderator] You may start the session now.",
            "messages": [],
        }

    def generate_therapist_response(self, state: TherapySessionState):
        name = self.therapist.name
        res = self.therapist.generate_response(state["msg"])
        print(f"--- Turn # {self.num_turns + 1}/{self.configs.max_turns} ---")
        print(f"{Fore.CYAN}{Style.BRIGHT}{name}{Style.RESET_ALL}: {res.content}")
        return {
            "msg": f"{self.therapist.name}: {res.content}",
            "messages": state["messages"]
            + [{"role": "therapist", "content": res.content}],
        }

    def generate_client_response(self, state: TherapySessionState):
        if state["msg"].replace(f"{self.therapist.name}: ", "") in [
            "END",
            "end",
            "exit",
        ]:
            return {
                "msg": "The therapist has ended the session.",
                "messages": state["messages"][:-1],
            }
        name = self.client.name
        res = self.client.generate_response(state["msg"])
        print(f"{Fore.RED}{Style.BRIGHT}{name}{Style.RESET_ALL}: {res.content}")
        self.num_turns += 1

        return {
            "msg": f"{name}: {res.content}",
            "messages": state["messages"]
            + [{"role": "client", "content": res.content}],
        }

    def give_reminder(self, state: TherapySessionState):
        turns_left = self.configs.max_turns - self.num_turns
        print(f"Reminder: {turns_left} turns left in the session.")
        return {
            "msg": state["msg"]
            + f"\n[Moderator] You have {turns_left} turns left in the session. Try to wrap up the conversation."
        }

    def check_session_end(self, state: TherapySessionState):
        if state["msg"] == "Session has ended.":
            return "END"
        turns_left = self.configs.max_turns - self.num_turns
        if self.num_turns >= self.configs.max_turns:
            print("=" * 50)
            return "END"
        elif turns_left <= self.configs.reminder_turn_num:
            return "REMIND"

        return "CONTINUE"

    def end_session(self, state: TherapySessionState):
        # print("> Generating session feedback...", end="", flush=True)
        # feedback = self.evaluator.generate(state["messages"]).model_dump(mode="json")
        # print(f"\r{' ' * 50}\r> Generated session feedback", end="\n")
        # summary = self.therapist.generate_summary()
        # print("> Generated summary")
        # feedback = self.client.generate_feedback()
        # print("> Generated feedback")
        session_state = {
            "profile": self.client.data,
            "messages": state["messages"],
            "num_turns": self.num_turns,
            # "summary": summary.model_dump(mode="json"),
            # "agenda": self.therapist.agenda.model_dump(mode="json"),
            # "feedback": feedback,
        }
        save_json(session_state, self.configs.output_dir)

        return {
            # "summary": summary.summary,
            "msg": "[Moderator] Session has ended.",
        }

    def load_graph_configs(self):
        lg_config = {"recursion_limit": self.configs.recursion_limit}
        if self.configs.langfuse:
            from langfuse.langchain import CallbackHandler

            session_handler = CallbackHandler()
            lg_config["callbacks"] = [session_handler]
        return lg_config

    def start(self):
        graph_configs = self.load_graph_configs()
        self.graph.invoke(input={}, config=graph_configs)

    def reset(self):
        self.messages = []
        self.num_turns = 0
        self.client.reset()
        self.therapist.reset()
