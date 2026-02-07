---
sidebar_position: 1
---

# Installation

## Requirements

- Python 3.12+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or pip

## Install with uv (Recommended)

```bash
# Clone the repository
git clone https://github.com/Sahandfer/PatientHub.git
cd PatientHub

# Install dependencies
uv sync

# Activate the environment
source .venv/bin/activate
```

## Install with pip

```bash
# Clone the repository
git clone https://github.com/Sahandfer/PatientHub.git
cd PatientHub

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install
pip install -e .
```

## Configuration
Create a `.env` file in the project root:  
### Cloud Models

```bash
OPENAI_API_KEY=<your API key>
OPENAI_BASE_URL=https://api.openai.com
```

:::tip Using Other Providers
PatientHub supports cloud and local models. See [Configuration](/docs/getting-started/configuration) for details.
:::

### Local Models via vLLM
Our recommended setup for local models is to run a vLLM (or OpenAI-compatible) server on a machine/process, then have PatientHub call it over HTTP via `LOCAL_BASE_URL`.

1) Install vLLM on the serving machine (GPU recommended):

```bash
pip install -U vllm
```

2) Serve a model with the OpenAI-compatible endpoint (example):

```bash
vllm serve Qwen/Qwen2.5-7B-Instruct --host 0.0.0.0 --port 8000
```

3) Point PatientHub to the server in your `.env`:

```bash
LOCAL_BASE_URL=http://<SERVER_HOST>:8000/v1
LOCAL_API_KEY=EMPTY
```

Then set your config to use `model_type=LOCAL` and `model_name` to the model name exposed by your vLLM server.

:::note vLLM fails to start
it’s usually a CUDA/driver mismatch on the serving machine—check your NVIDIA driver/CUDA runtime and use a vLLM version compatible with your environment.
:::

## Verify Installation

```bash
uv run python -c "from patienthub.clients import CLIENT_REGISTRY; print(list(CLIENT_REGISTRY.keys()))"
```

You should see a list of available client agents:

```
['patientPsi', 'roleplayDoh', 'eeyore', 'psyche', 'simPatient', 'consistentMI', ...]
```

## Optional: Web Demo Dependencies

To run the Chainlit web demo:

```bash
# Chainlit is already included in dependencies
chainlit run app.py
```

## Troubleshooting

### Common Issues

**API Key not found:**
Make sure your `.env` file is in the project root and contains valid credentials.

**Module not found:**
Ensure you've activated the virtual environment:

```bash
source .venv/bin/activate
```
