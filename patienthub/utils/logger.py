import json
import os
import sys
import logging
from datetime import datetime, timezone
from threading import Lock
from typing import Any, Dict

from litellm import completion_cost


def default_trace_log_path(output_dir: str) -> str:
    if output_dir.endswith(".json"):
        return f"{output_dir[:-5]}.agent.log"
    return f"{output_dir}.agent.log"


def get_logger(name: str) -> logging.Logger:
    """Get a configured logger."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(
            logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        )
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    return logger


class AgentTraceLogger:
    """Small JSONL logger for per-run agent tracing."""

    _write_lock = Lock()

    def __init__(
        self,
        log_path: str,
        enabled: bool = True,
        include_messages: bool = True,
        include_raw_text: bool = True,
        include_parsed_output: bool = True,
        max_content_chars: int | None = 20000,
        context: Dict[str, Any] | None = None,
    ):
        self.log_path = log_path
        self.enabled = enabled
        self.include_messages = include_messages
        self.include_raw_text = include_raw_text
        self.include_parsed_output = include_parsed_output
        self.max_content_chars = max_content_chars
        self.context = context or {}

    def bind(self, **context) -> "AgentTraceLogger":
        return AgentTraceLogger(
            log_path=self.log_path,
            enabled=self.enabled,
            include_messages=self.include_messages,
            include_raw_text=self.include_raw_text,
            include_parsed_output=self.include_parsed_output,
            max_content_chars=self.max_content_chars,
            context={**self.context, **context},
        )

    def log_event(self, event_type: str, payload: Dict[str, Any] | None = None) -> None:
        if not self.enabled:
            return

        parent_dir = os.path.dirname(self.log_path)
        if parent_dir:
            os.makedirs(parent_dir, exist_ok=True)

        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "event": event_type,
            **self.context,
            **self._serialize(payload or {}),
        }

        with self._write_lock:
            with open(self.log_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

    def log_llm_call(
        self,
        *,
        model_name: str,
        messages: Any,
        response_format: Any = None,
        response: Any = None,
        raw_response: Any = None,
        latency_ms: float | None = None,
    ) -> None:
        payload = {
            "model": model_name,
            "response_format": self._format_name(response_format),
        }
        usage = self._extract_usage(raw_response)
        cost = self._extract_cost(raw_response)
        raw_output = self._extract_raw_output(raw_response or response)
        parsed_output = self._extract_parsed_output(response)
        if latency_ms is not None:
            payload["latency_ms"] = round(latency_ms, 2)
        if usage:
            payload["usage"] = usage
        if cost is not None:
            payload["cost"] = round(cost, 6)
        if self.include_messages:
            payload["messages"] = messages
        if self.include_raw_text and raw_output not in (None, ""):
            payload["raw_output"] = raw_output
        if self.include_parsed_output and parsed_output is not None:
            payload["parsed_output"] = parsed_output

        self.log_event("llm_call", payload)

    def log_llm_error(
        self,
        *,
        model_name: str,
        messages: Any,
        response_format: Any = None,
        error: Exception,
        latency_ms: float | None = None,
    ) -> None:
        payload = {
            "model": model_name,
            "response_format": self._format_name(response_format),
            "error": str(error),
            "error_type": type(error).__name__,
        }
        if latency_ms is not None:
            payload["latency_ms"] = round(latency_ms, 2)
        if self.include_messages:
            payload["messages"] = messages

        self.log_event("llm_call_error", payload)

    def _format_name(self, value: Any) -> str | None:
        if value is None:
            return None
        return getattr(value, "__name__", value.__class__.__name__)

    def _extract_usage(self, response: Any) -> Dict[str, int]:
        if hasattr(response, "usage") and response.usage:
            return {
                "prompt_tokens": response.usage.prompt_tokens or 0,
                "completion_tokens": response.usage.completion_tokens or 0,
                "total_tokens": response.usage.total_tokens or 0,
            }
        return {}

    def _extract_cost(self, response: Any) -> float | None:
        try:
            return completion_cost(completion_response=response)
        except Exception:
            return None

    def _extract_raw_output(self, response: Any) -> Any:
        if response is None:
            return None
        if hasattr(response, "choices"):
            try:
                return self._extract_raw_output(response.choices[0].message)
            except Exception:
                return None
        if hasattr(response, "content"):
            return response.content
        return response if isinstance(response, str) else None

    def _extract_parsed_output(self, response: Any) -> Any:
        if hasattr(response, "model_dump"):
            return response.model_dump()
        return None

    def _truncate(self, value: str) -> str:
        if self.max_content_chars is None or len(value) <= self.max_content_chars:
            return value
        return value[: self.max_content_chars] + "...<truncated>"

    def _serialize(self, value: Any) -> Any:
        if value is None or isinstance(value, (bool, int, float)):
            return value
        if isinstance(value, str):
            return self._truncate(value)
        if isinstance(value, dict):
            return {k: self._serialize(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [self._serialize(v) for v in value]
        if hasattr(value, "model_dump"):
            return self._serialize(value.model_dump())
        if hasattr(value, "role") or hasattr(value, "content"):
            return self._serialize(
                {
                    "role": getattr(value, "role", None),
                    "content": getattr(value, "content", None),
                }
            )
        return self._truncate(repr(value))
