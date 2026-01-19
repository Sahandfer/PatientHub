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
git clone https://github.com/Sahandfer/Patient-Simulation.git
cd Patient-Simulation

# Install dependencies
uv sync

# Activate the environment
source .venv/bin/activate
```

## Install with pip

```bash
# Clone the repository
git clone https://github.com/Sahandfer/Patient-Simulation.git
cd Patient-Simulation

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install
pip install -e .
```

## Configuration

Create a `.env` file in the project root:

```bash
LAB_API_KEY=<your API key>
LAB_BASE_URL=http://115.182.62.174:18888/v1
```

:::tip Using Other Providers
PatientHub supports OpenAI, HuggingFace, and local models. See [Configuration](/docs/getting-started/configuration) for details.
:::

## Verify Installation

```bash
uv run python -c "from patienthub.clients import CLIENT_REGISTRY; print(list(CLIENT_REGISTRY.keys()))"
```

You should see a list of available client agents:

```
['basic', 'patientPsi', 'roleplayDoh', 'eeyore', 'psyche', 'simPatient', 'consistentMI', ...]
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

**CUDA/GPU issues:**
For local models, ensure PyTorch is installed with CUDA support:

```bash
pip install torch --index-url https://download.pytorch.org/whl/cu118
```
