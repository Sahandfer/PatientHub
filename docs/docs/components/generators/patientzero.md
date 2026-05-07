# PatientZero Generator

> Scaling Synthetic Patient Agents to Real-World Distributions without Real Patient Data

**Paper**: [Arxiv](https://arxiv.org/pdf/2509.11078)

Generates clinically grounded static patient records from disease knowledge and attribute priors. The current implementation follows the Patient-Zero hierarchical synthesis idea: it starts from an abstract disease concept, standardizes disease knowledge, samples patient attributes, generates symptoms, creates examination results, validates the generated content, and appends the final record to a character JSON file.

## Overview

| Property   | Value                         |
| ---------- | ----------------------------- |
| **Key**    | `patientZero`                 |
| **Type**   | LLM-based + sampled priors    |
| **Output** | PatientZero character records |

## Key Features

- **Disease-grounded generation(Stage I)**: Uses source-grounded `raw_outlines.json` and standardized `disease_outlines.json` as the clinical scaffold.
- **Attribute sampling(Stage II)**: Samples demographics, socioeconomic factors, lifestyle factors, communication style, and severity from global and disease-specific priors.
- **Stage-wise synthesis(Stage III & IV)**: Generates patient background, symptom trajectory, and examination results in separate pipeline stages.
- **Verify-and-regenerate loop(Stage V)**: Validates patient record content and examination results before saving the final profile.
- **Append-only output**: Saves multiple cases into one final JSON list.

## How It Works

`generate_character()` runs the full PatientZero pipeline for the disease configured by `disease_key`:

1. **Stage I: Disease outline standardization** - if the disease is not already present in `disease_outlines.json`, the generator converts the matching raw outline into a standardized `DiseaseOutline`.
2. **Stage II: Attribute permutation** - samples a valid patient attribute vector from `attribute_priors.json` plus disease-specific overrides in `disease_attribute_priors.json`.
3. **Stage III: Patient record and symptoms** - generates `patient_profile` and `symptom_trajectory` from the sampled attributes and disease outline.
4. **Stage IV: Examination results** - generates mental status exam, scale assessments, risk assessment, exclusionary findings, and a clinical summary.
5. **Stage V: Validation** - checks Stage III and Stage IV outputs. Failed generations are retried with revision guidance.
6. **Final save** - appends the validated record to `output_path`.

The final observable profile follows the paper's static record definition `P = {B, S, E}`:

- `B`: background patient profile
- `S`: symptom trajectory
- `E`: examination results

The disease outline `O` is used as a latent scaffold and is not part of the role-play schema requirement.

## Supported Diseases

The default PatientZero resources currently include the following diseases. These entries have the required raw outline, standardized disease outline, disease-specific attribute priors, and examination references, so they can be used directly as `disease_key` values.

| Disease Key | Disease Name |
| ----------- | ------------ |
| `adhd` | ADHD |
| `anxiety_disorder` | Anxiety Disorder |
| `bipolar_disorder` | Bipolar Disorder |
| `depression` | Depression |
| `insomnia` | Insomnia |
| `ocd` | OCD |
| `ptsd` | PTSD |
| `schizophrenia` | Schizophrenia |

## Usage

```python
from omegaconf import OmegaConf
from patienthub.generators import get_generator

config = OmegaConf.create({
    "agent_name": "patientZero",
    "model_type": "OPENAI",
    "model_name": "gpt-4o",
    "temperature": 0.7,
    "max_tokens": 8192,
    "max_retries": 3,
    "prompt_path": "data/prompts/generator/patientZero.yaml",
    "source_data_dir": "data/resources/PatientZero",
    "output_path": "data/characters/PatientZero.json",
    "disease_key": "depression",
    "random_seed": 0,
})

generator = get_generator(agent_name="patientZero", configs=config, lang="en")
generator.generate_character()
```

## Configuration

| Parameter         | Type        | Default                                      | Description                                                     |
| ----------------- | ----------- | -------------------------------------------- | --------------------------------------------------------------- |
| `prompt_path`     | string      | `data/prompts/generator/patientZero.yaml`    | Path to PatientZero prompts                                     |
| `source_data_dir` | string      | `data/resources/PatientZero`                 | Folder for source data, priors, examination references, and reusable disease outlines |
| `output_path`     | string      | `data/characters/PatientZero.json`           | Final JSON file where validated records are appended            |
| `disease_key`     | string      | `depression`                                 | Target disease key, for example `depression` or `insomnia`      |
| `random_seed`     | int/null    | `None`                                       | Optional seed for reproducible attribute sampling               |                                          |
| `max_retries`     | int         | `3`                                          | API retry attempts                                              |

## Output Format

The final output file is a JSON array. Each call appends one validated case:

```json
[
  {
    "metadata": {
      "disease_name": "Major Depressive Disorder",
      "disease_key": "depression",
      "severity_level": "severe",
      "seed": 0,
      "case_index": 0,
      "case_id": "depression_0"
    },
    "patient_profile": {
      "age": 34,
      "age_strata": "Adult",
      "biological_sex": "Female",
      "physiological_status": "Non-pregnant",
      "ethnicity": "Caucasian",
      "geography": "Urban (Metropolitan)",
      "communication_style": "Reserved",
      "name": "Example Patient",
      "lifestyle_summary": "...",
      "past_medical_history": "...",
      "family_history": "..."
    },
    "symptom_trajectory": {
      "current_severity": "severe",
      "chief_complaint": "...",
      "onset": "...",
      "duration": "...",
      "selected_symptoms": [
        {
          "name": "Persistent low mood",
          "duration": "8 weeks",
          "severity": "severe",
          "impact": "..."
        }
      ]
    },
    "examination_results": {
      "mental_status_exam": {
        "appearance_behavior": "...",
        "speech": "...",
        "mood_affect": "..."
      },
      "scale_assessments": [
        {
          "scale_name": "PHQ-9",
          "score": 22,
          "severity_interpretation": "Severe",
          "rationale": "..."
        }
      ],
      "risk_assessment": {
        "suicide_risk": "moderate",
        "violence_risk": "none",
        "self_neglect_risk": "low",
        "rationale": "..."
      },
      "clinical_summary": "..."
    }
  }
]
```

The role-play schema requires `patient_profile`, `symptom_trajectory`, and `examination_results`. Metadata and validation logs may be present in generator output, but they are not required for adapter-level profile conversion.

## Required Data Files

PatientZero depends on both disease knowledge and attribute priors. With the default paths, the generator expects these files:

| File | Location | Purpose |
| ---- | -------- | ------- |
| `raw_outlines.json` | `source_data_dir` | Human-provided disease knowledge gathered from authoritative sources |
| `attribute_priors.json` | `source_data_dir` | Global demographic, socioeconomic, lifestyle, and communication distributions |
| `disease_attribute_priors.json` | `source_data_dir` | Disease-specific overrides for age, sex, severity, or other sampled attributes |
| `exam_references.json` | `source_data_dir` | Disease-specific clinical scales and exclusionary findings |
| `disease_outlines.json` | `source_data_dir` | Reusable standardized disease outlines used by later generation stages |

`source_data_dir` contains both human-provided priors and reusable standardized outlines. `disease_outlines.json` may be generated by Stage I, but it is saved beside the source files because it can be reused across future runs.

## Adding a New Disease

To add a disease, choose a stable normalized key such as `social_anxiety_disorder` and add matching entries to the source files.

### 1. Gather Authoritative Disease Knowledge

Prefer official or professional medical sources:

- Government or public-health agencies, for example NIMH, CDC, WHO, NIH, NHLBI
- Professional clinical organizations or guideline bodies
- Peer-reviewed reviews or diagnostic resources when official pages are insufficient

Collect content that can support:

- Disease summary and core clinical characteristics
- Common symptoms and symptom timing
- Severity-specific presentation differences
- Special populations, such as children, older adults, pregnancy
- Red flags, contraindications, and differential diagnoses
- Recommended scales or examinations

### 2. Add the Raw Outline

Add one entry to `data/resources/PatientZero/raw_outlines.json`:

```json
{
  "social_anxiety_disorder": {
    "disease_name": "Social Anxiety Disorder",
    "stage": "disease_outline_standardization",
    "retrieval_date": "2026-05-07",
    "evidence_note": "Summarized from official clinical source material for synthetic case generation.",
    "sources": [
      {
        "title": "Source title",
        "publisher": "Source publisher",
        "url": "https://example.org/source-page"
      }
    ],
    "raw_outline": {
      "summary": "...",
      "core_features": ["..."],
      "common_symptoms": ["..."],
      "course_and_timing": ["..."],
      "severity_notes": {
        "mild": "...",
        "moderate": "...",
        "severe": "..."
      },
      "special_populations": ["..."],
      "red_flags": ["..."],
      "differential_considerations": ["..."]
    }
  }
}
```

The generator can standardize this into `disease_outlines.json` automatically when `disease_key` is used and the standardized outline does not yet exist.

### 3. Add Disease-Specific Attribute Priors

Add one entry to `data/resources/PatientZero/disease_attribute_priors.json`. Each override should include `source`, `method`, and `labels`:

```json
{
  "social_anxiety_disorder": {
    "age_strata": {
      "source": [
        {
          "title": "Source title",
          "url": "https://example.org/prevalence-page",
          "evidence": "Age-specific prevalence or onset information."
        }
      ],
      "method": "labels are normalized PatientZero sampling weights mapped from source age bands.",
      "labels": {
        "Child": 0.25,
        "Adult": 0.70,
        "Elderly": 0.05
      }
    },
    "biological_sex": {
      "source": [
        {
          "title": "Source title",
          "url": "https://example.org/prevalence-page",
          "evidence": "Sex-specific prevalence information."
        }
      ],
      "method": "labels are normalized PatientZero sampling weights mapped from source male/female prevalence.",
      "labels": {
        "Male": 0.45,
        "Female": 0.55
      }
    },
    "severity_level": {
      "source": [
        {
          "title": "Source title",
          "url": "https://example.org/severity-page",
          "evidence": "Severity, impairment, or clinical-presentation distribution information."
        }
      ],
      "method": "labels map source severity or impairment categories to mild/moderate/severe.",
      "labels": {
        "mild": 0.40,
        "moderate": 0.35,
        "severe": 0.25
      }
    }
  }
}
```

Only fields that differ from the global priors need to be added. Fields not specified here fall back to `attribute_priors.json`.

### 4. Add Examination References

Add one entry to `data/resources/PatientZero/exam_references.json` under `diseases`:

```json
{
  "diseases": {
    "social_anxiety_disorder": {
      "selected_scales": ["GAD-7"],
      "exclusionary_findings": [
        "substance and medication review",
        "screen for panic symptoms when clinically relevant"
      ]
    }
  }
}
```

`selected_scales` must refer to scales already defined in `scale_pool`. If a new scale is needed, first add it to `scale_pool` with its score range and interpretation notes.

### 5. Generate the Disease Case

Set `disease_key` to the new key:

```python
config.disease_key = "social_anxiety_disorder"
config.random_seed = 0
generator = get_generator(agent_name="patientZero", configs=config, lang="en")
generator.generate_character()
```

If the standardized outline is missing, Stage I writes it to `source_data_dir/disease_outlines.json`. The final validated case is appended to `output_path`.

## Use Cases

- Creating role-play-ready psychiatric patient profiles without using real patient records
- Building disease-specific synthetic case banks with controlled demographic and severity distributions
- Evaluating clinical interview agents with cases that include symptoms, mental status findings, scales, and risk assessment
