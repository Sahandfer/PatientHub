import os
import json
import yaml
from jinja2 import Template
from dotenv import load_dotenv
from langchain.chat_models import init_chat_model
from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline

load_dotenv(".env")


def load_json(path: str):
    return json.load(open(path, "r", encoding="utf-8"))


def load_yaml(path: str):
    try:
        with open(path, "r") as file:
            return yaml.safe_load(file)
    except Exception as e:
        print("Error loading YAML file:", e)
        return {}


def load_prompts(role: str, agent_type: str, lang: str = "en"):
    path = f"data/prompts/{role}/{agent_type}.yaml"
    prompts = {}
    data = load_yaml(path)[lang]
    for k, v in data.items():
        if isinstance(v, str):
            prompts[k] = Template(v)
    return prompts


def parse_json_response(res):
    try:
        res = res.replace("```json", "").replace("```", "")
        res = json.loads(res)
        return res
    except Exception as e:
        print(f"Error while parsing JSON response: {e}")
        return res


def save_json(data, file_path: str):
    # Check if the directory exists, if not create it
    if not os.path.exists(os.path.dirname(file_path)):
        os.makedirs(os.path.dirname(file_path))

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def append_json(item, file_path: str):
    existing = []
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                existing = json.load(f)
        except Exception:
            existing = []

    if isinstance(existing, list):
        existing.append(item)
    elif existing:
        existing = [existing, item]
    else:
        existing = [item]

    save_json(existing, file_path)


def get_model_client(configs):
    # Support both DictConfig (attribute access) and dict (key access)
    def get(name, default=None):
        if isinstance(configs, dict):
            return configs.get(name, default)
        return getattr(configs, name, default)

    api_type = get("api_type")
    model_name = get("model_name")

    if api_type == "local":
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
    if api_type == "huggingface":
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
    if api_type == "LAB":
        return init_chat_model(
            model=model_name,
            model_provider="openai",
            base_url=os.environ.get(f"{api_type}_BASE_URL"),
            api_key=os.environ.get(f"{api_type}_API_KEY"),
            temperature=get("temperature"),
            max_tokens=get("max_tokens"),
            max_retries=get("max_retries"),
        )


def get_reranker_model(configs):
    # Support both DictConfig (attribute access) and dict (key access)
    def cfg(name, default=None):
        if isinstance(configs, dict):
            return configs.get(name, default)
        return getattr(configs, name, default)

    api_type = cfg("api_type")
    model_name = cfg("model_name")
    if api_type not in ("huggingface", "local") or not model_name:
        return None, None, None

    try:
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
    except Exception:
        return None, None, None

    device_index = cfg("device", 0)
    try:
        device_index = int(device_index)
    except (TypeError, ValueError):
        device_index = 0

    if torch.cuda.is_available() and device_index >= 0:
        device = torch.device(f"cuda:{device_index}")
    else:
        device = torch.device("cpu")

    try:
        tokenizer = AutoTokenizer.from_pretrained(model_name)
        model = AutoModelForSequenceClassification.from_pretrained(model_name)
        model.to(device)
        model.eval()
        return tokenizer, model, device
    except Exception:
        return None, None, None


def rerank_query_passages(
    tokenizer, model, device, query: str, passages: list[str], max_length: int = 512
):
    """Score (query, passage) pairs with a cross-encoder model.

    Returns a list of scores (higher means more relevant), or None on failure.
    """
    if tokenizer is None or model is None or not passages:
        return None

    try:
        import torch
    except Exception:
        return None

    pairs = list(zip([query] * len(passages), passages))
    try:
        with torch.no_grad():
            inputs = tokenizer(
                pairs,
                padding=True,
                truncation=True,
                return_tensors="pt",
                max_length=max_length,
            )
            inputs = {k: v.to(device) for k, v in inputs.items()}
            outputs = model(**inputs, return_dict=True)
            logits = outputs.logits.view(-1).float()
            scores = torch.sigmoid(logits).tolist()
        return scores
    except Exception:
        return None
