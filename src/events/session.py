from datetime import datetime
from typing import Dict
from camel.agents import BaseAgent
from camel.messages import BaseMessage
from camel.types import RoleType


class TherapySession:
    def __init__(
        self, characters: Dict[str, BaseAgent], max_turns=1, reminder_turn_num=2
    ):
        self.characters = characters
        self.messages = []
        self.num_turns = 0
        self.max_turns = max_turns
        self.reminder_turn_num = reminder_turn_num

    def get_message(self, role: str, content: str):
        return BaseMessage(
            role_name=role,
            role_type=RoleType.USER,
            content=content,
            meta_dict={},
        )

    def generate_response(self, role: str, msg: str):
        res = self.characters[role].generate_response(msg)
        self.messages.append({"role": role, "content": res.get("response")})
        return self.get_message(role, f"{role}: {res.get('response')}")

    def simulate(self):
        self.characters["Therapist"].create_agenda()
        self.characters["Client"].init_mental_state()

        msg = self.get_message("Moderator", "You may start the session now.")

        for i in range(self.max_turns):
            msg = self.generate_response("Therapist", msg)
            print(msg.content)
            msg = self.generate_response("Client", msg)
            print(msg.content)
            self.num_turns += 1

            turns_left = self.max_turns - self.num_turns
            if turns_left <= self.reminder_turn_num:
                moderator_msg = f"\nModerator: the time for this session is coming to an end. You have {turns_left} turns left to wrap up this session."
                msg.content += moderator_msg
                print(moderator_msg)

        msg = self.get_message(
            "Moderator",
            "The session has concluded. Please generate a summary of this session and the next steps.",
        )
