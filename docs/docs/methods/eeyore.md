---
sidebar_position: 3
---

# Eeyore 

> Eeyore: Realistic Depression Simulation via Expert-in-the-Loop Supervised and Preference Optimization

**Venue**: ACL 2025 (Findings)  
**Paper**: [ACL Anthology](https://aclanthology.org/2025.findings-acl.707/)

## Overview

Eeyore introduce a Structured Alignment Framework that incorporates human experts. The framework contains three stages: data curation, instruction tuning, and preference optimization. It aims to create realistic simulations of individuals experiencing depression. 

## Key Features

- **Data Curation**: Mined real-world depression-related conversations from public sources 
> (e.g., depression subreddits, counseling transcripts)
- **Psychological Profile Construction**: A detailed structured profile containing different dimensions (DSM-V standards and Beck's cognitive theory)
- **Instruction Tuning & DPO**: To align the model closer to clinical expert expectations

## Usage

### CLI

```bash
uv run python -m examples.simulate client=eeyore therapist=user
```

### Python

```python
from omegaconf import OmegaConf
from patienthub.clients import get_client

config = OmegaConf.create({
    'agent_type': 'eeyore',
    'model_type': 'LOCAL',
    'model_name': 'hosted_vllm//data3/public_checkpoints/huggingface_models/Eeyore_llama3.1_8B',
    'temperature': 0.7,
    'max_tokens': 1024,
    'max_retries': 3,
    'data_path': 'data/characters/Eeyore.json',
    'data_idx': 0,
})

client = get_client(configs=config, lang='en')
client.set_therapist({'name': 'Clinician'})

response = client.generate_response("How have you been sleeping lately?")
print(response)
```
> ⚠️ **Hint:**  
> - Start a local OpenAI-compatible model server (e.g., vLLM) to serve the weights.  
> - Set `LOCAL_BASE_URL`; PatientHub passes them as `api_base/api_key` to LiteLLM.  
> - Use `model_type=LOCAL` and set `model_name` to your served model id/name.  
> - Run: `uv run python -m examples.simulate client=eeyore therapist=user`  

## Configuration

| Option      | Description            | Default                       |
| ----------- | ---------------------- | ----------------------------- |
| `data_path` | Path to character file | `data/characters/Eeyore.json` |
| `data_idx`  | Character index        | `0`                           |

## Character Data Format

```json
{
  "conversation": [
      {
          "role": "system",
          "content": ""
      },
      {
          "role": "user",
          "content": "hello, how are you feeling today?\n"
      },
      {
          "role": "assistant",
          "content": "I am feeling really sad and lonely right now. My boyfriend and I broke up and it was me who wanted it but now I regret breaking up and he doesn't want me back."
      }
  ],
  "source": "ESC",
  "id_source": "1132",
  "profile": {
      "name": "Cannot be identified",
      "gender": "Female",
      "age": "Cannot be identified",
      "marital status": "Single",
      "occupation": "Cannot be identified",
      "situation of the client": "The client is feeling sad and lonely after breaking up with her boyfriend, whom she wants back after realizing her mistake. She feels pressured by potential competition and has been negatively affected by the breakup.",
      "resistance toward the support": "Low",
      "symptom severity": {
          "feelings of sadness, tearfulness, emptiness, or hopelessness": "Moderate",
          "angry outbursts, irritability, or frustration, even over small matters": "Mild",
          "loss of interest or pleasure in most or all normal activities, such as sex, hobbies, or sports": "Moderate",
          "sleep disturbances, including insomnia or sleeping too much": "Not exhibited",
          "tiredness and lack of energy, so even small tasks take extra effort": "Not exhibited",
          "changes in appetite and weight (reduced appetite and weight loss or increased cravings for food and weight gain)": "Not exhibited",
          "anxiety, agitation, or restlessness": "Mild",
          "slowed thinking, speaking, or body movements": "Not exhibited",
          "feelings of worthlessness or guilt, fixating on past failures or self-blame": "Moderate",
          "trouble thinking, concentrating, making decisions, and remembering things": "Mild",
          "frequent or recurrent thoughts of death, suicidal thoughts, suicide attempts, or suicide": "Not exhibited",
          "unexplained physical problems, such as back pain or headaches": "Not exhibited",
          "becoming withdrawn, negative, or detached": "Not exhibited",
          "increased engagement in high-risk activities": "Not exhibited",
          "greater impulsivity": "Mild",
          "increased use of alcohol or drugs": "Not exhibited",
          "isolating from family and friends": "Mild",
          "inability to meet the responsibilities of work and family or ignoring other important roles": "Not exhibited"
      },
      "cognition distortion exhibition": {
          "selective abstraction": "Not exhibited",
          "overgeneralizing": "Not exhibited",
          "personalization": "Exhibited",
          "catastrophic thinking": "Not exhibited",
          "minimisation": "Not exhibited",
          "arbitrary inference": "Exhibited"
      },
      "depression severity": "Mild Depression - The client shows feelings of sadness and regret following a breakup but lacks symptoms of severe depression.",
      "suicidal ideation severity": "No suicidal ideation",
      "homicidal ideation severity": "No homicidal ideation",
      "counseling history": "N/A"
  },
  "cognitive profile": {
      "life_history": "The client is a young woman who broke up with her boyfriend, which she now regrets. The relationship brought her social status in her small town because he was popular. During their relationship, her boyfriend behaved in dismissive ways, such as leaving her alone at parties, which left her feeling unimportant. Her parents and friends disapproved of the relationship, mainly because they felt she was settling for less. She briefly liked someone else, leading to the breakup, but she now wants to repair her relationship with her ex-boyfriend, partly due to jealousy seeing other girls interested in him on social media.",
      "core_beliefs": "Unlovable belief",
      "core_belief_description": "I am bound to be rejected, I am bound to be abandoned",
      "intermediate_beliefs": "If I'm with the popular guy, then I'm important and desirable. It's necessary to be liked and approved by others (popularity) to be happy.",
      "intermediate_beliefs_during_depression": "If I'm not with the popular guy, then I'm worthless. I'm unlovable and undesired if I'm not achieving and maintaining high social status.",
      "coping_strategies": "Monitoring her ex-boyfriend's social media activity, attempting to reconcile with him and win back his affections",
      "cognitive_models": [
          {
              "situation": "Breaking up with her boyfriend and wanting him back despite his ill-treatment",
              "automatic_thoughts": "I made a mistake by breaking up, I need to get him back to feel important and loved",
              "emotion": "sad/down/lonely/unhappy",
              "behavior": "Decides to beg for her relationship back, keeps checking his social media"
          },
          {
              "situation": "Thinking about how her ex-boyfriend was popular in their town",
              "automatic_thoughts": "I was desirable when I was with him, I've lost my status without him",
              "emotion": "disappointed",
              "behavior": "Feels regret and plans to repair the relationship despite the lack of proper affection from the boyfriend"
          },
          {
              "situation": "Seeing other girls interested in her ex-boyfriend on social media after they broke up",
              "automatic_thoughts": "Others might get him before I can, I need to hurry and get him back",
              "emotion": "jealous/envious",
              "behavior": "Feels pressured to act quickly to prevent him from moving on"
          }
      ]
  }
}
```

## Example Conversation

**Clinician**: "Hi Sam, thank you for coming in. How have you been feeling lately?"

**Patient (Eeyore)**: "_sighs_ I don't know... just tired, I guess. Everything feels like such an effort. Even getting out of bed this morning took everything I had."

**Clinician**: "It sounds like you're experiencing a lot of fatigue. How long has this been going on?"

**Patient**: "Months now. I used to love going to yoga, seeing friends... now I can't remember the last time I did either. What's the point, really?"

**Clinician**: "You mentioned you used to enjoy yoga and seeing friends. What changed?"

**Patient**: "I lost my job back in March. I keep telling myself I'll start applying for new ones, but every time I sit down to work on my resume, I just... can't. I stare at the screen and think, 'Why would anyone hire me anyway?'"

## Resources

`data/characters/Eeyore.json`: Collected a large amount of real-world depression-related conversations from public sources such as Reddit (r/depression), YouTube (the HOPE dataset), ESC, and AnnoMI.