---
sidebar_position: 1
---

# Supported Methods Overview

PatientHub implements patient simulation methods from leading AI and HCI venues.

## Method Summary

| Method                                     | Venue          | Year | Focus Area                | Key Feature                 |
| ------------------------------------------ | -------------- | ---- | ------------------------- | --------------------------- |
| [ConsistentMI](/docs/methods/consistentmi) | ACL (Main)     | 2025 | Motivational Interviewing | Stage-of-change transitions |
| [Eeyore](/docs/methods/eeyore)             | ACL (Findings) | 2025 | Depression                | Expert-validated simulation |
| AnnaAgent                                  | ACL (Findings) | 2025 | Multi-session             | Dynamic memory evolution    |
| AdaptiveVP                                 | ACL (Findings) | 2025 | Nurse Training            | Adaptive dialogue           |
| [PatientPsi](/docs/methods/patientpsi)     | EMNLP (Main)   | 2024 | CBT                       | Cognitive model-based       |
| RoleplayDoh                                | EMNLP (Main)   | 2024 | Counseling                | Principle-based simulation  |
| SimPatient                                 | CHI            | 2025 | Alcohol Misuse            | Cognitive state updates     |
| TalkDep                                    | CIKM           | 2025 | Depression Screening      | Clinical grounding          |
| SAPS                                       | ArXiv          | 2024 | Clinical Diagnosis        | State-aware responses       |
| ClientCast                                 | ArXiv          | 2024 | Psychotherapy             | Client-centered assessment  |
| Psyche                                     | ArXiv          | 2025 | Psychiatric Assessment    | Multi-faceted evaluation    |

## By Focus Area

### Depression & Mood Disorders

- **Eeyore**: Realistic depression simulation with expert validation
- **TalkDep**: Clinically grounded personas for depression screening

### Motivational Interviewing

- **ConsistentMI**: Stage-of-change model with consistent behavior
- **SimPatient**: Cognitive model with internal state tracking

### General Psychotherapy

- **PatientPsi**: CBT-focused with cognitive distortions
- **RoleplayDoh**: Domain-expert created principles
- **ClientCast**: Assessment-focused simulation

### Specialized Training

- **AdaptiveVP**: Nurse communication training
- **SAPS**: Medical diagnosis training
- **Psyche**: Psychiatric assessment training

## Comparison

### Complexity vs. Realism Trade-off

```
High Realism
    │
    │   ConsistentMI ●
    │              Eeyore ●
    │         SimPatient ●
    │    PatientPsi ●
    │         RoleplayDoh ●
    │   SAPS ●
    │ Basic ●
    │
    └────────────────────────► High Complexity
```

### Feature Comparison

| Feature           | PatientPsi | ConsistentMI | Eeyore | SimPatient |
| ----------------- | ---------- | ------------ | ------ | ---------- |
| Cognitive Model   | ✅         | ✅           | ✅     | ✅         |
| Stage Transitions | ❌         | ✅           | ❌     | ❌         |
| Multi-session     | ❌         | ❌           | ❌     | ✅         |
| Expert Validated  | ❌         | ✅           | ✅     | ✅         |
| Internal State    | ✅         | ✅           | ✅     | ✅         |

## Choosing a Method

### For CBT Training

→ Use **PatientPsi** or **Psyche**

### For MI Training

→ Use **ConsistentMI** or **SimPatient**

### For Depression Screening Research

→ Use **Eeyore** or **TalkDep**

### For Medical Diagnosis Training

→ Use **SAPS**

### For General Counseling

→ Use **RoleplayDoh** or **ClientCast**

### For Multi-session Studies

→ Use **AnnaAgent** or **SimPatient**

## Quick Start by Method

### PatientPsi

```bash
uv run python -m examples.simulate client=patientPsi therapist=CBT
```

### ConsistentMI

```bash
uv run python -m examples.simulate client=consistentMI therapist=MI
```

### Eeyore

```bash
uv run python -m examples.simulate client=eeyore therapist=user
```

## Adding New Methods

See [Contributing: New Agents](/docs/contributing/new-agents) to implement additional patient simulation methods.
