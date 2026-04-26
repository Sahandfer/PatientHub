from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict

from patienthub.utils.logger import AgentTraceLogger, default_trace_log_path


@dataclass
class EventTraceConfig:
    trace_enabled: bool = True
    trace_log_path: str = ""
    trace_include_messages: bool = False
    trace_include_raw_text: bool = True
    trace_include_parsed_output: bool = True
    trace_max_content_chars: int = 20000


class TraceableEvent:
    def __init__(self, configs: Any):
        self.configs = configs
        self.run_id = ""
        self.trace_logger = None
        self.trace_log_path = ""

    def ensure_run_id(self) -> str:
        if not self.run_id:
            self.run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.run_id

    def setup_trace_logger(
        self,
        *,
        output_dir: str,
        agents: Dict[str, Any] | None = None,
    ) -> None:
        self.ensure_run_id()
        if not getattr(self.configs, "trace_enabled", False):
            self.trace_logger = None
            self.trace_log_path = ""
            return

        self.trace_log_path = (
            getattr(self.configs, "trace_log_path", "")
            or default_trace_log_path(output_dir)
        )
        self.trace_logger = AgentTraceLogger(
            log_path=self.trace_log_path,
            include_messages=getattr(self.configs, "trace_include_messages", True),
            include_raw_text=getattr(self.configs, "trace_include_raw_text", True),
            include_parsed_output=getattr(
                self.configs, "trace_include_parsed_output", True
            ),
            max_content_chars=getattr(self.configs, "trace_max_content_chars", 20000),
        ).bind(run_id=self.run_id)

        for role, agent in (agents or {}).items():
            self.attach_agent_trace_logger(role, agent)

        run_start_payload = {
            "event_type": getattr(
                self.configs, "event_type", self.__class__.__name__
            ),
            "output_dir": output_dir,
        }
        for role, agent in (agents or {}).items():
            run_start_payload[f"{role}_agent"] = self.get_agent_identifier(agent)

        self.trace_logger.log_event(
            "run_start",
            run_start_payload,
        )

    def attach_agent_trace_logger(self, role: str, agent: Any) -> None:
        chat_model = getattr(agent, "chat_model", None)
        if chat_model and hasattr(chat_model, "attach_trace_logger"):
            chat_model.attach_trace_logger(
                self.trace_logger.bind(
                    agent_role=role,
                    agent_name=getattr(agent, "name", agent.__class__.__name__),
                )
            )

    def get_agent_identifier(self, agent: Any) -> str:
        configs = getattr(agent, "configs", None)
        identifier = getattr(configs, "agent_name", None)
        if identifier:
            return identifier
        return agent.__class__.__name__

    def log_trace_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        if self.trace_logger:
            self.trace_logger.log_event(event_type, payload)
