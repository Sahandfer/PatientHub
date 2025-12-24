from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class Aspect:
    """A single aspect within a dimension."""

    name: str
    description: str
    guidelines: Optional[str] = None


@dataclass
class Dimension:
    """A dimension to evaluate."""

    name: str
    description: str
    aspects: List[Aspect] = field(default_factory=list)
    target: str = "client"  # "client" or "therapist"
