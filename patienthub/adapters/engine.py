# coding=utf-8
# Licensed under the MIT License;

"""LLM-backed runtime for cross-client character adaptation."""

import json
import os
from dataclasses import dataclass
from typing import Any

from omegaconf import DictConfig
from pydantic import BaseModel

from patienthub.clients import get_client_config
from patienthub.configs import APIModelConfig
from patienthub.utils import get_chat_model, load_json, load_prompts

from . import get_character_container, get_character_model


@dataclass
class AdapterConfig(APIModelConfig):
    """Configuration for the character adapter."""

    source_client: str = "patientPsi"
    target_client: str = "annaAgent"
    prompt_path: str = "data/prompts/adapter/character.yaml"
    input_path: str = ""
    output_path: str = ""
    source_idx: int = 0


class CharacterAdapter:
    """Convert one client character format into another via a typed LLM call."""

    def __init__(self, configs: DictConfig):
        self.configs = configs
        self.source_model = get_character_model(configs.source_client)
        self.target_model = get_character_model(configs.target_client)
        self.chat_model = get_chat_model(configs)
        self.prompts = load_prompts(path=configs.prompt_path, lang=configs.lang)

    def resolve_input_path(self) -> str:
        if self.configs.input_path:
            return self.configs.input_path
        return get_client_config(self.configs.source_client).data_path

    def resolve_output_path(self) -> str:
        if self.configs.output_path:
            return self.configs.output_path

        default_target_path = get_client_config(self.configs.target_client).data_path
        root, ext = os.path.splitext(default_target_path)
        return f"{root}_from_{self.configs.source_client}{ext or '.json'}"

    def load_source_payload(self) -> dict[str, Any]:
        raw = load_json(self.resolve_input_path())
        if isinstance(raw, list):
            try:
                payload = raw[self.configs.source_idx]
            except IndexError as exc:
                raise ValueError(
                    f"source_idx {self.configs.source_idx} is out of range for {self.resolve_input_path()}"
                ) from exc
        elif isinstance(raw, dict):
            payload = raw
        else:
            raise ValueError("Source character file must contain a JSON object or list")

        validated = self.source_model.model_validate(payload)
        return validated.model_dump(by_alias=True, exclude_none=True)

    def load_target_example(self) -> dict[str, Any]:
        raw = load_json(get_client_config(self.configs.target_client).data_path)
        if isinstance(raw, list):
            if not raw:
                raise ValueError(
                    f"No target example found for {self.configs.target_client}"
                )
            payload = raw[0]
        elif isinstance(raw, dict):
            payload = raw
        else:
            raise ValueError("Target character file must contain a JSON object or list")

        validated = self.target_model.model_validate(payload)
        return validated.model_dump(by_alias=True, exclude_none=True)

    def build_prompt(self, source_payload: dict[str, Any]) -> str:
        return self.prompts["adapt"].render(
            source_client=self.configs.source_client,
            target_client=self.configs.target_client,
            source_character=json.dumps(source_payload, ensure_ascii=False, indent=2),
            target_example=json.dumps(
                self.load_target_example(),
                ensure_ascii=False,
                indent=2,
            ),
        )

    def coerce_target_model(self, result: BaseModel | dict[str, Any]) -> BaseModel:
        if isinstance(result, BaseModel):
            payload = result.model_dump(by_alias=True, exclude_none=True)
        elif isinstance(result, dict):
            payload = result
        else:
            payload = result
        return self.target_model.model_validate(payload)

    def adapt(self) -> dict[str, Any]:
        source_payload = self.load_source_payload()
        prompt = self.build_prompt(source_payload)
        result = self.chat_model.generate(
            messages=[{"role": "system", "content": prompt}],
            response_format=self.target_model,
        )

        validated = self.coerce_target_model(result)
        return validated.model_dump(by_alias=True, exclude_none=True)

    def save(self, payload: dict[str, Any]) -> str:
        output_path = self.resolve_output_path()
        parent_dir = os.path.dirname(output_path)
        if parent_dir and not os.path.exists(parent_dir):
            os.makedirs(parent_dir)

        if os.path.exists(output_path):
            raise ValueError(f"Output file already exists: {output_path}")

        container = get_character_container(self.configs.target_client)
        if container == "dict":
            serialized: Any = payload
        else:
            serialized = [payload]

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(serialized, f, indent=4, ensure_ascii=False)

        return output_path

    def adapt_and_save(self) -> dict[str, Any]:
        payload = self.adapt()
        self.save(payload)
        return payload
