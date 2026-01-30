---
sidebar_position: 8
---

# ClientCast

> Towards a Client-Centered Assessment of LLM Therapists by Client Simulation

**Venue**: ArXiv  
**Paper**: [ArXiv](https://arxiv.org/pdf/2406.12266)

## Overview

ClientCast creates client simulations for assessing LLM-based therapists. It introduces well-designed and detailed psychological profiles including Big Five personality traits, symptom assessments (PHQ-9, GAD-7, OQ-45), and conversation history from real therapy sessions to create realistic client behavior.

## Key Features

- **Big Five Personality**: Detailed personality modeling with explanations
- **Symptom Assessment**: Integration with PHQ-9, GAD-7, and OQ-45 scales
- **Real Conversation Grounding**: Uses human therapy conversation excerpts
- **Client-Centered Focus**: Designed for therapist assessment rather than training

## Psychological Scales

ClientCast integrates multiple validated assessment instruments:

| Scale | Description                        | Focus               |
| ----- | ---------------------------------- | ------------------- |
| PHQ-9 | Patient Health Questionnaire       | Depression symptoms |
| GAD-7 | Generalized Anxiety Disorder scale | Anxiety symptoms    |
| OQ-45 | Outcome Questionnaire              | Overall functioning |

## Usage

### CLI

```bash
uv run python -m examples.simulate client=clientCast therapist=CBT
```

### Python

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client

config = OmegaConf.create({
    'agent_type': 'clientCast',
    'model_type': 'LAB',
    'model_name': 'gpt-4o',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
    'data_path': 'data/characters/ClientCast.json',
    'conv_path': 'data/resources/ClientCast/human_data.json',
    'symptoms_path': 'data/resources/ClientCast/symptoms.json',
    'data_idx': 0,
    'conv_id': 0,
})

client = get_client(configs=config, lang='en')
client.set_therapist({'name': 'Therapist'})

response = client.generate_response("What brings you in today?")
print(response.content)
```

## Configuration

| Option          | Description                 | Default                                     |
| --------------- | --------------------------- | ------------------------------------------- |
| `data_path`     | Path to character file      | `data/characters/ClientCast.json`           |
| `conv_path`     | Path to conversation data   | `data/resources/ClientCast/human_data.json` |
| `symptoms_path` | Path to symptom assessment definitions | `data/resources/ClientCast/symptoms.json`   |
| `data_idx`      | Character index             | `0`                                         |
| `conv_id`       | Conversation excerpt ID     | `0`                                         |

## Character Data Format

```json
{
  "basic_profile": {
    "name": "Not Specified",
    "gender": "Female",
    "age": -1,
    "occupation": "Not Specified",
    "topic": "alcohol consumption – discussing frequency and effects...",
    "situation": "The client drinks alcohol regularly to unwind...",
    "emotion": "The client feels guilty about their drinking habits...",
    "reasons": "Concerned about alcohol consumption and its effect on depression",
    "problem": "alcohol consumption – struggles with drinking more than intended",
    "feeling_expression": "Medium – shares feelings but does not deeply explore them",
    "emotional_fluctuation": "Medium – talks about relief and worsening feelings",
    "resistance": "Low – open to discussing drinking habits"
  },
  "big_five": {
    "Openness": {
      "score_percent": 55,
      "explanation": "Enjoys watching movies and reading..."
    },
    "Conscientiousness": {
      "score_percent": 60,
      "explanation": "Aware of drinking habits, willing to set goals..."
    },
    "Extraversion": {
      "score_percent": 45,
      "explanation": "Enjoys social activities but doesn't mention frequent interactions"
    },
    "Agreeableness": {
      "score_percent": 65,
      "explanation": "Willing to reduce alcohol consumption, cooperative"
    },
    "Neuroticism": {
      "score_percent": 75,
      "explanation": "Experiences depression and uses alcohol to cope"
    }
  },
  "symptoms": {
    "PHQ9": {
      "1": {
        "identified": false,
        "severity_level": null,
        "explanation": "Still finds interest in activities..."
      }
    },
    "GAD7": {
      "1": {
        "identified": false,
        "explanation": "No mentioned anxiety symptoms..."
      }
    },
    "OQ45": {
      "1": {
        "identified": false,
        "explanation": "Unable to assess social interactions..."
      }
    }
  }
}
```

## How It Works

1. **Profile Construction**: Builds case synopsis from basic profile
2. **Symptom Integration**: Incorporates identified symptoms with severity levels
3. **Personality Mapping**: Uses Big Five traits to guide response style
4. **Conversation Grounding**: References real therapy conversation excerpts
5. **Response Generation**: Produces responses consistent with profile and conversation context

## Resources

`data/resources/ClientCast/human_data.json`: Human therapy conversation excerpts for grounding client simulations
`data/resources/ClientCast/symptoms.json`: Symptom item texts for PHQ-9, GAD-7, and OQ-45 used to identify symptoms in the ClientCast profile

<!-- ## Research Applications

ClientCast is designed for:

- **Therapist Assessment**: Evaluating LLM-based therapist quality
- **A/B Testing**: Comparing different therapist approaches
- **Safety Evaluation**: Testing therapist responses to various client presentations
- **Benchmark Creation**: Building standardized client cases for evaluation -->
