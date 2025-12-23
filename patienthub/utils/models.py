import os
from dotenv import load_dotenv
from dataclasses import dataclass
from typing import Any, List, Optional
from langchain.chat_models import init_chat_model
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline

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


def get_chat_model(configs):
    def get(name, default=None):
        return get_config_value(configs, name, default)

    model_type = get("model_type")
    model_name = get("model_name")

    if model_type == "local":
        hf_pipe = HuggingFacePipeline.from_model_id(
            model_id=model_name,
            task="text-generation",
            device=get("device"),
            pipeline_kwargs={
                "max_new_tokens": get("max_new_tokens"),
                "temperature": get("temperature"),
                "repetition_penalty": get("repetition_penalty"),
                "return_full_text": False,
            },
        )
        return init_chat_model(
            model_provider="huggingface", model=model_name, llm=hf_pipe
        )
    if model_type == "huggingface":
        return ChatHuggingFace.from_model_id(
            model_id=model_name,
            task="text-generation",
            device=get("device"),
            model_kwargs={
                "max_new_tokens": get("max_new_tokens"),
                "temperature": get("temperature"),
                "repetition_penalty": get("repetition_penalty"),
                "return_full_text": False,
            },
        )
    if model_type == "LAB":
        return init_chat_model(
            model=model_name,
            model_provider="openai",
            base_url=os.environ.get(f"{model_type}_BASE_URL"),
            api_key=os.environ.get(f"{model_type}_API_KEY"),
            temperature=get("temperature"),
            max_tokens=get("max_tokens"),
            max_retries=get("max_retries"),
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
