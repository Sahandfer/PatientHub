from abc import abstractmethod
from typing import Any, Dict, List


class BaseGenerator:
    r"""Base class for all generator agents."""

    configs: Dict[str, Any]
    input_dir: str
    output_dir: str
    lang: str
