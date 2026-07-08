# PatientHub

> A unified hub to create, simulate, and evaluate methods for patient/client simulation.

📚 **[Documentation](https://sahandfer.github.io/PatientHub/)** | 🚀 **[Quick Start](#quick-start)** | 📄 **[Paper](https://arxiv.org/abs/2602.11684)**

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
patienthub simulate
```

You can also override any configuration via the command line:

```bash
patienthub simulate client=patientPsi therapist=basic evaluator=conv_judge evaluator.prompt_path=data/prompts/evaluator/client_conv.yaml
```

### Other examples

**Create** scaffolding for a new agent:

```bash
patienthub create agent_type=client agent_name=myClient
```

**Evaluate** a recorded session:

```bash
patienthub evaluate evaluator=conv_judge evaluator.prompt_path=data/prompts/evaluator/client_conv.yaml input_dir=data/sessions/default/badtherapist.json
```

**Generate** a character profile:

```bash
patienthub generate generator=psyche
```

**Adapt** a character profile from one client format to another:

```bash
patienthub adapt input_path=data/characters/patientPsi.json target_client=roleplayDoh
```

**Run the web demo** (requires `dev` dependencies):

```bash
uv sync --extra dev
uv run python -m chainlit run examples/chainlit.py
```

## Supported Agents

### Clients (Patients)

| Client       | Key            | Description                                                                                                                                                   |
| ------------ | -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| SAPS         | `saps`         | State-aware patient simulator for clinical diagnosis ([ArXiv](https://arxiv.org/pdf/2403.08495))                                                              |
| ConsistentMI | `consistentMI` | Consistent client simulation for Motivational Interviewing counseling ([ACL 2025 Main](https://aclanthology.org/2025.acl-long.1021/))                         |
| Eeyore       | `eeyore`       | Realistic depression simulation via expert-in-the-loop SFT and preference optimization ([ACL 2025 Findings](https://aclanthology.org/2025.findings-acl.707/)) |
| AnnaAgent    | `annaAgent`    | Dynamic evolution agent with multi-session memory for realistic seeker simulation ([ACL 2025 Findings](https://aclanthology.org/2025.findings-acl.1192/))     |
| Adaptive-VP  | `adaptiveVP`   | LLM virtual patients that adapt to trainee dialogue for nurse communication training ([ACL 2025 Findings](https://aclanthology.org/2025.findings-acl.118/))   |
| SimPatient   | `simPatient`   | Simulated patients for MI-based counselor training on alcohol misuse ([CHI 2025](https://dl.acm.org/doi/full/10.1145/3706598.3714014))                        |
| TalkDep      | `talkDep`      | Clinically grounded LLM personas for conversation-centric depression screening ([CIKM 2025](https://dl.acm.org/doi/10.1145/3746252.3761617))                  |
| ClientCAST   | `clientCast`   | Client-centered assessment of LLM therapists via client simulation ([ArXiv](https://github.com/wangjs9/ClientCAST))                                           |
| PSYCHE       | `psyche`       | Multi-faceted patient simulation for evaluating psychiatric assessment agents ([ArXiv](https://arxiv.org/pdf/2501.01594))                                     |
| MindVoyager  | `mindVoyager`  | Progressively disclosed cognitive-diagram client modeling metacognition and openness ([ACL 2025 Findings](https://aclanthology.org/2025.findings-acl.1332/))  |
| PATIENT-Ψ    | `patientPsi`   | LLM patients for training mental health professionals in CBT ([EMNLP 2024 Main](https://aclanthology.org/2024.emnlp-main.711/))                               |
| Roleplay-doh | `roleplayDoh`  | Domain-expert-authored LLM patients via eliciting and adhering to principles ([EMNLP 2024 Main](https://aclanthology.org/2024.emnlp-main.591/))               |
| PatientZero  | `patientZero`  | Disease-grounded synthetic patient records sampled from attribute priors ([ArXiv](https://arxiv.org/pdf/2509.11078))                                          |
| Deprofile    | `deprofile`    | Patient built from a decomposed clinical profile with matched dialogues and a social-media timeline                                                           |
| CARS         | `cars`         | CBT-grounded resistance-aware simulation driven by Cognitive Conceptualization Diagrams ([ArXiv](https://arxiv.org/abs/2606.04389))                           |
| User         | `user`         | Human-in-the-loop client (manual input)                                                                                                                       |

### Therapists

| Therapist        | Key      | Description                                                             |
| ---------------- | -------- | ----------------------------------------------------------------------- |
| Basic (CBT)      | `basic`  | Cognitive Behavioral Therapy therapist (with optional chain-of-thought) |
| CAMI             | `cami`   | Motivational Interviewing therapist with topic-graph guidance           |
| PSYCHE Therapist | `psyche` | Therapist from the PSYCHE psychiatric assessment framework              |
| Eliza            | `eliza`  | Classic pattern-matching Rogerian therapist                             |
| User             | `user`   | Human-in-the-loop therapist                                             |

### Evaluators

| Evaluator                | Key             | Description                                       |
| ------------------------ | --------------- | ------------------------------------------------- |
| LLM Judge (Conversation) | `conv_judge`    | LLM-based evaluation of therapy conversations     |
| LLM Judge (Profile)      | `profile_judge` | LLM-based evaluation of generated client profiles |

### Generators

| Generator   | Key           | Description                                                              |
| ----------- | ------------- | ------------------------------------------------------------------------ |
| PSYCHE      | `psyche`      | MFC psychiatric profiles for assessment training                         |
| ClientCast  | `clientCast`  | Profiles from conversation excerpts via Big Five and clinical scales     |
| AnnaAgent   | `annaAgent`   | Multi-session profiles with scales and memory states                     |
| PatientZero | `patientZero` | Disease-grounded synthetic patient records with sampled priors           |
| Deprofile   | `deprofile`   | Clinical/social profile assembly with matched timelines and memory cards |
| CARS        | `cars`        | CBT resistance profiles from a CCD and seed statements                   |

## Project Structure

```text
docs/               # Documentation site (Docusaurus)

data/
├── characters/     # Character profiles (JSON)
├── prompts/        # Prompt templates (YAML, per agent)
├── sessions/       # Saved session logs
└── resources/      # Source datasets and auxiliary files

patienthub/
├── clients/        # Client (patient) agent implementations
├── therapists/     # Therapist agent implementations
├── evaluators/     # Evaluation modules
├── generators/     # Character profile generators
├── events/         # Session orchestration (Burr-based)
├── npcs/           # Non-player character agents
├── configs/        # Hydra config utilities
├── cli/            # CLI entry points
└── utils/          # File I/O, model helpers

```

## License

See [LICENSE](./LICENSE) for details.

## Citation

If you find our work useful for your research, please kindly cite our paper as follows:

```bibtex
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
