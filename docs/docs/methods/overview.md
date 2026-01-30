---
sidebar_position: 0
---

# Supported Agents Overview

PatientHub implements various agent types for comprehensive therapy simulation research. This includes client agents (patient simulations) from leading AI and HCI venues, as well as therapist agents, evaluators, NPCs, and generators.

## Agent Categories

- **[Clients](./saps.md)** - Patient simulation agents with various disorders and behaviors
- **[Therapists](./therapists.md)** - Therapeutic intervention agents (CBT, Eliza, etc.)
- **[Evaluators](./evaluators.md)** - Assessment agents for measuring therapy quality
- **[NPCs](./npcs.md)** - Supporting characters for complex scenarios
- **[Generators](./generators.md)** - Tools for creating synthetic client profiles

## Client Agents Summary

| Method                                     | Venue          | Year | Focus Area                | Key Feature                 |
| ------------------------------------------ | -------------- | ---- | ------------------------- | --------------------------- |
| [SAPS](/docs/methods/saps)                 | ArXiv          | 2024 | Clinical Diagnosis        | State-aware responses       |
| [ConsistentMI](/docs/methods/consistentmi) | ACL (Main)     | 2025 | Motivational Interviewing | Stage-of-change transitions |
| [Eeyore](/docs/methods/eeyore)             | ACL (Findings) | 2025 | Depression                | Expert-validated simulation |
| [AnnaAgent](/docs/methods/annaagent)       | ACL (Findings) | 2025 | Multi-session             | Dynamic memory evolution    |
| [AdaptiveVP](/docs/methods/adaptivevp)     | ACL (Findings) | 2025 | Nurse Training            | Adaptive dialogue           |
| [SimPatient](/docs/methods/simpatient)     | CHI            | 2025 | Alcohol Misuse            | Cognitive state updates     |
| [TalkDep](/docs/methods/talkdep)           | CIKM           | 2025 | Depression Screening      | Clinical grounding          |
| [ClientCAST](/docs/methods/clientcast)     | ArXiv          | 2024 | Psychotherapy             | Client-centered assessment  |
| [PSYCHE](/docs/methods/psyche)             | ArXiv          | 2025 | Psychiatric Assessment    | Multi-faceted evaluation    |
| [PatientPsi](/docs/methods/patientpsi)     | EMNLP (Main)   | 2024 | CBT                       | Cognitive model-based       |
| [RoleplayDoh](/docs/methods/roleplaydoh)   | EMNLP (Main)   | 2024 | Counseling                | Principle-based simulation  |

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

### For Nurse Training

→ Use **AdaptiveVP**

## Quick Start by Method

### PatientPsi

```bash
uv run python -m examples.simulate client=patientPsi therapist=CBT
```

### ConsistentMI

```bash
uv run python -m examples.simulate client=consistentMI therapist=CBT
```

### Eeyore

```bash
uv run python -m examples.simulate client=eeyore therapist=user
```

### AdaptiveVP (Nurse Training)

```bash
uv run python -m examples.simulate client=adaptiveVP therapist=user
```

## Adding New Methods

See [Contributing: New Agents](/docs/contributing/new-agents) to implement additional patient simulation methods.
