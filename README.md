# PatientHub

> A unified hub to create, simulate, and evaluate methods for patient/client simulation.

## Quick Start

### 1. Setting up the environment

Set up and activate the virtual environment (after installing [uv](https://docs.astral.sh/uv/getting-started/installation/))

```bash
uv sync
source .venv/bin/activate
```

Create a file named `.env` and fill it with the following values:

```bash
LAB_API_KEY=<your API key>
LAB_BASE_URL=http://115.182.62.174:18888/v1
```

### 2. Running simulations

Run the following script for simulation (with default configs)

```bash
uv run python -m examples.simulate
```

You can also run the following script to run customized simulations.

```bash
uv run python -m examples.simulate client=[client] therapist=[therapist] evaluator=evaluator evaluator.eval_type=[eval_type]
```

### 3. Supported Agents

#### Clients (Patients)

| Source / Description                                                                                                                                                   | Venue               | Focus                              | Agent                                                  |
| :--------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | ---------------------------------- | ------------------------------------------------------ |
| [Automatic Interactive Evaluation for Large Language Models with State Aware Patient Simulator](https://arxiv.org/pdf/2403.08495)       | ArXiv               | General (Clinical Diagnosis)               | [`SAPS`](./patienthub/clients/SAPS.py)   |
| [Consistent Client Simulation for Motivational Interviewing-based Counseling](https://aclanthology.org/2025.acl-long.1021/)                                            | ACL 2025 (Main)     | General (MI)                       | [`consistentMI`](./patienthub/clients/consistentMI.py) |
| [Eeyore: Realistic Depression Simulation via Expert-in-the-Loop Supervised and Preference Optimization](https://aclanthology.org/2025.findings-acl.707/)               | ACL 2025 (Findings) | Depression (Screening/General)     | [`eeyore`](./patienthub/clients/eeyore.py)             |
| [AnnaAgent: Dynamic Evolution Agent System with Multi-Session Memory for Realistic Seeker Simulation](https://aclanthology.org/2025.findings-acl.1192/)                | ACL 2025 (Findings) | General (Multi-session Counseling) | [`annaAgent`](./patienthub/clients/annaAgent.py)       |
| [Scaffolding Empathy: Training Counselors with Simulated Patients and Utterance-level Performance Visualizations](https://dl.acm.org/doi/full/10.1145/3706598.3714014) | CHI 2025            | Alcohol Misuse (MI)                | [`simPatient`](./patienthub/clients/simPatient.py)     |
| [TalkDep: Clinically Grounded LLM Personas for Conversation-Centric Depression Screening](https://dl.acm.org/doi/10.1145/3746252.3761617)                              | CIKM 2025           | Depression (Diagnosis)             | [`talkDep`](./patienthub/clients/talkDep.py)           |
| [Towards a Client-Centered Assessment of LLM Therapists by Client Simulation](https://github.com/wangjs9/ClientCAST)                                                   | Arxiv               | General (Psychotherapy)            | [`clientCast`](./patienthub/clients/clientCast.py)     |
| [PSYCHE: A Multi-faceted Patient Simulation Framework for Evaluation of Psychiatric Assessment Conversational Agents](https://arxiv.org/pdf/2501.01594)                | ArXiv               | General (Psychiatric Assessment)   | [`psyche`](./patienthub/clients/psyche.py)             |
| [PATIENT-Ψ: Using Large Language Models to Simulate Patients for Training Mental Health Professionals](https://aclanthology.org/2024.emnlp-main.711/)                  | EMNLP 2024 (Main)   | General (CBT)                      | [`patientPsi`](./patienthub/clients/patientPsi.py)     |
| [Roleplay-doh: Enabling Domain-Experts to Create LLM-simulated Patients via Eliciting and Adhering to Principles](https://aclanthology.org/2024.emnlp-main.591/)       | EMNLP 2024 (Main)   | General (Counseling)               | [`roleplayDoh`](./patienthub/clients/roleplayDoh.py)   |

#### Therapists

- `basic` → custom therapist for testing purposes
- `eliza` → simple implementation of the Eliza chatbot
- `user `→ user role-playing as a therapist

#### Evaluators

- `basic` → custom evaluator for testing purposes

- `eval_type` can be one of the following
  - `cbt`
  - `active_listening`

### 3. Creating new agents

You can run the following command to create the necessary files for a new agent:

```bash
uv run python -m examples.create generator.gen_agent_type=[client|therapist] generator.gen_agent_name=<agent_name>
```

For example

```bash
uv run python -m examples.create generator.gen_agent_type=client generator.gen_agent_name=test
```

## Project Structure

```
patienthub/
├── base/           # Base classes (ChatAgent, etc.)
├── clients/        # Client agent implementations + configs
├── therapists/     # Therapist agent implementations + configs
├── evaluators/     # Evaluation modules
├── generators/     # Character/file/event generators
├── configs/        # Shared config utilities
├── brain/          # Mental state modeling
├── events/         # Session management
└── utils/          # Helpers

examples/           # CLI entry points
data/
├── characters/     # Character profiles (JSON)
├── prompts/        # Prompt templates (YAML)
├── sessions/       # Session logs
└── resources/            # Source datasets
```
