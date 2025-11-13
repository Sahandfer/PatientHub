from agents import BaseAgent

from utils import save_json
from dotenv import load_dotenv
from typing import TypedDict, List, Dict, Any, Optional
from langgraph.graph import StateGraph, START, END
from colorama import Fore, Style, init

load_dotenv(".env")
init(autoreset=True)


class TherapySessionState(TypedDict):
    messages: List[Dict[str, Any]]
    summary: Optional[str]
    homework: Optional[List[str]]
    msg: Optional[str]


class TherapySession:
    def __init__(
        self,
        client: BaseAgent,
        therapist: BaseAgent,
        evaluator: BaseAgent,
        output_dir: str,
        max_turns: int = 1,
        reminder_turn_num: int = 2,
    ):
        self.client = client
        self.therapist = therapist
        self.evaluator = evaluator
        self.output_dir = output_dir
        self.max_turns = max_turns
        self.reminder_turn_num = reminder_turn_num
        self.num_turns = 0
        self.graph = self.build_graph()

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

    # Preparations before the interaction
    def init_session(self, state: TherapySessionState):
        # Introduce characters together
        self.therapist.set_client({"name": self.client.name})
        self.client.set_therapist({"name": self.therapist.name})
        # Create an agenda for this session
        # print("> Creating the agenda for this session...", end="", flush=True)
        # agenda = self.therapist.generate_agenda()
        # print(f"\r{' ' * 50}\r> Created agenda for this session", end="\n")
        # # Initialize client's mental states before the session
        # print("> Initializing client's mental state...", end="", flush=True)
        # self.client.init_mental_state()
        # print(f"\r{' ' * 50}\r> Initialized client's mental state", end="\n")

        print("=" * 50)
        return {
            "msg": f"[Moderator] You may start the session now, {self.therapist.name}.",
            "messages": [],
            # "agenda": agenda,
            # "agenda": None,
        }

    def generate_therapist_response(self, state: TherapySessionState):
        res = self.therapist.generate_response(state["msg"])
        print(f"--- Turn # {self.num_turns + 1}/{self.max_turns} ---")
        # print(
        #     f"{Fore.CYAN}{Style.BRIGHT}{self.therapist.name}{Style.RESET_ALL}: {res.content}"
        # )
        print(f"{Fore.CYAN}{Style.BRIGHT}咨询师{Style.RESET_ALL}: {res.content}")
        return {
            "msg": f"{self.therapist.name}: {res.content}",
            "messages": state["messages"]
            + [{"role": "Therapist", "content": res.content}],
        }

    def generate_client_response(self, state: TherapySessionState):
        if state["msg"].replace(f"{self.therapist.name}: ", "") in [
            "END",
            "end",
            "exit",
        ]:
            return {
                "msg": "Session has ended.",
                "messages": state["messages"][:-1],
            }
        res = self.client.generate_response(state["msg"])
        # print(
        #     f"{Fore.RED}{Style.BRIGHT}{self.client.name}{Style.RESET_ALL}: {res.content}"
        # )
        print(f"{Fore.RED}{Style.BRIGHT}来访者{Style.RESET_ALL}: {res.content}")
        self.num_turns += 1

        return {
            "msg": f"{self.client.name}: {res.content}",
            "messages": state["messages"]
            + [{"role": "Client", "content": res.content}],
        }

    def give_reminder(self, state: TherapySessionState):
        turns_left = self.max_turns - self.num_turns
        print(f"Reminder: {turns_left} turns left in the session.")
        return {
            "msg": state["msg"]
            + f"\nModerator: You have {turns_left} turns left in the session. Try to wrap up the conversation."
        }

    def check_session_end(self, state: TherapySessionState):
        if state["msg"] == "Session has ended.":
            return "END"
        turns_left = self.max_turns - self.num_turns
        if self.num_turns >= self.max_turns:
            print("=" * 50)
            return "END"
        elif turns_left <= self.reminder_turn_num:
            return "REMIND"

        return "CONTINUE"

    def end_session(self, state: TherapySessionState):
        print("> Generating session feedback...", end="", flush=True)
        feedback = self.evaluator.generate(state["messages"]).model_dump(mode="json")
        print(f"\r{' ' * 50}\r> Generated session feedback", end="\n")
        for k, v in feedback.items():
            if k != "dimension_feedback":
                print(f"{Fore.GREEN}{Style.BRIGHT}{k}:{Style.RESET_ALL} {v}")
            else:
                for dim, dim_feedback in v.items():
                    print(f"  {Fore.YELLOW}{Style.BRIGHT}{dim}:{Style.RESET_ALL}")
                    for fk, fv in dim_feedback.items():
                        print(
                            f"    {Fore.CYAN}{Style.BRIGHT}{fk}:{Style.RESET_ALL} {fv}"
                        )
        # summary = self.therapist.generate_summary()
        # print("> Generated summary")
        # feedback = self.client.generate_feedback()
        # print("> Generated feedback")
        session_state = {
            "messages": state["messages"],
            # "summary": summary.model_dump(mode="json"),
            "num_turns": self.num_turns,
            # "agenda": self.therapist.agenda.model_dump(mode="json"),
            "feedback": feedback,
        }
        save_json(session_state, self.output_dir)

        return {
            # "summary": summary.summary,
            "msg": "Moderator: Session has ended.",
        }

    def reset(self):
        self.messages = []
        self.num_turns = 0
        self.client.reset()
        self.therapist.reset()
