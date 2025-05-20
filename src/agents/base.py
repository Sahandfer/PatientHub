from abc import ABC, abstractmethod


class BaseAgent(ABC):
    def __init__(self, role: str, client):
        self.role = role
        self.client = client
        self.messages = []
        self.memory = []

    def reset_messages(self):
        self.messages = []

    def add_message(self, msg):
        self.messages.append(msg)

    def remove_message(self, idx):
        if idx < len(self.messages):
            self.messages.pop(idx)

    def edit_message(self, idx, msg):
        if idx < len(self.messages):
            self.messages[idx] = msg

    # @abstractmethod
    # def reset(self):
    #     """Reset the agent's state."""
    #     pass
