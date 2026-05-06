"""
Adapt a character profile from one client format to another.
It requires:
    - input_path: path to the source character JSON file
    - target_client: name of the target client (e.g., roleplayDoh)
It infers the target structure from the registered schema and optionally accepts
an example JSON for few-shot guidance.

Usage:
    # Adapt using schema only
    patienthub adapt input_path=data/characters/PatientPsi.json target_client=roleplayDoh

    # Pick a specific character by index
    patienthub adapt input_path=data/characters/PatientPsi.json target_client=roleplayDoh source_index=2

    # Supplement with a few-shot example
    patienthub adapt input_path=data/characters/PatientPsi.json target_client=roleplayDoh example=data/characters/roleplayDoh.json

    # Specify output path
    patienthub adapt input_path=data/characters/PatientPsi.json target_client=roleplayDoh output=data/characters/adapted/result.json

    # Use Chinese output
    patienthub adapt input_path=data/characters/PatientPsi.json target_client=roleplayDoh lang=zh
"""

import json

import hydra
from jinja2 import Template
from omegaconf import DictConfig
from dataclasses import dataclass
from hydra.core.config_store import ConfigStore

from patienthub.configs import APIModelConfig
from patienthub.schemas import get_profile_schema
from patienthub.utils import load_json, save_json, get_chat_model, parse_json_response
from patienthub.utils.logger import get_logger, init_logging, LogLevel

logger = get_logger(__name__)

ADAPT_PROMPT = Template(
    """\
You are adapting a PatientHub character profile from one client format to another.

Target client: {{ target_client }}

Your task is to produce a target-client character that is faithful to the source profile while making reasonable target-specific expansions where the source and target formats do not map one-to-one.

Rules:
1. Preserve source facts whenever they can be transferred directly.
2. Infer missing target-only details conservatively and plausibly.
3. Prefer clinically and behaviorally coherent expansions over decorative detail.
4. Do not contradict the source character.
5. Use the target schema to understand the required fields and their types.
6. Do not mention this conversion process.
7. Return only the target structure as valid JSON.
{% if lang != "en" %}8. Generate the data in {{ lang }}.{% endif %}

Source character JSON:
{{ source_character }}

Target schema (JSON Schema):
{{ target_schema }}
{% if target_example %}
Target example JSON (for reference only — do not copy facts unless supported by the source):
{{ target_example }}
{% endif %}\
"""
)


@dataclass
class AdaptConfig(APIModelConfig):
    """Configuration for adapting character profiles between client formats."""

    input_path: str = ""
    target_client: str = ""
    source_index: int = 0
    example_path: str = ""
    output_path: str = "data/characters/adapted.json"
    lang: str = "en"


cs = ConfigStore.instance()
cs.store(name="adapt", node=AdaptConfig)


@hydra.main(version_base=None, config_name="adapt")
def adapt(configs: DictConfig):
    init_logging("adapt", level=LogLevel.INFO)
    logger.info(
        "Starting adaptation: %s → %s (index=%d)",
        configs.input_path,
        configs.target_client,
        configs.source_index,
    )
    try:
        if not configs.input_path or not configs.target_client:
            logger.error("input_path and target_client are required.")
            return
        source_data = load_json(configs.input_path)
        source_character = json.dumps(
            source_data[configs.source_index], indent=2, ensure_ascii=False
        )

        target_schema = get_profile_schema(configs.target_client)
        target_schema_json = json.dumps(target_schema.model_json_schema(), indent=2)

        target_example = None
        if configs.example_path:
            example_data = load_json(configs.example_path)
            target_example = json.dumps(example_data[0], indent=2, ensure_ascii=False)

        prompt = ADAPT_PROMPT.render(
            target_client=configs.target_client,
            source_character=source_character,
            target_schema=target_schema_json,
            target_example=target_example,
            lang=configs.lang,
        )

        chat_model = get_chat_model(configs)
        result = chat_model.generate([{"role": "system", "content": prompt}])

        adapted_character = parse_json_response(result.content)

        save_json(adapted_character, configs.output_path, overwrite=False)
        logger.info("Adapted character saved to '%s'", configs.output_path)

    except IndexError:
        logger.error(
            "source_index=%d is out of range (file has %d entries).",
            configs.source_index,
            len(source_data),
        )
    except FileNotFoundError as e:
        logger.error("File not found: %s", e)
    except KeyboardInterrupt:
        logger.warning("Adaptation interrupted by user.")


if __name__ == "__main__":
    adapt()
