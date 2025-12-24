from .base import Dimension, Aspect

CONSISTENCY = Dimension(
    name="consistency",
    description="Evaluates whether the client's responses are consistent",
    target="client",
    aspects=[
        Aspect(
            name="profile_factual",
            description="Factual consistency with the character profile",
            guidelines="Check if stated facts (age, job, family) match the profile",
        ),
        Aspect(
            name="conv_factual",
            description="Factual consistency within the conversation history",
            guidelines="Check for self-contradictions across turns",
        ),
        Aspect(
            name="behavioral",
            description="Behavioral consistency between profile and responses",
            guidelines="Check if actions/reactions match personality traits",
        ),
        Aspect(
            name="emotional",
            description="Emotional consistency between profile and responses",
            guidelines="Check if emotional expressions match the profile's affect",
        ),
    ],
)
