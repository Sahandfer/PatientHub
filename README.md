# Backend

> The Backend of the patient simulation project (using LangChain + FastAPI)

# Supported Agents

## Clients

- [x] Custom agent (`basic`) -> for testing purposes
- [x] PatientPsi (`patientPsi`) -> from https://arxiv.org/abs/2405.19660
- [x] RoleplayDoh -> from https://aclanthology.org/2024.emnlp-main.591/
- [ ] Eeyore -> from https://aclanthology.org/2025.findings-acl.707.pdf
- [ ] EvoPatient -> from https://github.com/ZJUMAI/EvoPatient

# Guide

- Create a file named `.env` and fill it with the following values

```bash
LAB_API_KEY=<your API key>
LAB_BASE_URL=http://115.182.62.174:18888/v1
```

- Run the following script for simulation

```bash
uv run src/simulate.py
```
