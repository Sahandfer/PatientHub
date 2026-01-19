---
sidebar_position: 2
---

# Adding New Evaluators

This guide explains how to add new evaluation methods to PatientHub.

## Overview

Evaluators assess simulation quality, therapist performance, or session outcomes. PatientHub supports multiple evaluation types: rating, survey, comparison, inspection, and interview.

## Architecture

```
patienthub/evaluators/
├── __init__.py       # Evaluator registry
├── rating.py         # Dimension-based rating
├── survey.py         # Standardized questionnaires
├── comparison.py     # A/B comparison
├── inspect.py        # Qualitative analysis
├── interview.py      # Interactive evaluation
└── your_evaluator.py # Your new evaluator
```

## Step 1: Create Evaluator File

Create a new file in `patienthub/evaluators/`:

```python
# patienthub/evaluators/myEvaluator.py

from typing import Any, Dict, List, Optional
from langchain_core.messages import AIMessage, HumanMessage

from patienthub.base.agents import BaseAgent


class MyEvaluator(BaseAgent):
    """
    Your custom evaluation method.

    Description of what this evaluator measures.
    """

    def __init__(
        self,
        configs: Any,
        lang: str = "en",
        **kwargs
    ):
        super().__init__(configs=configs, lang=lang, **kwargs)

        # Load evaluation criteria
        self._load_criteria()

        # Initialize results storage
        self.results = []

    def _load_criteria(self):
        """Load evaluation criteria from config or file."""
        self.criteria = getattr(self.configs, 'criteria', [])
        self.scoring_scale = getattr(self.configs, 'scale', (1, 5))

    def evaluate(
        self,
        conversation: List[Dict[str, str]],
        client_profile: Optional[Dict] = None,
        therapist_profile: Optional[Dict] = None,
        **kwargs
    ) -> Dict[str, Any]:
        """
        Evaluate a conversation.

        Args:
            conversation: List of turns [{"role": "therapist/client", "content": "..."}]
            client_profile: Optional client character info
            therapist_profile: Optional therapist info
            **kwargs: Additional evaluation parameters

        Returns:
            Dictionary containing evaluation results
        """
        results = {
            "evaluator": "myEvaluator",
            "scores": {},
            "feedback": {},
            "overall": None,
        }

        # Prepare conversation text
        conv_text = self._format_conversation(conversation)

        # Evaluate each criterion
        for criterion in self.criteria:
            score, feedback = self._evaluate_criterion(
                conv_text, criterion, client_profile, therapist_profile
            )
            results["scores"][criterion] = score
            results["feedback"][criterion] = feedback

        # Calculate overall score
        if results["scores"]:
            results["overall"] = sum(results["scores"].values()) / len(results["scores"])

        self.results.append(results)
        return results

    def _format_conversation(self, conversation: List[Dict]) -> str:
        """Format conversation for evaluation."""
        lines = []
        for turn in conversation:
            role = turn.get("role", "unknown").capitalize()
            content = turn.get("content", "")
            lines.append(f"{role}: {content}")
        return "\n\n".join(lines)

    def _evaluate_criterion(
        self,
        conversation: str,
        criterion: str,
        client_profile: Optional[Dict],
        therapist_profile: Optional[Dict],
    ) -> tuple:
        """
        Evaluate a single criterion using LLM.

        Returns:
            (score, feedback) tuple
        """
        prompt = self._build_evaluation_prompt(
            conversation, criterion, client_profile, therapist_profile
        )

        messages = [
            {"role": "system", "content": self._get_system_prompt()},
            {"role": "user", "content": prompt},
        ]

        response = self.llm.invoke(messages)

        # Parse response for score and feedback
        score, feedback = self._parse_response(response.content, criterion)

        return score, feedback

    def _get_system_prompt(self) -> str:
        """System prompt for the evaluator LLM."""
        return """You are an expert evaluator assessing therapy conversations.
Provide objective, constructive assessments based on the criteria given.
Always explain your reasoning and provide specific examples from the conversation."""

    def _build_evaluation_prompt(
        self,
        conversation: str,
        criterion: str,
        client_profile: Optional[Dict],
        therapist_profile: Optional[Dict],
    ) -> str:
        """Build the evaluation prompt."""
        prompt = f"""Please evaluate the following conversation on the criterion: {criterion}

Conversation:
{conversation}

"""
        if client_profile:
            prompt += f"""
Client Profile:
{client_profile}

"""

        prompt += f"""
Rate on a scale of {self.scoring_scale[0]} to {self.scoring_scale[1]}.
Provide your rating and a brief explanation.

Format your response as:
SCORE: [number]
FEEDBACK: [your explanation]
"""
        return prompt

    def _parse_response(self, response: str, criterion: str) -> tuple:
        """Parse LLM response into score and feedback."""
        import re

        # Extract score
        score_match = re.search(r'SCORE:\s*(\d+(?:\.\d+)?)', response)
        score = float(score_match.group(1)) if score_match else None

        # Extract feedback
        feedback_match = re.search(r'FEEDBACK:\s*(.+)', response, re.DOTALL)
        feedback = feedback_match.group(1).strip() if feedback_match else response

        # Clamp score to valid range
        if score is not None:
            score = max(self.scoring_scale[0], min(self.scoring_scale[1], score))

        return score, feedback

    def get_summary(self) -> Dict[str, Any]:
        """Get summary statistics across all evaluations."""
        if not self.results:
            return {"error": "No evaluations performed"}

        summary = {
            "num_evaluations": len(self.results),
            "average_scores": {},
            "overall_average": None,
        }

        # Aggregate scores by criterion
        all_criteria = set()
        for r in self.results:
            all_criteria.update(r["scores"].keys())

        for criterion in all_criteria:
            scores = [r["scores"].get(criterion) for r in self.results if r["scores"].get(criterion)]
            if scores:
                summary["average_scores"][criterion] = sum(scores) / len(scores)

        # Overall average
        overalls = [r["overall"] for r in self.results if r["overall"] is not None]
        if overalls:
            summary["overall_average"] = sum(overalls) / len(overalls)

        return summary

    def reset(self):
        """Reset evaluator for new evaluation batch."""
        self.results = []
```

## Step 2: Register the Evaluator

Add to `patienthub/evaluators/__init__.py`:

```python
from patienthub.evaluators.myEvaluator import MyEvaluator

EVALUATOR_REGISTRY = {
    # ... existing evaluators ...
    'myEvaluator': MyEvaluator,
}

def get_evaluator(configs, lang: str = "en", **kwargs):
    eval_type = configs.eval_type
    if eval_type not in EVALUATOR_REGISTRY:
        raise ValueError(f"Unknown evaluator type: {eval_type}")
    return EVALUATOR_REGISTRY[eval_type](configs=configs, lang=lang, **kwargs)
```

## Step 3: Define Evaluation Dimensions

Create dimension definitions in `patienthub/evaluators/dimensions/`:

```python
# patienthub/evaluators/dimensions/myDimensions.py

MY_DIMENSIONS = {
    "empathy": {
        "name": "Empathy",
        "description": "The degree to which the therapist demonstrates understanding of the client's emotional experience",
        "indicators": [
            "Reflects client's feelings accurately",
            "Validates emotional experiences",
            "Shows genuine concern",
        ],
        "scale": (1, 5),
        "anchors": {
            1: "No empathy demonstrated",
            3: "Moderate empathy with some reflection",
            5: "Deep empathic understanding throughout",
        }
    },
    "authenticity": {
        "name": "Client Authenticity",
        "description": "How realistic and consistent the simulated client's responses are",
        "indicators": [
            "Responses match character profile",
            "Emotional reactions are appropriate",
            "Maintains consistent personality",
        ],
        "scale": (1, 5),
        "anchors": {
            1: "Responses feel artificial or inconsistent",
            3: "Generally authentic with minor inconsistencies",
            5: "Highly authentic and completely consistent",
        }
    },
}
```

## Step 4: Create Configuration

Add configuration options:

```yaml
# configs/evaluator/myEvaluator.yaml
eval_type: myEvaluator
model_type: LAB
model_name: gpt-4o
temperature: 0.0 # Deterministic for evaluation
max_tokens: 1024
criteria:
  - empathy
  - authenticity
scale: [1, 5]
target: therapist # or "client" or "both"
```

## Step 5: Add Tests

```python
# patienthub/tests/test_myEvaluator.py

import pytest
from omegaconf import OmegaConf
from patienthub.evaluators import get_evaluator


@pytest.fixture
def evaluator_config():
    return OmegaConf.create({
        'eval_type': 'myEvaluator',
        'model_type': 'LAB',
        'model_name': 'gpt-4o-mini',
        'temperature': 0.0,
        'max_tokens': 512,
        'criteria': ['empathy', 'authenticity'],
        'scale': [1, 5],
    })


@pytest.fixture
def sample_conversation():
    return [
        {"role": "therapist", "content": "Hello, how are you feeling today?"},
        {"role": "client", "content": "Not great, I've been really anxious lately."},
        {"role": "therapist", "content": "I hear that you've been struggling with anxiety. That sounds difficult. Can you tell me more about what triggers it?"},
        {"role": "client", "content": "Work mostly. The deadlines are overwhelming."},
    ]


def test_evaluator_initialization(evaluator_config):
    evaluator = get_evaluator(configs=evaluator_config)
    assert evaluator is not None


def test_single_evaluation(evaluator_config, sample_conversation):
    evaluator = get_evaluator(configs=evaluator_config)
    results = evaluator.evaluate(sample_conversation)

    assert "scores" in results
    assert "feedback" in results
    assert "overall" in results


def test_multiple_evaluations(evaluator_config, sample_conversation):
    evaluator = get_evaluator(configs=evaluator_config)

    evaluator.evaluate(sample_conversation)
    evaluator.evaluate(sample_conversation)

    summary = evaluator.get_summary()
    assert summary["num_evaluations"] == 2
```

## Evaluator Types

### Rating Evaluator

Scores conversations on predefined dimensions (1-5 scale).

### Survey Evaluator

Administers standardized questionnaires (PHQ-9, GAD-7, etc.).

### Comparison Evaluator

A/B comparison between two agents or methods.

### Inspection Evaluator

Qualitative analysis with structured feedback.

### Interview Evaluator

Interactive evaluation through follow-up questions.

## Advanced Features

### Turn-Level vs Session-Level

```python
class TurnLevelEvaluator(BaseEvaluator):
    def evaluate(self, conversation, **kwargs):
        turn_results = []
        for i in range(0, len(conversation), 2):  # Each exchange
            turn = conversation[i:i+2]
            result = self._evaluate_turn(turn)
            turn_results.append(result)

        return {
            "turn_results": turn_results,
            "session_aggregate": self._aggregate(turn_results),
        }
```

### Multi-Rater Support

```python
class MultiRaterEvaluator(BaseEvaluator):
    def __init__(self, configs, **kwargs):
        super().__init__(configs, **kwargs)
        self.num_raters = getattr(configs, 'num_raters', 3)

    def evaluate(self, conversation, **kwargs):
        ratings = []
        for _ in range(self.num_raters):
            rating = self._single_evaluation(conversation)
            ratings.append(rating)

        return {
            "individual_ratings": ratings,
            "consensus": self._compute_consensus(ratings),
            "agreement": self._compute_agreement(ratings),
        }
```

## Checklist

Before submitting your new evaluator:

- [ ] Evaluator class in `patienthub/evaluators/`
- [ ] Registered in `__init__.py`
- [ ] Dimension definitions (if applicable)
- [ ] Configuration file
- [ ] Unit tests passing
- [ ] Documentation updated
- [ ] Example usage: `python -m examples.evaluate evaluator=yourEvaluator`
