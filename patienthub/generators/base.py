from abc import ABC, abstractmethod
from typing import Any, Dict


class BaseGenerator(ABC):
    r"""Base class for all generator agents."""

    configs: Dict[str, Any]
    input_dir: str
    output_dir: str
    lang: str
