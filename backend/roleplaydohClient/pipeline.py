import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple, Union

import yaml
from langchain_core.language_models import BaseChatModel

DEFAULT_CONSISTENCY_QUESTION = "Is the client's response consistent with the given conversation history?"


def _load_prompt_blocks(path: Path) -> Dict[str, str]:
    with path.open("r", encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    prompts: Dict[str, str] = {}
    for key, block in data.items():
        if isinstance(block, str):
            prompts[str(key)] = block.strip()
    return prompts


def _load_principles(path: Path) -> Dict[str, List[str]]:
    with path.open("r", encoding="utf-8") as fh:
        data = json.load(fh)
    return {str(k): v for k, v in data.items()}


def _safe_json_loads(payload: str) -> Dict[str, Any]:
    try:
        return json.loads(payload)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", payload, re.DOTALL)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                return {}
    return {}


class RoleplayDohPipeline:
    """Implements Roleplay-doh style self-critique for client responses."""

    def __init__(
        self,
        prompt_file: Path,
        principles_file: Path,
        response_model: BaseChatModel,
        question_model: Optional[BaseChatModel] = None,
        revision_model: Optional[BaseChatModel] = None,
        verbose: bool = False,
        log_file: Optional[Union[str, Path]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.prompt_file = prompt_file
        self.prompts = _load_prompt_blocks(prompt_file)
        self.principles = _load_principles(principles_file)
        self.response_model = response_model
        self.question_model = question_model or response_model
        self.revision_model = revision_model or response_model
        self.verbose = verbose
        self.context = context or {}
        self.log_file = Path(log_file) if log_file else None
        if self.log_file:
            self.log_file.parent.mkdir(parents=True, exist_ok=True)

    def _log(self, message: str) -> None:
        if self.verbose:
            print(f"[RoleplayDoh] {message}")

    def update_context(self, **kwargs: Any) -> None:
        self.context.update({k: v for k, v in kwargs.items() if v is not None})

    def _describe_model(self, model: BaseChatModel) -> str:
        return getattr(model, "model_name", None) or model.__class__.__name__

    def _log_to_file(self, stage: str, payload: Dict[str, Any]) -> None:
        if not self.log_file:
            return
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "stage": stage,
            "context": self.context,
            **payload,
        }
        try:
            with self.log_file.open("a", encoding="utf-8") as fh:
                fh.write(json.dumps(entry, ensure_ascii=False))
                fh.write("\n")
        except Exception:
            pass

    def select_principles(
        self, principle_ids: Optional[Iterable[str]] = None
    ) -> Dict[str, List[str]]:
        selected: Dict[str, List[str]] = {}
        if principle_ids:
            for pid in principle_ids:
                key = str(pid)
                criteria = self.principles.get(key)
                if criteria:
                    selected[key] = criteria
        else:
            selected = dict(self.principles)

        if not selected:
            selected = {
                "default": [
                    "Ensure the client's response remains consistent with the established persona and conversation context."
                ]
            }
        return selected

    def _choose_principle_bundle(
        self, principles_map: Dict[str, List[str]]
    ) -> Tuple[str, List[str]]:
        for key, criteria in principles_map.items():
            if criteria:
                return key, criteria
        return "default", [
            "Ensure the client's response remains consistent with the established persona and conversation context."
        ]

    def generate_initial_response(self, system_prompt: str, transcript: str) -> str:
        template = self.prompts.get("Initial_Response_Prompt", "")
        prompt = template.format(system_prompt=system_prompt, transcript=transcript)
        result = self.response_model.invoke(prompt)
        content = getattr(result, "content", result)
        self._log(f"Initial response generated with {len(transcript.splitlines())} history lines.")
        self._log_to_file(
            "initial_response",
            {
                "model": self._describe_model(self.response_model),
                "inputs": {
                    "system_prompt": system_prompt,
                    "transcript": transcript,
                },
                "output": content,
            },
        )
        return content.strip()

    def generate_questions(
        self,
        principles_map: Dict[str, List[str]],
        therapist_message: str,
        client_response: str,
    ) -> Dict[str, Any]:
        template = self.prompts.get("Question_Rewrite_Prompt", "")
        if not isinstance(principles_map, dict):
            principles_map = {
                "default": list(principles_map) if principles_map else []
            }
        selected_key, selected_criteria = self._choose_principle_bundle(principles_map)
        criteria_payload = json.dumps(
            {selected_key: selected_criteria}, ensure_ascii=False, indent=2
        )
        prompt = template.format(
            criteria_payload=criteria_payload,
            therapist_message=therapist_message,
            client_response=client_response,
        )
        raw = self.question_model.invoke(prompt)
        content = getattr(raw, "content", raw)
        payload = _safe_json_loads(content)
        result = payload.get("result", payload)
        questions = result.get("questions", [])
        extra_questions = (
            result.get("extra questions", result.get("extra_questions", [])) or []
        )
        extra_justification = result.get(
            "extra_questions_justification", result.get("extra questions justification", [])
        ) or []
        self._log(
            f"Generated {len(questions)} main questions and {len(extra_questions)} extra questions."
        )
        self._log_to_file(
            "question_generation",
            {
                "model": self._describe_model(self.question_model),
                "inputs": {
                    "principles": {selected_key: selected_criteria},
                    "therapist_message": therapist_message,
                    "client_response": client_response,
                },
                "output": {
                    "questions": questions,
                    "extra_questions": extra_questions,
                    "extra_justification": extra_justification,
                    "raw": payload or content,
                    "principle_id": selected_key,
                },
            },
        )
        return {
            "raw": payload or content,
            "questions": questions,
            "extra_questions": extra_questions,
            "extra_justification": extra_justification,
            "principle_id": selected_key,
        }

    def assess_and_rewrite(
        self,
        question_list: List[str],
        persona: str,
        conversation_history: str,
        therapist_message: str,
        client_response: str,
    ) -> Dict[str, Any]:
        template = self.prompts.get("Assess_Revise_Prompt", "")
        if "Assess_Revise_Prompt" not in self.prompts:
            return {
                "answers": [],
                "justification": [],
                "response": client_response,
                "reasoning": "",
            }
        questions = list(question_list) if question_list else []
        if not questions:
            questions = [DEFAULT_CONSISTENCY_QUESTION]
        criteria_lines = "\n".join(
            f"{idx}. {question}" for idx, question in enumerate(questions, start=1)
        )
        prompt = template.format(
            criteria_lines=criteria_lines,
            persona=persona,
            conversation_history=conversation_history or "No previous conversation.",
            therapist_message=therapist_message,
            client_response=client_response,
        )
        raw = self.revision_model.invoke(prompt)
        content = getattr(raw, "content", raw)
        payload = _safe_json_loads(content)
        result = payload.get("result", payload)
        rewritten = result.get("response")
        changed = bool(rewritten) and rewritten.strip() != client_response.strip()
        self._log(
            f"Assessment answers: {len(result.get('answers', []))}; "
            f"response rewritten: {changed}"
        )
        self._log_to_file(
            "assessment_revision",
            {
                "model": self._describe_model(self.revision_model),
                "inputs": {
                    "questions": question_list,
                    "persona": persona,
                    "conversation_history": conversation_history,
                    "therapist_message": therapist_message,
                    "client_response": client_response,
                },
                "output": {
                    "answers": result.get("answers", []),
                    "justification": result.get("justification", []),
                    "response": rewritten,
                    "reasoning": result.get("reasoning", ""),
                    "raw": payload or content,
                },
            },
        )
        return {
            "raw": payload or content,
            "answers": result.get("answers", []),
            "justification": result.get("justification", []),
            "response": result.get("response") or client_response,
            "reasoning": result.get("reasoning", ""),
        }
