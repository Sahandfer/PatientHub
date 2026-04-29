import os
import logging
import instructor
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Any, List, Optional, Dict
from litellm import completion, supports_response_schema, completion_cost, rerank

logger = logging.getLogger(__name__)

logging.getLogger("LiteLLM").setLevel(logging.WARNING)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("instructor").setLevel(logging.WARNING)

load_dotenv()


def get_config_value(configs, name, default=None):
    # Support both DictConfig (attribute access) and dict (key access)
    if isinstance(configs, dict):
        return configs.get(name, default)
    return getattr(configs, name, default)


class ChatModel:
    def __init__(self, model_name, **kwargs):
        self.model_name = model_name
        self.kwargs = kwargs
        self.res_format_support = supports_response_schema(model=model_name)
        self.total_cost = 0.0
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0
        if not self.res_format_support:
            logger.warning("Model '%s' does not support response format", model_name)

    def track_usage(self, response):
        """Track token usage and cost from API response using LiteLLM."""
        if hasattr(response, "usage") and response.usage:
            self.prompt_tokens += response.usage.prompt_tokens or 0
            self.completion_tokens += response.usage.completion_tokens or 0
            self.total_tokens += response.usage.total_tokens or 0
        try:
            self.total_cost += completion_cost(completion_response=response)
        except Exception:
            logger.warning("Cost not available for model '%s'", self.model_name)

    def generate(self, messages, response_format=None):
        logger.debug(
            "LLM request: model=%s #messages=%d", self.model_name, len(messages)
        )
        if not self.res_format_support or response_format is None:
            res = completion(model=self.model_name, messages=messages, **self.kwargs)
            self.track_usage(res)
            result = res.choices[0].message
            logger.debug(
                "LLM response: model=%s finish_reason=%s tokens=%s",
                self.model_name,
                res.choices[0].finish_reason,
                res.usage.total_tokens if res.usage else "n/a",
            )
            return result
        else:
            client = instructor.from_litellm(completion)
            res = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_model=response_format,
                **self.kwargs,
            )
            if hasattr(res, "_raw_response"):
                self.track_usage(res._raw_response)
                logger.debug(
                    "LLM response: model=%s tokens=%s",
                    self.model_name,
                    (
                        res._raw_response.usage.total_tokens
                        if res._raw_response.usage
                        else "n/a"
                    ),
                )
            return res

    def get_usage(self) -> Dict:
        """Get usage summary."""
        return {
            "prompt_tokens": self.prompt_tokens,
            "completion_tokens": self.completion_tokens,
            "total_tokens": self.total_tokens,
            "total_cost": round(self.total_cost, 6),
        }

    def reset_usage(self):
        """Reset usage tracking."""
        self.total_cost = 0.0
        self.total_tokens = 0
        self.prompt_tokens = 0
        self.completion_tokens = 0


def get_chat_model(configs):
    def get(name, default=None):
        return get_config_value(configs, name, default)

    model_type = get("model_type")
    model_name = get("model_name")

    return ChatModel(
        model_name=model_name,
        api_base=os.environ.get(f"{model_type}_BASE_URL", None),
        api_key=os.environ.get(f"{model_type}_API_KEY", None),
    )


@dataclass
class Reranker:
    """Reranker backed by LiteLLM's hosted_vllm provider."""

    model_name: str
    api_base: Optional[str] = None
    api_key: Optional[str] = None

    @staticmethod
    def read_field(obj: Any, name: str, default: Any = None) -> Any:
        if isinstance(obj, dict):
            return obj.get(name, default)
        return getattr(obj, name, default)

    @classmethod
    def extract_scores(cls, response: Any, total_docs: int) -> Optional[List[float]]:
        scores = [0.0] * total_docs
        results = cls.read_field(response, "results", []) or []
        valid_count = 0

        for item in results:
            index = cls.read_field(item, "index")
            relevance_score = cls.read_field(item, "relevance_score")
            if relevance_score is None:
                relevance_score = cls.read_field(item, "score")

            try:
                index = int(index)
                relevance_score = float(relevance_score)
            except (TypeError, ValueError):
                continue

            if 0 <= index < total_docs:
                scores[index] = relevance_score
                valid_count += 1

        if valid_count == 0:
            return None

        return scores

    def score(self, query: str, passages: List[str]) -> Optional[List[float]]:
        """Score passages through LiteLLM's rerank endpoint."""
        if not passages:
            return None

        logger.debug("Reranker request: model=%s passages=%d", self.model_name, len(passages))
        try:
            response = rerank(
                model=self.model_name,
                query=query,
                documents=passages,
                top_n=len(passages),
                return_documents=False,
                api_base=self.api_base,
                api_key=self.api_key,
            )
        except Exception as e:
            logger.error("Reranker failed: %s", e, exc_info=True)
            return None

        scores = self.extract_scores(response, len(passages))
        logger.debug("Reranker response: model=%s scores=%s", self.model_name, scores)
        return scores


def get_reranker(configs: Any) -> Optional[Reranker]:
    """Get a LOCAL reranker backed by LiteLLM's hosted_vllm provider."""

    def get(name, default=None):
        return get_config_value(configs, name, default)

    model_type = get("reranker_model_type")
    model_name = get("reranker_model_name")

    if model_type != "LOCAL" or not model_name:
        return None

    reranker = Reranker(
        model_name=model_name,
        api_base=os.environ.get("LOCAL_BASE_URL"),
        api_key=os.environ.get("LOCAL_API_KEY"),
    )
    logger.info("Loaded reranker '%s'", model_name)
    return reranker
