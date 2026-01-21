from dataclasses import dataclass
from typing import TypedDict, List, Dict, Any, Optional

from patienthub.utils import save_json

from langgraph.graph import StateGraph, START, END


@dataclass
class InterviewConfig:
    """Configuration for an interview event."""

    event_type: str = "interview"
    num_questions: int = 5
    langfuse: bool = False
    output_dir: str = "data/interviews/default/interview_1.json"


class InterviewState(TypedDict):
    questions: List[str]
    answers: List[str]
    current_question: Optional[str]
    msg: Optional[str]


class Interview:
    def __init__(self, configs: Dict[str, Any]):
        self.configs = configs

        self.current_question_idx = 0
        self.graph = self.build_graph()

    def set_characters(self, characters: Dict[str, Any]):
        try:
            self.interviewer = characters["interviewer"]
            self.interviewee = characters["interviewee"]
        except KeyError as e:
            raise ValueError(f"Missing character in interview: {e}")

    def build_graph(self):
        # The interview graph
        graph = StateGraph(InterviewState)

        # Nodes for the graph
        graph.add_node("initiate_interview", self.init_interview)
        graph.add_node("ask_question", self.ask_question)
        graph.add_node("receive_answer", self.receive_answer)
        graph.add_node("end_interview", self.end_interview)

        # Edges for the graph
        graph.add_edge(START, "initiate_interview")
        graph.add_edge("initiate_interview", "ask_question")
        graph.add_edge("ask_question", "receive_answer")
        graph.add_edge(
            "receive_answer", "ask_question", condition=self.has_more_questions
        )
        graph.add_edge(
            "receive_answer",
            "end_interview",
            condition=lambda state: not self.has_more_questions(state),
        )
        graph.add_edge("end_interview", END)

        return graph

    def init_interview(self, state: InterviewState):
        self.current_question_idx = 0
        return {
            "questions": [],
            "answers": [],
            "current_question": None,
            "msg": "The interview is starting.",
        }

    def ask_question(self, state: InterviewState):
        question = self.interviewer.generate_question()
        self.current_question_idx += 1
        return {
            "questions": state["questions"] + [question],
            "answers": state["answers"],
            "current_question": question,
            "msg": f"Interviewer: {question}",
        }

    def receive_answer(self, state: InterviewState):
        answer = self.interviewee.generate_answer(state["current_question"] or "")
        return {
            "questions": state["questions"],
            "answers": state["answers"] + [answer],
            "current_question": None,
            "msg": f"Interviewee: {answer}",
        }

    def has_more_questions(self, state: InterviewState) -> bool:
        return self.current_question_idx < self.configs.num_questions

    def end_interview(self, state: InterviewState):
        if self.configs.langfuse:
            save_json(
                {
                    "questions": state["questions"],
                    "answers": state["answers"],
                },
                self.configs.output_dir,
            )
        return {
            "questions": state["questions"],
            "answers": state["answers"],
            "current_question": None,
            "msg": "The interview has ended.",
        }
