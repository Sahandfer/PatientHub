---
sidebar_position: 1
---

# SAPS

> Automatic Interactive Evaluation for Large Language Models with State Aware Patient Simulator

**Venue**: ArXiv  
**Paper**: [arXiv](https://arxiv.org/pdf/2403.08495)

## Overview

SAPS focuses on clinical consultation, where the agent role-plays based on real hospital cases to assess whether the doctor can accurately diagnose the condition.  
SAPS introduces State Tracking and Memory Bank mechanisms, forcing the patient simulator to decide "how much information to give" or "whether to refuse to answer" based strictly on the doctor's performance.

## Key Features

It uses specific Prompts to judge in three stages:

- **Broad Category (Stage I)**: Classify the doctor's questions into Inquiry, Advice, Demand, Other Topic or End
- **Specificity (Stage II)**: Determine the question is specific or broad
- **Relevance (Stage III)**: Extract relevant information from the complete medical record

Based on the final state obtained by the State Tracker, SAPS selects the corresponding **state_instruction prompt** to generate the patient response.

## How It Works

1. **Load a Real Case Profile**: Selects a patient case (medical record) as the simulation “ground truth”.
2. **Track the Doctor’s Intent (State Tracking)**: For each doctor turn, classifies the utterance type and checks whether it is specific enough to answer.
3. **Retrieve Only Relevant Evidence (Memory Bank)**: When needed, extracts the most relevant fragment(s) from the full medical record; otherwise withholds details to avoid over-disclosure.
4. **Route to a State-Specific Behavior Prompt**: Chooses a response policy/instruction prompt based on the final state (what to disclose / how to respond).
5. **Generate Response with Conversation Context**: Produces the patient reply conditioned on the selected instruction and multi-turn history, then updates the dialogue memory for the next turn.

## Usage

### CLI

```bash
uv run python -m examples.simulate client=saps therapist=user
```

### Python

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client

config = OmegaConf.create(
    {
        "agent_type": "saps",
        "model_type": "OPENAI",
        "model_name": "gpt-4o",
        "temperature": 0.7,
        "max_tokens": 1024,
        "max_retries": 3,
        "data_path": "data/characters/SAPS.json",
        "data_idx": 0,
    }
)

client = get_client(configs=config, lang="en")

response = client.generate_response(
    "Could you describe your main symptoms and when they started?"
)
print(response)
```

## Configuration

| Option        | Description            | Default                         |
| ------------- | ---------------------- | ------------------------------- |
| `prompt_path` | Path to prompt file    | `data/prompts/client/saps.yaml` |
| `data_path`   | Path to character file | `data/characters/SAPS.json`     |
| `data_idx`    | Character index        | `0`                             |

## Character Data Format

```json
{
  "id": 539,
  "patient_info": "Female, 62 years old, recurrence of symmetrical facial features three years post soft palate adhesion surgery. Normal jaw opening and mouth opening type, postoperative changes to the soft palate, no obvious masses, local scarring, local induration, ill-defined margins, no tenderness, no ulceration or bleeding, no erythema, intact permanent dentition, and no other apparent abnormalities. Several nodules less than 1 cm in diameter palpable in the submandibular area, no enlarged lymph nodes in the neck. Blood work dated 2015-09-16 05:29: White blood cell count 7.4 x 10^9/L (N); red blood cell count 3.44 x10^12/L (L); hemoglobin 103 g/L (L); hematocrit 0.304 (L); platelet count 236 x10^9/L (N); segmented neutrophils 63.5% (N). Serum chemistry dated 2015-09-16 07:17: serum potassium 3.11 mmol/L (L); serum sodium 144 mmol/L (N); serum chloride 107 mmol/L (H). Examination: Histological cryosection Result: “IIB” lymph node with tumor tissue present (+).Examination: Histological cryosection Specimens examined: LN \"Submandibular 1\" (one), \"Submandibular 2\" (one), both negative (-)"
}
```

## Resources

Two Doctor LLMs Test Sets

`data/resources/SAPS/HospitalCases.json`(In Chinese): Includes 50 real hospital cases.

`data/resources/SAPS/MedicalExam.json`(In English): Includes 150 cases selected from MedQA, MedMCQA, MMLU, SelfExam, and QMAX.
