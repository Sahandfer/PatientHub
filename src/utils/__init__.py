import os
import json
from dotenv import load_dotenv
from camel.models import ModelFactory
from camel.types import ModelPlatformType

load_dotenv(".env")


def get_model_client(model_name):
    return ModelFactory.create(
        model_platform=ModelPlatformType.OPENAI,
        model_type=model_name,
        url=os.environ.get("BASE_URL"),
        api_key=os.environ.get("API_KEY"),
    )


def parse_json_response(res):
    try:
        res = res.replace("```json", "").replace("```", "")
        res = json.loads(res)
        return res
    except json.JSONDecodeError:
        return res
