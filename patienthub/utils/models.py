import os
import logging
import instructor
from pydantic import BaseModel
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Any, List, Optional, Dict
from litellm import completion, supports_response_schema

logging.getLogger("LiteLLM").setLevel(logging.WARNING)


# from langchain.chat_models import init_chat_model
# from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline

load_dotenv(".env")


def get_config_value(configs, name, default=None):
    # Support both DictConfig (attribute access) and dict (key access)
    if isinstance(configs, dict):
        return configs.get(name, default)
    return getattr(configs, name, default)


def get_device(device_index: int):
    import torch

    try:
        device_index = int(device_index)
    except Exception:
        device_index = 0

    if torch.cuda.is_available() and device_index >= 0:
        return torch.device(f"cuda:{device_index}")
    return torch.device("cpu")


class ChatModel:
    def __init__(self, model_name, **kwargs):
        self.model_name = model_name
        self.kwargs = kwargs
        self.res_format_support = supports_response_schema(model=model_name)
        if not self.res_format_support:
            print("> Model does not support response format")

    def generate(self, messages, response_format=None):
        if not self.res_format_support or response_format is None:
            res = completion(model=self.model_name, messages=messages, **self.kwargs)
            return res.choices[0].message
        else:
            client = instructor.from_litellm(completion)
            res = client.chat.completions.create(
                model=self.model_name,
                messages=messages,
                response_model=response_format,
                **self.kwargs,
            )
            return res


def get_chat_model(configs):
    def get(name, default=None):
        return get_config_value(configs, name, default)

    model_type = get("model_type")
    model_name = get("model_name")

    return ChatModel(
        model_name=model_name,
        base_url=os.environ.get(f"{model_type}_BASE_URL", None),
        api_key=os.environ.get(f"{model_type}_API_KEY", None),
    )


def load_reranker_model(model_name: str, device: Any):
    """Load tokenizer and model for reranking."""
    from transformers import AutoModelForSequenceClassification, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSequenceClassification.from_pretrained(model_name)
    model.to(device)
    model.eval()
    return tokenizer, model


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
