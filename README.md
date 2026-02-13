# PatientHub

> A unified hub to create, simulate, and evaluate methods for patient/client simulation.

📚 **[Documentation](https://sahandfer.github.io/PatientHub/)** | 🚀 **[Quick Start](#quick-start)** | 📦 **[Supported Agents](#supported-agents)**

## Quick Start

### Setting up the environment

Set up and activate the virtual environment (after installing [uv](https://docs.astral.sh/uv/getting-started/installation/))

```bash
uv sync
source .venv/bin/activate
```

Create a file named `.env` and fill it with your API credentials:

```bash
OPENAI_API_KEY=<your API key>
OPENAI_BASE_URL=<your API base URL> # Optional
```

### Running simulations

Run the following script for simulation (with default configs):

```bash
uv run python -m examples.simulate
```

You can also override any configuration via the command line:

```bash
uv run python -m examples.simulate client=patientPsi therapist=basic evaluator=llm_judge
```

### Other examples

**Create** scaffolding for a new agent:

```bash
uv run python -m examples.create agent_type=client agent_name=myClient
```

**Evaluate** a recorded session:

```bash
uv run python -m examples.evaluate evaluator=llm_judge input_dir=data/sessions/default/session.json
```

**Generate** a character profile:

```bash
uv run python -m examples.generate generator=psyche
```

**Run the web demo** (requires `dev` dependencies):

```bash
uv run chainlit run examples/chainlit.py
```

## Supported Agents

### Clients (Patients)

| Source / Description                                                                                                                                                                     | Venue               | Focus                                  | Agent                                                  |
| :--------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ------------------- | -------------------------------------- | ------------------------------------------------------ |
| [Automatic Interactive Evaluation for Large Language Models with State Aware Patient Simulator](https://arxiv.org/pdf/2403.08495)                                                        | ArXiv               | General (Clinical Diagnosis)           | [`saps`](./patienthub/clients/saps.py)                 |
| [Consistent Client Simulation for Motivational Interviewing-based Counseling](https://aclanthology.org/2025.acl-long.1021/)                                                              | ACL 2025 (Main)     | General (MI)                           | [`consistentMI`](./patienthub/clients/consistentMI.py) |
| [Eeyore: Realistic Depression Simulation via Expert-in-the-Loop Supervised and Preference Optimization](https://aclanthology.org/2025.findings-acl.707/)                                 | ACL 2025 (Findings) | Depression (Screening/General)         | [`eeyore`](./patienthub/clients/eeyore.py)             |
| [AnnaAgent: Dynamic Evolution Agent System with Multi-Session Memory for Realistic Seeker Simulation](https://aclanthology.org/2025.findings-acl.1192/)                                  | ACL 2025 (Findings) | General (Multi-session Counseling)     | [`annaAgent`](./patienthub/clients/annaAgent.py)       |
| [ Adaptive-VP: A Framework for LLM-Based Virtual Patients that Adapts to Trainees’ Dialogue to Facilitate Nurse Communication Training](https://aclanthology.org/2025.findings-acl.118/) | ACL 2025 (Findings) | General (Nurse Communication Training) | [`adaptiveVP`](./patienthub/clients/adaptiveVP.py)     |
| [Scaffolding Empathy: Training Counselors with Simulated Patients and Utterance-level Performance Visualizations](https://dl.acm.org/doi/full/10.1145/3706598.3714014)                   | CHI 2025            | Alcohol Misuse (MI)                    | [`simPatient`](./patienthub/clients/simPatient.py)     |
| [TalkDep: Clinically Grounded LLM Personas for Conversation-Centric Depression Screening](https://dl.acm.org/doi/10.1145/3746252.3761617)                                                | CIKM 2025           | Depression (Diagnosis)                 | [`talkDep`](./patienthub/clients/talkDep.py)           |
| [Towards a Client-Centered Assessment of LLM Therapists by Client Simulation](https://github.com/wangjs9/ClientCAST)                                                                     | Arxiv               | General (Psychotherapy)                | [`clientCast`](./patienthub/clients/clientCast.py)     |
| [PSYCHE: A Multi-faceted Patient Simulation Framework for Evaluation of Psychiatric Assessment Conversational Agents](https://arxiv.org/pdf/2501.01594)                                  | ArXiv               | General (Psychiatric Assessment)       | [`psyche`](./patienthub/clients/psyche.py)             |
| [PATIENT-Ψ: Using Large Language Models to Simulate Patients for Training Mental Health Professionals](https://aclanthology.org/2024.emnlp-main.711/)                                    | EMNLP 2024 (Main)   | General (CBT)                          | [`patientPsi`](./patienthub/clients/patientPsi.py)     |
| [Roleplay-doh: Enabling Domain-Experts to Create LLM-simulated Patients via Eliciting and Adhering to Principles](https://aclanthology.org/2024.emnlp-main.591/)                         | EMNLP 2024 (Main)   | General (Counseling)                   | [`roleplayDoh`](./patienthub/clients/roleplayDoh.py)   |

### Therapists

| Therapist        | Key      | Description                                                             |
| ---------------- | -------- | ----------------------------------------------------------------------- |
| Basic (CBT)      | `basic`  | Cognitive Behavioral Therapy therapist (with optional chain-of-thought) |
| CAMI             | `cami`   | Motivational Interviewing therapist with topic-graph guidance           |
| PSYCHE Therapist | `psyche` | Therapist from the PSYCHE psychiatric assessment framework              |
| Eliza            | `eliza`  | Classic pattern-matching Rogerian therapist                             |
| User             | `user`   | Human-in-the-loop therapist                                             |

### Evaluators

| Evaluator | Key         | Description                              |
| --------- | ----------- | ---------------------------------------- |
| LLM Judge | `llm_judge` | LLM-based evaluation of therapy sessions |

### Generators

| Generator  | Key          | Description                         |
| ---------- | ------------ | ----------------------------------- |
| PSYCHE     | `psyche`     | Character generation for PSYCHE     |
| ClientCast | `clientCast` | Character generation for ClientCast |
| AnnaAgent  | `annaAgent`  | Character generation for AnnaAgent  |

## Project Structure

```
patienthub/
├── clients/        # Client (patient) agent implementations
├── therapists/     # Therapist agent implementations
├── evaluators/     # Evaluation modules
├── generators/     # Character profile generators
├── events/         # Session orchestration (Burr-based)
├── npcs/           # Non-player character agents
├── configs/        # Hydra config utilities
└── utils/          # File I/O, model helpers

examples/           # CLI entry points (simulate, evaluate, generate, create, interview)
data/
├── characters/     # Character profiles (JSON)
├── prompts/        # Prompt templates (YAML, per agent)
├── sessions/       # Saved session logs
└── resources/      # Source datasets and auxiliary files

docs/               # Documentation site (Docusaurus)
```

## License

See [LICENSE](./LICENSE) for details.

## Citation

If you find our work useful for your research, please kindly cite our paper as follows:

```
@misc{sabour2026patienthub,
      title={PatientHub: A Unified Framework for Patient Simulation},
      author={Sahand Sabour and TszYam NG and Minlie Huang},
      year={2026},
      eprint={2602.11684},
      archivePrefix={arXiv},
      primaryClass={cs.CL},
      url={https://arxiv.org/abs/2602.11684},
}
```
