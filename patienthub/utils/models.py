import os
import logging
import instructor
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Any, List, Optional, Dict
from litellm import completion, supports_response_schema, completion_cost

logging.getLogger("LiteLLM").setLevel(logging.WARNING)

load_dotenv(".env")


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
            print("> Model does not support response format")

    def track_usage(self, response):
        """Track token usage and cost from API response using LiteLLM."""
        if hasattr(response, "usage") and response.usage:
            self.prompt_tokens += response.usage.prompt_tokens or 0
            self.completion_tokens += response.usage.completion_tokens or 0
            self.total_tokens += response.usage.total_tokens or 0
        try:
            self.total_cost += completion_cost(completion_response=response)
        except Exception:
            pass  # Cost calculation not available for this model

    def generate(self, messages, response_format=None):
        if not self.res_format_support or response_format is None:
            res = completion(model=self.model_name, messages=messages, **self.kwargs)
            self.track_usage(res)
            return res.choices[0].message
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
    def __init__(self, tokenizer: Any, model: Any, device: Any):
        self.tokenizer = tokenizer
        self.model = model
        self.device = device

    def score(
        self, query: str, passages: List[str], max_length: int = 512
    ) -> Optional[List[float]]:
        """Score (query, passage) pairs. Higher = more relevant."""
        if not passages:
            return None

        pairs = [(query, passage) for passage in passages]

        try:
            return self.compute_scores(pairs, max_length)
        except Exception:
            return None

    def compute_scores(self, pairs: List[tuple], max_length: int) -> List[float]:
        """Compute relevance scores for query-passage pairs."""
        import torch

        with torch.no_grad():
            inputs = self.tokenizer(
                pairs,
                padding=True,
                truncation=True,
                return_tensors="pt",
                max_length=max_length,
            )
            inputs = {k: v.to(self.device) for k, v in inputs.items()}
            outputs = self.model(**inputs, return_dict=True)
            logits = outputs.logits.view(-1).float()
            return torch.sigmoid(logits).tolist()


def get_device(device_index: int):
    import torch

    try:
        device_index = int(device_index)
    except Exception:
        device_index = 0

    if torch.cuda.is_available() and device_index >= 0:
        return torch.device(f"cuda:{device_index}")
    return torch.device("cpu")


def load_reranker_model(model_name: str, device: Any):
    """Load tokenizer and model for reranking."""
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.to(device)
    model.eval()
    return tokenizer, model


def get_reranker(configs: Any) -> Optional[Reranker]:
    """Get a Reranker instance from config, or None if unavailable."""

    def get(name, default=None):
        return get_config_value(configs, name, default)

    model_type = get("model_type")
    model_name = get("model_name")

    if model_type not in ("huggingface", "local") or not model_name:
        return None

    try:
        device = get_device(get("device", 0))
        tokenizer, model = load_reranker_model(model_name, device)
        return Reranker(tokenizer=tokenizer, model=model, device=device)
    except Exception:
        return None
