from typing import Dict, Any
from datetime import datetime
from dataclasses import dataclass
from colorama import Fore, Style, init
from patienthub.utils import save_json
from burr.core import ApplicationBuilder, State, action, when, expr

init(autoreset=True)


@dataclass
class TherapySessionConfig:
    """Configuration for a therapy session."""

    event_type: str = "therapySession"
    reminder_turn_num: int = 5
    max_turns: int = 30
    output_dir: str = "data/sessions/default/session_1.json"


@action(reads=[], writes=["messages", "msg", "initialized"])
def init_session(state: State, therapist, client) -> State:
    """Initialize the therapy session."""
    therapist.set_client({"name": client.name})
    client.set_therapist({"name": therapist.name})

    print("=" * 50)
    return state.update(
        messages=[],
        msg="[Moderator] You may start the session now.",
        initialized=True,
    )


@action(reads=["msg", "messages", "num_turns"], writes=["msg", "messages"])
def generate_therapist_response(state: State, therapist, max_turns) -> State:
    """Generate therapist's response."""
    name = therapist.name
    res = therapist.generate_response(state["msg"])
    res = res.content if not isinstance(res, str) else res

    print(f"--- Turn # {state['num_turns'] + 1}/{max_turns} ---")
    print(f"{Fore.CYAN}{Style.BRIGHT}{name}{Style.RESET_ALL}: {res}")

    return state.update(
        msg=f"{name}: {res}",
        messages=state["messages"] + [{"role": "therapist", "content": res}],
    )


@action(
    reads=["msg", "messages", "num_turns"],
    writes=["msg", "messages", "num_turns", "session_ended"],
)
def generate_client_response(state: State, therapist, client) -> State:
    """Generate client's response."""
    # Check if therapist ended the session
    therapist_msg = state["msg"].replace(f"{therapist.name}: ", "")
    if therapist_msg in ["END", "end", "exit"]:
        return state.update(
            msg="The therapist has ended the session.",
            messages=state["messages"][:-1],
            session_ended=True,
        )

    name = client.name
    res = client.generate_response(state["msg"])
    res = res.content if not isinstance(res, str) else res
    print(f"{Fore.RED}{Style.BRIGHT}{name}{Style.RESET_ALL}: {res}")

    return state.update(
        msg=f"{name}: {res}",
        messages=state["messages"] + [{"role": "client", "content": res}],
        num_turns=state["num_turns"] + 1,
        session_ended=False,
    )


@action(reads=["msg", "num_turns"], writes=["msg", "needs_reminder"])
def check_and_remind(state: State, max_turns, reminder_turn_num) -> State:
    """Check if reminder is needed and update state."""
    turns_left = max_turns - state["num_turns"]
    needs_reminder = 0 < turns_left <= reminder_turn_num

    if needs_reminder:
        print(f"Reminder: {turns_left} turns left in the session.")
        return state.update(
            msg=state["msg"]
            + f"\n[Moderator] You have {turns_left} turns left in the session. Try to wrap up the conversation.",
            needs_reminder=True,
        )

    return state.update(needs_reminder=False)


@action(reads=["messages", "num_turns"], writes=["msg"])
def end_session(state: State, client, output_dir) -> State:
    """End the session and save results."""
    session_state = {
        "profile": client.data,
        "messages": state["messages"],
        "num_turns": state["num_turns"],
    }
    save_json(session_state, output_dir)

    print("=" * 50)
    return state.update(msg="[Moderator] Session has ended.")


class TherapySession:
    def __init__(self, configs: TherapySessionConfig):
        self.configs = configs
        self.client = None
        self.therapist = None
        self.evaluator = None
        self.app = None

    def set_characters(self, characters: Dict[str, Any]):
        try:
            self.client = characters["client"]
            self.therapist = characters["therapist"]
            self.evaluator = characters.get("evaluator", None)
        except KeyError as e:
            raise ValueError(f"Missing character in session: {e}")

    def build_app(self):
        """Build the Burr application."""
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        app = (
            ApplicationBuilder()
            .with_actions(
                init_session=init_session.bind(
                    therapist=self.therapist, client=self.client
                ),
                generate_therapist_response=generate_therapist_response.bind(
                    therapist=self.therapist, max_turns=self.configs.max_turns
                ),
                generate_client_response=generate_client_response.bind(
                    therapist=self.therapist, client=self.client
                ),
                check_and_remind=check_and_remind.bind(
                    max_turns=self.configs.max_turns,
                    reminder_turn_num=self.configs.reminder_turn_num,
                ),
                end_session=end_session.bind(
                    client=self.client, output_dir=self.configs.output_dir
                ),
            )
            .with_transitions(
                ("init_session", "generate_therapist_response"),
                ("generate_therapist_response", "generate_client_response"),
                (
                    "generate_client_response",
                    "end_session",
                    when(session_ended=True),
                ),
                (
                    "generate_client_response",
                    "end_session",
                    expr(f"num_turns >= {self.configs.max_turns}"),
                ),
                ("generate_client_response", "check_and_remind"),
                ("check_and_remind", "generate_therapist_response"),
            )
            .with_entrypoint("init_session")
            .with_state(
                messages=[],
                msg="",
                num_turns=0,
                session_ended=False,
                initialized=False,
                needs_reminder=False,
            )
            .with_tracker(project="patienthub")  # Enables local tracking
            .with_identifiers(app_id=f"therapy_session_{run_id}")
            .build()
        )
        return app

    def start(self):
        """Run the therapy session."""
        self.app = self.build_app()

        # Run until end_session is reached
        while True:
            action, result, state = self.app.step()
            if action.name == "end_session":
                break

    def reset(self):
        """Reset the session state."""
        self.app = None
        self.client.reset()
        self.therapist.reset()
