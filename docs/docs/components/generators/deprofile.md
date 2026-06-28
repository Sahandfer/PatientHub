# Deprofile Generator

> Decomposing Clinical Profiles for Mental Health Patient Simulation

Builds a Deprofile patient character by joining a clinical profile, two dialogue
records, and social-media timeline evidence. The generator expects the data to have already been standardized
into the JSON resources described below, then it selects a social candidate,
constructs timeline memory, and saves a role-playable character file.

## Overview

| Property   | Value                                  |
| ---------- | -------------------------------------- |
| **Key**    | `deprofile`                            |
| **Type**   | Matching Counseling/Asessment Dialogue & Social-media Timeline |
| **Output** | Deprofile character profile            |

## What This Generator Does

- **Clinical/social assembly**: Loads one clinical profile, assessment dialogue,
  counseling dialogue, symptom timeline, and life-event timeline.
- **Candidate selection**: Uses the profile's indexed `candidate_id` list when
  available. If no indexed candidate is provided, it rematches against
  `social_user_profiles.json`.
- **Schema validation**: Validates clinical profiles, dialogue roles, social
  profile demographics, supported symptom labels, and timeline structure with
  `patienthub.schemas.deprofile`.
- **Timeline memory construction**: Converts raw symptom and life-event timelines
  into graph nodes, temporal edges, episodes, and compact `card_text` memory
  cards.
- **Append/update output**: Writes the assembled character to `output_path`,
  replacing any previous record with the same `profile_id`.

## What This Generator Does Not Do

The current PatientHub implementation does not infer Big Five traits, symptom
labels, demographic fields, or timelines from raw social-media data. If you only
have original posts, you must first preprocess them into:

- a social profile entry in `social_user_profiles.json` when rematching is needed;
- a symptom timeline entry in `symptom_timelines.json`;
- a life-event timeline entry in `life_event_timelines.json`.

There is also no separate `0_en_ch_symp_pair.json` input. The supported
social-symptom to clinical-symptom mapping is defined in
`patienthub/schemas/deprofile.py` as `SOCIAL_SYMPTOM_TO_CLINICAL`.

### Not Yet Implemented: Raw Social Data Preprocessing

PatientHub does not yet implement the preprocessing pipeline from the most raw
social-media data to Deprofile's three standardized social resources:

```text
raw social-media data
  -> social_user_profiles.json
  -> symptom_timelines.json
  -> life_event_timelines.json
```

That means the generator currently assumes these three resources already exist
when they are needed. In particular, users must prepare demographic fields, Big
Five scores, supported symptom labels, symptom timeline items, and life-event
timeline items before calling `generate_character()`.

## How It Works

`generate_character()` runs this sequence:

1. `load_clinical_profile()` reads `deprofiles_complete_index.json` by
   `profile_id`.
2. `load_dialogues()` reads `assessment_dialogues.json` and
   `counseling_dialogues.json` by the same `profile_id`.
3. `select_candidate()` chooses the social user:
   - if `clinical_profile.candidate_id` is non-empty,
     `select_index_candidate()` selects `candidate_id[candidate_rank]`;
   - otherwise `select_rematched_candidate()` loads `social_user_profiles.json` and
     searches for a compatible social profile.
4. `load_timelines()` loads `symptom_timelines.json` and
   `life_event_timelines.json` by the selected social user ID.
5. `build_timeline_memory()` calls `process_timeline()` for symptom and
   life-event timelines. It builds normalized time, graph nodes, edges,
   episodes, and memory cards.
6. `upsert_output()` saves a `DeprofileCharacter` record to `output_path`.

The client role-play prompt uses the final character file. For life events, the
Deprofile client prefers `timeline_memory.life_event.cards[*].card_text` and
falls back to raw `life_event_timeline.timeline` only when memory cards are not
available.

## Usage

```python
from omegaconf import OmegaConf
from patienthub.generators import get_generator

config = OmegaConf.create({
    "agent_name": "deprofile",
    "profile_id": "0069",
    "candidate_rank": 0,
    "resource_dir": "data/resources/Deprofile",
    "social_profiles_path": "data/resources/Deprofile/social_user_profiles.json",
    "prompt_path": "data/prompts/generator/deprofile.yaml",
    "output_path": "data/characters/Deprofile.json",
    "symptom_similarity_threshold": 0.5,
    "personality_similarity_threshold": 0.8,
    "coc_horizon_days": 90,
    "coc_max_items": 80,
    "coc_episode_window_days": 7,
})

generator = get_generator(agent_name="deprofile", configs=config, lang="zh")
character = generator.generate_character()
```

`lang` is set by `get_generator(..., lang="zh" | "en")`. It controls the
language-specific prompt templates used for timeline memory card rendering.

## Configuration

| Parameter | Type | Default | Description |
| --------- | ---- | ------- | ----------- |
| `profile_id` | string | `0069` | Clinical profile key to load from `deprofiles_complete_index.json` |
| `candidate_rank` | int | `0` | Which indexed or rematched candidate to use |
| `resource_dir` | string | `data/resources/Deprofile` | Directory containing the fixed Deprofile resource files |
| `social_profiles_path` | string | `data/resources/Deprofile/social_user_profiles.json` | Social profile catalog used only when rematching is needed |
| `prompt_path` | string | `data/prompts/generator/deprofile.yaml` | Prompt templates for timeline extraction and memory cards |
| `output_path` | string | `data/characters/Deprofile.json` | JSON array file where generated characters are saved |
| `symptom_similarity_threshold` | float | `0.5` | Minimum symptom overlap for rematched candidates |
| `personality_similarity_threshold` | float | `0.8` | Minimum Big Five cosine similarity for rematched candidates |
| `coc_horizon_days` | int | `90` | Relative-day horizon used when building timeline memory |
| `coc_max_items` | int | `80` | Maximum timeline items processed per timeline type |
| `coc_episode_window_days` | int | `7` | Bucket size for grouping timeline nodes into episodes |

## Required Resource Files

With the default `resource_dir`, Deprofile reads these fixed file names:

| File | Keyed By | Required When | Purpose |
| ---- | -------- | ------------- | ------- |
| `deprofiles_complete_index.json` | `profile_id` | Always | Clinical profile, risks, symptoms, Big Five, and optional indexed candidates |
| `assessment_dialogues.json` | `profile_id` | Always | Doctor-user assessment dialogue snippets |
| `counseling_dialogues.json` | `profile_id` | Always | Consultant-patient counseling dialogue snippets |
| `symptom_timelines.json` | `social_user_id` | Always for selected social user | Social posts labeled as symptom evidence |
| `life_event_timelines.json` | `social_user_id` | Always for selected social user | Social posts labeled as life-event evidence |
| `social_user_profiles.json` | `social_user_id` | Only for rematch mode | Demographics, Big Five, and social symptom labels used to find candidates |

The resource files are catalogs: each top-level key identifies either a clinical
profile or a social user. The selected `profile_id` must exist in the three
clinical/dialogue catalogs. The selected social user ID must exist in both
timeline catalogs.

## Which Files Do I Need To Add?

Use this table before editing data:

| Situation | Add / Update These Files | Notes |
| --------- | ------------------------ | ----- |
| Use an existing curated Deprofile profile | No new files | Set `profile_id` and `candidate_rank`; the existing `candidate_id` chooses a social user |
| Add a new clinical profile and already know the social user | `deprofiles_complete_index.json`, `assessment_dialogues.json`, `counseling_dialogues.json`, `symptom_timelines.json`, `life_event_timelines.json` | Put the social user in `candidate_id`; `social_user_profiles.json` is not required for index mode |
| Add a new clinical profile but do not know which social user to use | Same as above, plus `social_user_profiles.json` entries for candidate social users | Leave `candidate_id` empty; the generator will rematch using demographics, symptoms, and Big Five |
| Add a new social-media candidate for future matching | `social_user_profiles.json`, `symptom_timelines.json`, `life_event_timelines.json` | This does not create a patient by itself; a clinical `profile_id` is still needed |
| Start from raw social-media posts only | Preprocess outside this generator first | Convert raw posts into Big Five, supported symptom labels, demographic fields, and the two timeline files |
| Add only assessment/counseling dialogue | Not enough | A complete Deprofile character also needs a clinical profile and both timelines |

## Candidate Selection Modes

### Indexed Candidate Mode

If `candidate_id` in the clinical profile is non-empty, the generator uses it
directly:

```json
{
  "candidate_id": [
    {
      "basic_id": "social_user_001",
      "similarity": 0.91,
      "symp_similarity": 1.0
    }
  ]
}
```

`candidate_rank: 0` selects `social_user_001`. In this mode the generator does
not need `social_user_profiles.json`, but it still needs:

- `symptom_timelines.json["social_user_001"]`
- `life_event_timelines.json["social_user_001"]`

Use this mode when you have already decided which social timeline belongs with
the clinical profile.

The bundled PatientHub Deprofile resources are intentionally reduced to the 27
curated profiles and their rank-0 social timelines. With these bundled
resources, keep `candidate_rank` at `0`. To use other indexed candidates, provide
matching entries in both timeline catalogs.

### Rematch Mode

If `candidate_id` is empty, the generator loads `social_profiles_path` and
searches for matching social users. A candidate must:

1. have both symptom and life-event timelines;
2. match demographics, unless either side is `Unknown`;
3. have social symptom labels that map to clinical positive symptoms;
4. not map to any clinical negative symptom;
5. pass `symptom_similarity_threshold`;
6. pass `personality_similarity_threshold` using Big Five cosine similarity.

Candidates are sorted by `personality_similarity + symptom_similarity`, then by
user ID. `candidate_rank` selects one candidate from that sorted list. If the
rank is outside the available matches, generation fails instead of silently
choosing another candidate.

Use this mode when you have a clinical profile but want PatientHub to choose a
compatible social timeline from a prepared candidate pool.

## Data Formats

### `deprofiles_complete_index.json`

Top-level object keyed by `profile_id`:

```json
{
  "NEW_PROFILE_001": {
    "cr_id": "cr-001",
    "d4_id": "d4-001",
    "age": 29,
    "gender": "F",
    "marital_status": "single",
    "work_status": "employed",
    "big_five": {
      "Openness": 6,
      "Conscientiousness": 4,
      "Extraversion": 2,
      "Agreeableness": 5,
      "Neuroticism": 7
    },
    "positive_symptoms": [
      "任务-情绪-情绪低落",
      "任务-睡眠-存在睡眠问题"
    ],
    "negative_symptoms": [
      "任务-自杀-存在自杀倾向"
    ],
    "summation": "Brief clinical summary.",
    "depression_risk": 2,
    "suicide_risk": 0,
    "candidate_id": [
      {
        "basic_id": "social_user_001",
        "similarity": 0.91,
        "symp_similarity": 1.0
      }
    ]
  }
}
```

Important constraints:

- `gender`: `F`, `M`, or `Unknown`
- `marital_status`: `single`, `married`, `divorced`, `widowed`, or `Unknown`
- `work_status`: `student`, `employed`, `unemployed`, `retired`, or `Unknown`
- `depression_risk` and `suicide_risk`: integers from `0` to `3`
- `candidate_id`: use an empty list for rematch mode
- `suicide_risk` is preferred; the schema also accepts the historical typo
  `suiside_risk`

Clinical `positive_symptoms` and `negative_symptoms` use clinical Chinese task
labels. Rematch only compares against the 17 clinical labels reachable from
`SOCIAL_SYMPTOM_TO_CLINICAL`; other clinical labels may remain in the profile
but will not help social rematching.

### `assessment_dialogues.json`

Top-level object keyed by the same `profile_id`:

```json
{
  "NEW_PROFILE_001": [
    {"role": "doctor", "content": "最近睡眠怎么样？"},
    {"role": "user", "content": "睡得很浅，经常醒。"}
  ]
}
```

Allowed roles are only `doctor` and `user`.

### `counseling_dialogues.json`

Top-level object keyed by the same `profile_id`:

```json
{
  "NEW_PROFILE_001": [
    {"role": "consultant", "content": "这样确实很难受。"},
    {"role": "patient", "content": "嗯，我最近压力很大。"}
  ]
}
```

Allowed roles are only `consultant` and `patient`.

### `social_user_profiles.json`

This file is required only for rematch mode. It is a top-level object keyed by
social user ID:

```json
{
  "social_user_001": {
    "gender": "F",
    "age": "26-35",
    "marital_status": "single",
    "work_status": "employed",
    "big_five": {
      "Openness": 6,
      "Conscientiousness": 4,
      "Extraversion": 2,
      "Agreeableness": 5,
      "Neuroticism": 7
    },
    "symptoms": [
      "Depressed_Mood",
      "sleep_disturbance"
    ],
    "life_events": true,
    "prompt_count": 38
  }
}
```

Important constraints:

- `age`: `0-17`, `18-25`, `26-35`, `36-50`, `50+`, or `Unknown`
- demographics may be `Unknown`; `Unknown` is treated as compatible
- `symptoms` must use supported social symptom labels
- `life_events` and `prompt_count` are optional metadata

Supported social symptom labels are:

| Social Label | Clinical Label |
| ------------ | -------------- |
| `Catatonic_behavior` | `任务-躯体症状-运动性迟滞` |
| `Decreased_energy_tiredness_fatigue` | `任务-精神状态-疲倦` |
| `Depressed_Mood` | `任务-情绪-情绪低落` |
| `Hyperactivity_agitation` | `任务-躯体症状-运动性激越` |
| `Inattention` | `任务-精神状态-注意力不集中` |
| `Indecisiveness` | `任务-精神状态-选择困难` |
| `Suicidal_ideas` | `任务-自杀-存在自杀倾向` |
| `Worthlessness_and_guilty` | `任务-自杀-自我价值感低` |
| `diminished_emotional_expression` | `任务-兴趣-情感淡漠` |
| `drastical_shift_in_mood_and_energy` | `任务-筛查-躁狂` |
| `fear_about_social_situations` | `任务-社会功能-避免与人接触` |
| `fear_of_gaining_weight` | `任务-食欲-显著体重变化` |
| `loss_of_interest_or_motivation` | `任务-兴趣-兴趣丧失` |
| `pessimism` | `任务-自杀-有无望感` |
| `poor_memory` | `任务-精神状态-记忆力下降` |
| `sleep_disturbance` | `任务-睡眠-存在睡眠问题` |
| `weight_and_appetite_change` | `任务-食欲-食欲存在问题` |

### `symptom_timelines.json`

Top-level object keyed by social user ID:

```json
{
  "social_user_001": {
    "user_id": "social_user_001",
    "symptoms": ["Depressed_Mood", "sleep_disturbance"],
    "timeline": [
      {
        "timestamp": 10,
        "symptom": "Depressed_Mood",
        "tweet": "I have felt down all week."
      },
      {
        "timestamp": 13,
        "symptom": "sleep_disturbance",
        "tweet": "I kept waking up last night."
      }
    ]
  }
}
```

`timestamp` is a relative day index, not a Unix timestamp. Larger values are
treated as more recent. During timeline memory construction, the largest
timestamp becomes the anchor day, and `days_ago = anchor_day - timestamp`.

Use the same symptom label vocabulary as `social_user_profiles.json` whenever possible.
The current timeline item schema accepts a string, but matching quality depends
on the standardized labels in the social profile.

### `life_event_timelines.json`

Top-level object keyed by social user ID:

```json
{
  "social_user_001": {
    "user_id": "social_user_001",
    "timeline": [
      {
        "timestamp": 9,
        "life_event": "Work",
        "tweet": "The project review has been stressful."
      },
      {
        "timestamp": 13,
        "life_event": "Family",
        "tweet": "I argued with my family again."
      }
    ]
  }
}
```

Life-event labels are not currently restricted by schema. Keep them short and
consistent, for example `Work`, `Family`, `Education`, `Social`,
`Relationships_Changes`, or another project-specific category. The raw `tweet`
is used as evidence for timeline memory construction.

## How Processed Must New Data Be?

Before adding a new social user to Deprofile, make sure the raw social-media
data has been processed to this level:

1. **Demographics**: gender, age band, marital status, and work status are
   normalized to the allowed values or `Unknown`.
2. **Big Five**: five numeric scores are available for Openness,
   Conscientiousness, Extraversion, Agreeableness, and Neuroticism.
3. **Symptom labels**: each social symptom is one of the supported labels above.
4. **Symptom timeline**: symptom-related posts are converted into
   `{timestamp, symptom, tweet}` items under the same `user_id`.
5. **Life-event timeline**: life-event posts are converted into
   `{timestamp, life_event, tweet}` items under the same `user_id`.
6. **Clinical side**: the clinical profile has risks, clinical symptom labels,
   Big Five, and both dialogue files.

After that, the generator can run. It will do the candidate matching and the
paper-style timeline memory processing inside PatientHub.

The upstream preprocessing step from raw social-media posts into
`social_user_profiles.json`, `symptom_timelines.json`, and
`life_event_timelines.json` is intentionally outside the current generator
implementation and still needs to be added in future work.

## Output Format

The output file is a JSON array of `DeprofileCharacter` records:

```json
[
  {
    "profile_id": "NEW_PROFILE_001",
    "clinical_profile": {},
    "assessment_dialogue": [],
    "counseling_dialogue": [],
    "social_user_id": "social_user_001",
    "symptom_timeline": {},
    "life_event_timeline": {},
    "timeline_memory": {
      "symptom": {
        "graph": {},
        "episodes": [],
        "cards": []
      },
      "life_event": {
        "graph": {},
        "episodes": [],
        "cards": [
          {
            "episode_id": "E_0",
            "time_range": {
              "days_ago_start": 6,
              "days_ago_end": 0
            },
            "salient_node_ids": ["EV_13_0"],
            "card_text": "今天：Family。代表时间点：今天（0天前）。"
          }
        ]
      }
    },
    "match_metadata": {
      "mode": "index",
      "selected_social_user_id": "social_user_001",
      "candidate_rank": 0,
      "personality_similarity": 0.91,
      "symptom_similarity": 1.0,
      "combined_score": 1.91,
      "personality_threshold": 0.8,
      "symptom_threshold": 0.5
    },
    "provenance": {
      "generator_version": "1",
      "language": "zh",
      "source_paths": {},
      "completeness": {
        "assessment": true,
        "counseling": true,
        "symptom_timeline": true,
        "life_event_timeline": true
      }
    }
  }
]
```

The role-play client does not need to re-open the source JSON resources. It
loads the generated character file. `symptom_timeline` and
`life_event_timeline` preserve the exact selected timeline contents, while
`timeline_memory` stores processed graph, episode, and memory-card views of
those timelines.

## Common Failure Cases

- `profile_id` exists in the clinical profile file but not in one of the
  dialogue files.
- `candidate_rank` is larger than the available `candidate_id` list or rematch
  result list.
- The selected social user does not exist in both timeline files.
- `social_user_profiles.json` is missing when `candidate_id` is empty.
- A social profile uses unsupported symptom labels.
- `user_id` inside a timeline object does not match the top-level social user
  key.

## Quick Checklist For Adding A Complete New Profile

1. Choose a stable `profile_id`, for example `NEW_PROFILE_001`.
2. Add `deprofiles_complete_index.json[profile_id]`.
3. Add `assessment_dialogues.json[profile_id]`.
4. Add `counseling_dialogues.json[profile_id]`.
5. Choose or create a `social_user_id`.
6. Add `symptom_timelines.json[social_user_id]`.
7. Add `life_event_timelines.json[social_user_id]`.
8. If using index mode, put `social_user_id` in `candidate_id`.
9. If using rematch mode, leave `candidate_id` empty and add
   `social_user_profiles.json[social_user_id]`.
10. Run `generate_character()` and inspect the saved character JSON.
