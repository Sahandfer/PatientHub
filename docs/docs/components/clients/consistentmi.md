---
sidebar_position: 2
---

# ConsistentMI

> Consistent Client Simulation for Motivational Interviewing-based Counseling

**Venue**: ACL 2025 (Main Conference)  
**Paper**: [ACL Anthology](https://aclanthology.org/2025.acl-long.1021/)

## Overview

ConsistentMI simulates clients in motivational interviewing (MI) sessions with consistent behavior based on the Transtheoretical Model (Stages of Change). The client's responses adapt based on their current stage and the therapist's MI techniques.

## Key Features

- **Stage of Change Model**: Precontemplation → Contemplation → Preparation → Action → Maintenance
- **Consistent Behavior**: Actions match the current stage
- **Stage Transitions**: Natural progression based on therapist's approach
- **MI-Specific Responses**: Reacts appropriately to OARS techniques

## How It Works

1. **Load Profile**: Reads the character JSON (personas, beliefs, acceptable plans, motivation topics) and initializes `stage` and `receptivity`.
2. **Initialize Prompts**: Builds a system prompt that anchors the client’s behavior/goal and injects personas + beliefs for consistency.
3. **Track Topic Engagement**: Matches the therapist’s latest utterance to a motivation topic using a reranker-backed topic matcher, then uses the topic graph distance to update `engagement` and count repeated off-topic turns. If reranking is unavailable or returns no valid scores, ConsistentMI falls back to lexical matching.
4. **Verify Motivation (Optional)**: If the therapist addresses the client’s core motivation, the client enters a short `Motivation` state for an acknowledging response.
5. **Sample a Stage-Consistent Action**: An LLM predicts an action distribution conditioned on recent context and the current stage.
6. **Select Grounding Detail**: For actions like `Inform/Downplay/Blame/Hesitate/Plan`, the client selects a relevant persona/belief/plan (only when the therapist asks a question) to ground the next reply.
7. **Generate Reply**: Renders a structured instruction (state + action + engagement + selected info) and calls the chat model to produce the final client utterance.

**Action space in the current implementation:**

- `Precontemplation`: `Deny`, `Downplay`, `Blame`, `Inform`, `Engage` (or `Terminate` after repeated off-topic turns)
- `Contemplation`: `Inform`, `Engage`, `Hesitate`, `Doubt`, `Acknowledge`
- `Preparation`: `Inform`, `Engage`, `Reject`, `Accept`, `Plan`
- `Motivation`: `Acknowledge` (then proceeds into `Contemplation`)

## Usage

### CLI

```bash
patienthub simulate client=consistentMI
```

### Python

```python
from patienthub.clients import get_client

client = get_client(agent_name="consistentMI", lang='en')

response = client.generate_response(
    "I noticed you mentioned you've been drinking more lately. How do you feel about that?"
)
print(response)
```

> ⚠️ **Hint:**
>
> - ConsistentMI use a local reranker served through vLLM's OpenAI-compatible `/rerank` endpoint.
> - Set `LOCAL_BASE_URL` and `LOCAL_API_KEY` in `.env`; PatientHub reuses them for the reranker.
> - Use `reranker_model_type=LOCAL`.
> - Set `reranker_model_name` to the LiteLLM vLLM route, e.g. `hosted_vllm/BAAI/bge-reranker-v2-m3`.
> - If the reranker server runs on the same machine, prefer `127.0.0.1` over `0.0.0.0` in `LOCAL_BASE_URL`.

## Configuration

| Option                | Description                                             | Default                                        |
| --------------------- | ------------------------------------------------------- | ---------------------------------------------- |
| `prompt_path`         | Path to prompt file                                     | `data/prompts/client/consistentMI.yaml`        |
| `data_path`           | Path to character file                                  | `data/characters/ConsistentMI.json`            |
| `data_idx`            | Character index                                         | `0`                                            |
| `topics_path`         | Topics from Wiki                                        | `data/resources/ConsistentMI/topics.json`      |
| `topic_graph_path`    | Correlation between topics                              | `data/resources/ConsistentMI/topic_graph.json` |
| `reranker_model_type` | Provider key for topic reranking                        | `LOCAL`                                        |
| `reranker_model_name` | LiteLLM model route for the reranker                    | `hosted_vllm/BAAI/bge-reranker-v2-m3`          |

### Local Reranker Example

```yaml
client:
  agent_name: consistentMI
  model_type: OPENAI
  model_name: gpt-4o
  reranker_model_type: LOCAL
  reranker_model_name: hosted_vllm/BAAI/bge-reranker-v2-m3
```

With a local vLLM reranker server, your `.env` should contain:

```bash
LOCAL_BASE_URL=http://127.0.0.1:7891/v1
LOCAL_API_KEY=EMPTY
```

## Character Data Format

```json
{
  "idx": 25,
  "topic": "reducing drug use",
  "initial_stage": "Precontemplation",
  "suggestibilities": [3, 3, 3, 2, 3],
  "Personas": [
    "You smoke weed to relax after a long day.",
    "Your wife is concerned about your smoking habits",
    "Your wife has pushed you to seek help.",
    "You have failed a UA at work.",
    "Your boss may fire you for failing the UA."
  ],
  "Acceptable Plans": [
    "You consider talking to his boss and taking steps to address his substance use to prevent losing his job."
  ],
  "Beliefs": [
    "You believe weed helps you unwind.",
    "You don't perceive smoking weed as a problem.",
    "You view smoking weed as a way to manage stress from working, paying the bills and house."
  ],
  "quality": "high",
  "Motivation": [
    "Career Break",
    "Employment",
    "Economy",
    "You are motivated because of the risk of smoking weed in career break for yourself, as you may lose your job."
  ],
  "Behavior": "drug use"
}
```

## Stages of Change

| Stage            | Description            | Typical Behaviors                     |
| ---------------- | ---------------------- | ------------------------------------- |
| Precontemplation | Not considering change | Denial, resistance, minimization      |
| Contemplation    | Aware but ambivalent   | Weighing pros/cons, uncertainty       |
| Preparation      | Planning to change     | Seeking information, small steps      |
| Action           | Actively changing      | Implementing changes, seeking support |
| Maintenance      | Sustaining change      | Preventing relapse, building habits   |

## Example Conversation

**Therapist**: "Thanks for coming in today. What brings you here?"

**Client (Precontemplation)**: "My boss made me come. Apparently someone complained about smelling alcohol on my breath at work. I think they're overreacting—I just had a couple drinks at lunch."

**Therapist**: "It sounds frustrating to feel like others are making a big deal out of something. What's your take on your drinking?"

**Client**: "I mean, I drink, sure. But I'm not an alcoholic or anything. I can stop whenever I want. I just don't want to right now. Work's been stressful."

**Therapist** (using reflection): "Work stress has been a factor, and you feel in control of your drinking."

**Client** (slight shift): "Well... I guess sometimes I drink more than I plan to. But who doesn't, right?"

## Best Practices

1. **Use MI Therapist**: Pair with `therapist=MI` for best results
2. **Watch for Change Talk**: Client will express change talk when therapist uses good MI
3. **Avoid Confrontation**: Confrontational approaches trigger resistance
4. **Track Stage**: Note when client shows signs of stage transition

## Limitations

- Stage transitions may not perfectly match clinical expectations
