import re
import random
from agents import BaseAgent
from pydantic import BaseModel, Field
from typing import Dict, List, Any
from langchain_core.messages import AIMessage, HumanMessage


class BaseElizaResponse(BaseModel):
    content: str = Field(
        description="The content of your generated response based on the client's input"
    )


class ElizaTherapist(BaseAgent):
    def __init__(self, data: Dict[str, Any]):
        self.role = "therapist"
        self.agent_type = "eliza"
        self.name = data["demographics"]["name"]
        self.data = data
        self.messages = []
        self.patterns = [
            (
                r"hello(.*)",
                [
                    "Hello... I'm glad you could drop by today.",
                    "Hi there... how are you today?",
                ],
            ),
            (
                r"hi(.*)",
                [
                    "Hello... what seems to be troubling you?",
                    "Hi... let's talk about what's on your mind.",
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
                r"why don\'t you (.*)",
                [
                    "Do you really think I don't {0}?",
                    "Perhaps eventually I will {0}.",
                    "Do you want me to {0}?",
                ],
            ),
            (
                r"why can\'t I (.*)",
                [
                    "Do you think you should be able to {0}?",
                    "If you could {0}, what would you do?",
                ],
            ),
            (
                r"I can\'t (.*)",
                [
                    "How do you know you can't {0}?",
                    "Perhaps you could {0} if you tried.",
                    "What would it take for you to {0}?",
                ],
            ),
            (
                r"I am (.*)",
                [
                    "Did you come to me because you are {0}?",
                    "How long have you been {0}?",
                    "How do you feel about being {0}?",
                ],
            ),
            (
                r"I\'m (.*)",
                ["How does being {0} make you feel?", "Do you enjoy being {0}?"],
            ),
            (
                r"you are (.*)",
                [
                    "What makes you think I am {0}?",
                    "Does it please you to believe I am {0}?",
                    "Perhaps you would like to be {0}?",
                ],
            ),
            (r"you\'re (.*)", ["Why do you say I'm {0}?", "Why do you think I'm {0}?"]),
            (
                r"(.*) mother(.*)",
                [
                    "Tell me more about your mother.",
                    "What is your relationship with your mother like?",
                ],
            ),
            (
                r"(.*) father(.*)",
                [
                    "Tell me more about your father.",
                    "How does your father make you feel?",
                ],
            ),
            (
                r"(.*) child(.*)",
                [
                    "Did you have close friends as a child?",
                    "What is your favorite childhood memory?",
                ],
            ),
            (
                r"(.*)\?",
                [
                    "Why do you ask that?",
                    "Please consider whether you can answer your own question.",
                    "Perhaps the answer lies within yourself?",
                ],
            ),
            (r"yes", ["You seem quite sure.", "OK, but can you elaborate a bit?"]),
            (
                r"no",
                [
                    "Why not?",
                    "You are being a bit negative.",
                    "Are you saying no just to be negative?",
                ],
            ),
            (
                r"(.*) computer(.*)",
                [
                    "Are you really talking about me?",
                    "Does it seem strange to talk to a computer?",
                    "How do computers make you feel?",
                ],
            ),
            (
                r"(.*) name(.*)",
                [
                    "Names don't interest me.",
                    "I don't care about names -- please go on.",
                ],
            ),
            (
                r"(.*) sorry(.*)",
                [
                    "There are many times when no apology is needed.",
                    "What feelings do you have when you apologize?",
                ],
            ),
            (
                r"(.*)",
                [
                    "Please tell me more.",
                    "Let's change focus a bit... Tell me about your family.",
                    "Can you elaborate on that?",
                    "Why do you say that {0}?",
                    "I see.",
                    "Very interesting.",
                    "{0}.",
                    "I see. And what does that tell you?",
                    "How does that make you feel?",
                    "How do you feel when you say that?",
                ],
            ),
        ]
        self.reflections = {
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

    def set_client(self, client, prev_sessions: List[Dict[str, str] | None] = []):
        self.client = client.data["demographics"]

    def reflect(self, fragment):
        tokens = fragment.lower().split()
        for i, token in enumerate(tokens):
            if token in self.reflections:
                tokens[i] = self.reflections[token]
        return " ".join(tokens)

    def preprocess(self, statement):
        # Remove punctuation and extra spaces
        statement = statement.replace(self.client["name"], "")
        statement = re.sub(r"[^\w\s]", "", statement)
        statement = re.sub(r"\s+", " ", statement).strip()
        return statement

    def generate(
        self, messages: List[str], response_format: BaseModel = BaseElizaResponse
    ):
        if len(self.messages) == 1:
            return response_format(content="Hello. How can I help you today?")
        msg = self.preprocess(messages[-1].content)
        for pattern, responses in self.patterns:
            match = re.match(pattern, msg.rstrip(".!"), re.IGNORECASE)
            if match:
                response = random.choice(responses)
                if "{0}" in response:
                    phrase = self.reflect(
                        match.group(1) if len(match.groups()) > 0 else ""
                    )
                    response = response.format(phrase)
                return response_format(content=response)
        return response_format(content="I'm not sure I understand you fully.")

    def generate_response(self, msg: str):
        self.messages.append(HumanMessage(content=msg))
        res = self.generate(messages=self.messages, response_format=BaseElizaResponse)
        self.messages.append(AIMessage(content=res.model_dump_json()))

        return res

    def reset(self):
        self.agent.reset()
