import re
import random
from dataclasses import dataclass
from patienthub.base import ChatAgent
from typing import Any, List, Tuple, Dict, Optional


@dataclass
class ElizaTherapistConfig:
    """Configuration for Eliza Therapist agent."""

    agent_type: str = "eliza"
    lang: str = "en"


class ElizaTherapist(ChatAgent):
    """
    A simple implementation of the ELIZA chatbot therapist.

    ELIZA was one of the first chatbots, created by Joseph Weizenbaum at MIT
    in 1964-1966. It simulates a Rogerian psychotherapist using pattern matching.
    """

    PATTERNS: List[Tuple[str, List[str]]] = [
        (
            r"hello|hi|hey",
            [
                "Hello... I'm glad you could drop by today.",
                "Hi there... how are you today?",
                "Hello... what seems to be troubling you?",
            ],
        ),
        (
            r"how are you",
            [
                "I'm doing well, but let's focus on you.",
                "Fine, thank you. How about you?",
            ],
        ),
        (
            r"I need (.*)",
            [
                "Why do you need {0}?",
                "Would it really help if you had {0}?",
                "Are you sure you need {0}?",
            ],
        ),
        (
            r"why don'?t you (.*)",
            [
                "Do you really think I don't {0}?",
                "Perhaps eventually I will {0}.",
                "Do you want me to {0}?",
            ],
        ),
        (
            r"why can'?t I (.*)",
            [
                "Do you think you should be able to {0}?",
                "If you could {0}, what would you do?",
            ],
        ),
        (
            r"I can'?t (.*)",
            [
                "How do you know you can't {0}?",
                "Perhaps you could {0} if you tried.",
                "What would it take for you to {0}?",
            ],
        ),
        (
            r"I'?m (.*)",
            [
                "How does being {0} make you feel?",
                "Do you enjoy being {0}?",
                "Did you come to me because you are {0}?",
                "How long have you been {0}?",
            ],
        ),
        (
            r"you'?re (.*)",
            [
                "What makes you think I am {0}?",
                "Does it please you to believe I am {0}?",
                "Why do you say I'm {0}?",
            ],
        ),
        (
            r"(.*)\b(mother|mom)\b(.*)",
            [
                "Tell me more about your mother.",
                "What is your relationship with your mother like?",
            ],
        ),
        (
            r"(.*)\b(father|dad)\b(.*)",
            [
                "Tell me more about your father.",
                "How does your father make you feel?",
            ],
        ),
        (
            r"(.*)\bchild(.*)",
            [
                "Did you have close friends as a child?",
                "What is your favorite childhood memory?",
            ],
        ),
        (
            r"(.*)\?$",
            [
                "Why do you ask that?",
                "Please consider whether you can answer your own question.",
                "Perhaps the answer lies within yourself?",
            ],
        ),
        (
            r"^yes\b",
            [
                "You seem quite sure.",
                "OK, but can you elaborate a bit?",
            ],
        ),
        (
            r"^no\b",
            [
                "Why not?",
                "You are being a bit negative.",
                "Are you saying no just to be negative?",
            ],
        ),
        (
            r"(.*)\bsorry\b(.*)",
            [
                "There are many times when no apology is needed.",
                "What feelings do you have when you apologize?",
            ],
        ),
    ]

    FALLBACK_RESPONSES: List[str] = [
        "Please tell me more.",
        "Let's change focus a bit... Tell me about your family.",
        "Can you elaborate on that?",
        "I see. And what does that tell you?",
        "How does that make you feel?",
        "Very interesting.",
    ]

    REFLECTIONS: Dict[str, str] = {
        "i": "you",
        "me": "you",
        "my": "your",
        "am": "are",
        "you": "I",
        "your": "my",
        "mine": "yours",
        "myself": "yourself",
        "yourself": "myself",
        "are": "am",
        "was": "were",
        "were": "was",
        "i'm": "you are",
        "you're": "I am",
        "i've": "you have",
        "you've": "I have",
        "i'll": "you will",
        "you'll": "I will",
    }

    def __init__(self, configs: Any = None) -> None:
        self.configs = configs
        self.name = "Eliza"
        self.client_name: Optional[str] = None
        self.is_first_message = True

    def set_client(self, client: Dict) -> None:
        """Set the client information."""
        self.client_name = client.get("name", "Client")

    def preprocess(self, text: str) -> str:
        """Normalize input text by removing extra whitespace and client name."""
        if self.client_name:
            text = text.replace(self.client_name, "")
        return re.sub(r"\s+", " ", text).strip()

    def reflect(self, text: str) -> str:
        """Swap first/second person pronouns for more natural responses."""
        tokens = text.lower().split()
        return " ".join(self.REFLECTIONS.get(token, token) for token in tokens)

    def format_response(self, response: str, match: re.Match) -> str:
        """Format response with reflected captured group."""
        if "{0}" not in response:
            return response
        phrase = match.group(1) if match.lastindex else ""
        return response.format(self.reflect(phrase))

    def match_pattern(self, text: str) -> str:
        """Find matching pattern and generate appropriate response."""
        for pattern, responses in self.PATTERNS:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                response = random.choice(responses)
                return self.format_response(response, match)
        return random.choice(self.FALLBACK_RESPONSES)

    def generate_response(self, msg: str) -> str:
        """Generate a response for a single message string."""
        if self.is_first_message:
            self.is_first_message = False
            return "Hello. How can I help you today?"
        else:
            text = self.preprocess(msg)
            content = self.match_pattern(text)
            return content

    def reset(self) -> None:
        """Reset the therapist to initial state."""
        self.is_first_message = True
        self.client_name = None
