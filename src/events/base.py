from abc import ABC, abstractmethod
from datetime import datetime


class BaseEvent(ABC):
    def __init__(self, event_type: str, data: dict):
        self.start_time = datetime.now()

    @abstractmethod
    def process_event(self):
        """Process the event and return a result."""
        pass
