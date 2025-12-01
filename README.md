# PatientHub

> A unified hub to create, simulate, and evaluate methods for patient/client simulation.

# Supported Clients

- [x] Custom basic for testing purposes
- [x] PatientPsi from https://arxiv.org/abs/2405.19660
- [x] RoleplayDoh from https://aclanthology.org/2024.emnlp-main.591/
- [x] Eeyore from https://aclanthology.org/2025.findings-acl.707.pdf
- [ ] EvoPatient from https://github.com/ZJUMAI/EvoPatient

# Guide

## 1. Setting up the environment

Set up and activate the virtual environment (after installling [uv](https://docs.astral.sh/uv/getting-started/installation/))

```bash
uv sync
source .venv/bin/activate
```

Create a file named `.env` and fill it with the following values

```bash
LAB_API_KEY=<your API key>
LAB_BASE_URL=http://115.182.62.174:18888/v1
```

## 2. Running simulations

Run the following script for simulation (with default configs)

```bash
uv run python -m src.scripts.simulate 
```

In addition, you can run the following script for customized simulations

```bash
uv run python -m src.scripts.simulate client=[client] therapist=[therapist] evaluator=evaluator evaluator.eval_type=[eval_type]
```

- `client` can be one of the following
  - `basic` → custom client for testing purposes
  - `patientPsi`
  - `roleplayDoh`
  - `eeyore`
- `therapist` can be one of the following
  - `basic` → custom therapist for testing purposes
  - `eliza` → simple implementation of the eliza chatbot
  - `user `→ user role-playing as a therapist
- `evaluator` can be one of the following
  - `basic` → custom evaluator for testing purposes
- `eval_type` can be one of the following
  - `cbt` 
  - `active_listening` 

## 3. Creating new clients

[TODO]
