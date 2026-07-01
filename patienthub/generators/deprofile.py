import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from omegaconf import DictConfig
from pydantic import ValidationError

from .base import BaseGenerator
from patienthub.configs import APIModelConfig
from patienthub.schemas import deprofile as ds
from patienthub.utils import load_json, save_json


@dataclass
class DeprofileGeneratorConfig(APIModelConfig):
    """Configuration for the Deprofile character generator."""

    agent_name: str = "deprofile"
    prompt_path: str = "data/prompts/generator/deprofile.yaml"
    output_path: str = "data/characters/deprofile.json"
    resource_dir: str = "data/resources/Deprofile"
    social_profiles_path: str = "data/resources/Deprofile/social_user_profiles.json"
    profile_id: str = "0069"
    candidate_rank: int = 0
    symptom_similarity_threshold: float = 0.5
    personality_similarity_threshold: float = 0.8
    coc_horizon_days: int = 90
    coc_max_items: int = 80
    coc_episode_window_days: int = 7
    coc_max_symptoms_per_card: int = 3
    coc_max_events_per_card: int = 2


class DeprofileGenerator(BaseGenerator):
    """Assemble a Deprofile character from standardized evidence."""

    def __init__(self, configs: DictConfig):
        super().__init__(configs)
        self.resource_dir = self.configs.resource_dir
        self._symptom_timelines: dict[str, Any] | None = None
        self._life_event_timelines: dict[str, Any] | None = None

    def load_social_profile_catalog(self) -> dict[str, ds.SocialProfile]:
        path = Path(self.configs.social_profiles_path)
        raw_profiles = load_json(str(path))
        try:
            return ds.SocialProfileCatalog.model_validate(raw_profiles).root
        except ValidationError as exc:
            raise ValueError(
                "Invalid social profile catalog "
                f"({path}); expected social_user_profiles.json to be a "
                "non-empty "
                "object keyed by social user ID with valid SocialProfile values"
            ) from exc

    def load_clinical_profile(self) -> ds.ClinicalProfile:
        profiles = load_json(f"{self.resource_dir}/deprofiles_complete_index.json")
        profile_id = str(self.configs.profile_id)
        return ds.ClinicalProfile.model_validate(profiles[profile_id])

    def load_dialogues(
        self,
    ) -> tuple[list[ds.AssessmentMessage], list[ds.CounselingMessage]]:
        profile_id = str(self.configs.profile_id)
        assessment_records = load_json(f"{self.resource_dir}/assessment_dialogues.json")
        counseling_records = load_json(f"{self.resource_dir}/counseling_dialogues.json")
        assessment = [
            ds.AssessmentMessage.model_validate(item)
            for item in assessment_records[profile_id]
        ]
        counseling = [
            ds.CounselingMessage.model_validate(item)
            for item in counseling_records[profile_id]
        ]
        return assessment, counseling

    def select_index_candidate(
        self, profile: ds.ClinicalProfile
    ) -> tuple[str, ds.MatchMetadata]:
        rank = int(self.configs.candidate_rank)
        candidate = profile.candidate_id[rank]
        return candidate.basic_id, ds.MatchMetadata(
            mode="index",
            selected_social_user_id=candidate.basic_id,
            candidate_rank=rank,
            personality_similarity=candidate.similarity,
            symptom_similarity=candidate.symp_similarity,
            combined_score=candidate.similarity + candidate.symp_similarity,
            personality_threshold=float(self.configs.personality_similarity_threshold),
            symptom_threshold=float(self.configs.symptom_similarity_threshold),
        )

    @staticmethod
    def age_to_band(age: int) -> str:
        if age <= 17:
            return "0-17"
        if age <= 25:
            return "18-25"
        if age <= 35:
            return "26-35"
        if age <= 50:
            return "36-50"
        return "50+"

    @staticmethod
    def compatible(left: str, right: str) -> bool:
        return left == "Unknown" or right == "Unknown" or left == right

    @classmethod
    def demographics_match(
        cls, clinical: ds.ClinicalProfile, social: ds.SocialProfile
    ) -> bool:
        return all(
            (
                cls.compatible(clinical.gender, social.gender),
                cls.compatible(cls.age_to_band(clinical.age), social.age),
                cls.compatible(clinical.marital_status, social.marital_status),
                cls.compatible(clinical.work_status, social.work_status),
            )
        )

    @staticmethod
    def cosine_similarity(left: list[float], right: list[float]) -> float:
        left_norm = math.sqrt(sum(value * value for value in left))
        right_norm = math.sqrt(sum(value * value for value in right))
        if left_norm == 0 or right_norm == 0:
            return 0.0
        similarity = sum(a * b for a, b in zip(left, right)) / (left_norm * right_norm)
        return max(-1.0, min(1.0, similarity))

    @staticmethod
    def big_five_vector(profile: ds.ClinicalProfile | ds.SocialProfile) -> list[float]:
        traits = profile.big_five
        return [
            traits.Openness,
            traits.Conscientiousness,
            traits.Extraversion,
            traits.Agreeableness,
            traits.Neuroticism,
        ]

    def load_timeline_catalogs(
        self,
    ) -> tuple[dict[str, Any], dict[str, Any]]:
        if self._symptom_timelines is None:
            symptom_path = f"{self.resource_dir}/symptom_timelines.json"
            self._symptom_timelines = load_json(symptom_path)
        if self._life_event_timelines is None:
            life_event_path = f"{self.resource_dir}/life_event_timelines.json"
            self._life_event_timelines = load_json(life_event_path)
        return self._symptom_timelines, self._life_event_timelines

    def select_rematched_candidate(
        self, profile: ds.ClinicalProfile
    ) -> tuple[str, ds.MatchMetadata]:
        social_profiles = self.load_social_profile_catalog()
        counts = ds.MatchStageCounts(total=len(social_profiles))
        candidates: list[tuple[float, str, float, float]] = []
        clinical_vector = self.big_five_vector(profile)

        symptom, life_event = self.load_timeline_catalogs()

        for user_id, social in social_profiles.items():
            if not (user_id in symptom and user_id in life_event):
                continue
            counts.timeline_eligible += 1
            if not self.demographics_match(profile, social):
                continue
            counts.demographic_compatible += 1

            mapped = [
                ds.SOCIAL_SYMPTOM_TO_CLINICAL[symptom] for symptom in social.symptoms
            ]
            if not mapped or any(
                symptom in profile.negative_symptoms for symptom in mapped
            ):
                continue
            symptom_similarity = sum(
                symptom in profile.positive_symptoms for symptom in mapped
            ) / len(mapped)
            if symptom_similarity < float(self.configs.symptom_similarity_threshold):
                continue
            counts.symptom_compatible += 1

            personality_similarity = self.cosine_similarity(
                clinical_vector, self.big_five_vector(social)
            )
            # Upstream (7_redo_json.py) keeps candidates with cosine ``> 0.8``;
            # rejecting ``<= threshold`` reproduces that strict comparison.
            if personality_similarity <= float(
                self.configs.personality_similarity_threshold
            ):
                continue
            counts.personality_compatible += 1
            candidates.append(
                (
                    personality_similarity + symptom_similarity,
                    user_id,
                    personality_similarity,
                    symptom_similarity,
                )
            )

        candidates.sort(key=lambda item: (-item[0], item[1]))
        rank = int(self.configs.candidate_rank)
        if rank < 0 or rank >= len(candidates):
            if not candidates:
                raise RuntimeError(
                    f"No social candidate matched profile {self.configs.profile_id}; "
                    f"stage_counts={counts.model_dump()}"
                )
            raise IndexError(
                f"candidate_rank {rank} is invalid for {len(candidates)} matches"
            )
        combined, user_id, personality, symptom = candidates[rank]
        return user_id, ds.MatchMetadata(
            mode="rematch",
            selected_social_user_id=user_id,
            candidate_rank=rank,
            personality_similarity=personality,
            symptom_similarity=symptom,
            combined_score=combined,
            personality_threshold=float(self.configs.personality_similarity_threshold),
            symptom_threshold=float(self.configs.symptom_similarity_threshold),
            stage_counts=counts,
        )

    def load_timelines(
        self, user_id: str
    ) -> tuple[ds.SymptomTimeline, ds.LifeEventTimeline]:
        symptom_records, life_event_records = self.load_timeline_catalogs()
        symptom = ds.SymptomTimeline.model_validate(symptom_records[user_id])
        life_event = ds.LifeEventTimeline.model_validate(life_event_records[user_id])
        if symptom.user_id != user_id or life_event.user_id != user_id:
            raise ValueError(f"Timeline owner does not match social user {user_id}")
        return symptom, life_event

    def time_norm(self, timestamp: int, anchor_timestamp: int) -> dict[str, Any]:
        days_ago = max(0, anchor_timestamp - timestamp)
        # Only the language-neutral ``days_ago`` is persisted; the relative-time
        # phrase is rendered at point-of-use (memory_card template / client) in
        # the appropriate language, so no baked string is stored here.
        return {
            "event_day": timestamp,
            "days_ago": days_ago,
            "absolute_date": None,
            "granularity": "day",
            "confidence": 1.0,
        }

    def episode_time_range(self, bucket: int, window: int) -> dict[str, Any]:
        # Match upstream build_episodes_by_window: the range spans the fixed
        # window boundaries (not the actual node days within the bucket).
        start_days = bucket * window + (window - 1)
        end_days = bucket * window
        return {
            "days_ago_start": start_days,
            "days_ago_end": end_days,
        }

    def render_memory_card(
        self, episode: dict[str, Any], episode_nodes: list[dict[str, Any]]
    ) -> dict[str, Any]:
        if not self.prompts or "memory_card" not in self.prompts:
            raise ValueError("Deprofile memory_card prompt is required.")
        max_symptoms = int(getattr(self.configs, "coc_max_symptoms_per_card", 3))
        max_events = int(getattr(self.configs, "coc_max_events_per_card", 2))
        representative = max(episode_nodes, key=lambda node: node["timestamp_day"])
        # Match upstream render_cards_minimal: keep only the most recent few
        # symptom/event nodes per card, symptom lines first then event lines.
        symptom_nodes = sorted(
            (n for n in episode_nodes if n.get("node_type") == "Symptom"),
            key=lambda node: node["timestamp_day"],
            reverse=True,
        )[:max_symptoms]
        event_nodes = sorted(
            (n for n in episode_nodes if n.get("node_type") == "LifeEvent"),
            key=lambda node: node["timestamp_day"],
            reverse=True,
        )[:max_events]
        card_items: list[dict[str, Any]] = []
        seen: set[Any] = set()
        for node in symptom_nodes:
            text = node.get("triple") or node.get("event_summary_cn")
            if text and text in seen:
                continue
            if text:
                seen.add(text)
            card_items.append(
                {
                    "node_type": "Symptom",
                    "text": text[:60] if text else None,
                    "symptom": node.get("symptom"),
                    "life_event": None,
                }
            )
        for node in event_nodes:
            text = node.get("event_triple") or node.get("event_summary_cn")
            card_items.append(
                {
                    "node_type": "LifeEvent",
                    "text": text[:60] if text else None,
                    "symptom": None,
                    "life_event": node.get("life_event"),
                }
            )
        lang = str(getattr(self.configs, "lang", "zh"))
        card_text = (
            self.prompts["memory_card"]
            .render(
                episode=episode,
                representative=representative,
                card_items=card_items,
                relative=lambda days: ds.days_to_relative(days, lang),
            )
            .strip()
        )
        return {
            "episode_id": episode["episode_id"],
            "time_range": episode["time_range"],
            "salient_node_ids": episode["salient_node_ids"],
            "card_text": card_text,
        }

    def process_timeline(self, kind: str, items: list[Any]) -> dict[str, Any]:
        # Sort ascending by timestamp first (upstream load_timeline does the
        # same) so the temporal_precedes edges below follow real time order
        # regardless of the input ordering.
        items = sorted(items, key=lambda item: item.timestamp)
        latest = max(item.timestamp for item in items)
        earliest = latest - int(getattr(self.configs, "coc_horizon_days", 90))
        # Strictly greater-than, matching upstream cut_items
        # (timestamp > now_day - horizon_days).
        bounded = [item for item in items if item.timestamp > earliest]
        bounded = bounded[-int(getattr(self.configs, "coc_max_items", 80)) :]
        prompt_key = "symptom_extract" if kind == "symptom" else "life_event_extract"
        nodes: list[dict[str, Any]] = []
        index_by_day: dict[str, list[str]] = {}
        index_by_symptom: dict[str, list[str]] = {}

        for item in bounded:
            label = item.symptom if kind == "symptom" else item.life_event
            triple = None
            summary = None
            if self.chat_model is not None and self.prompts:
                prompt = self.prompts[prompt_key].render(label=label, tweet=item.tweet)
                extracted = self.chat_model.generate(
                    [{"role": "user", "content": prompt}],
                    response_format=ds.CoCExtraction,
                )
                if not extracted.is_meaningful or not extracted.event_triple:
                    continue
                triple = extracted.event_triple
                summary = extracted.summary
            # Upstream uses ``SYM_{day}_{symptom}``; the extra ``_{len(nodes)}``
            # suffix keeps ids unique when the same symptom recurs on one day
            # (otherwise the by_symptom index and edges would collide).
            node_id = (
                f"SYM_{item.timestamp}_{label}_{len(nodes)}"
                if kind == "symptom"
                else f"EV_{item.timestamp}_{len(nodes)}"
            )
            node = {
                "id": node_id,
                "node_type": "Symptom" if kind == "symptom" else "LifeEvent",
                "timestamp_day": item.timestamp,
                "time_norm": self.time_norm(item.timestamp, latest),
            }
            if kind == "symptom":
                node.update(
                    {
                        "symptom": label,
                        "triple": triple,
                        "evidence": [item.tweet],
                    }
                )
                index_by_symptom.setdefault(label, []).append(node_id)
            else:
                node.update(
                    {
                        "life_event": label,
                        "is_meaningful": triple is not None,
                        "event_triple": triple,
                        "event_summary_cn": summary,
                        "evidence": [item.tweet],
                    }
                )
            nodes.append(node)
            index_by_day.setdefault(str(item.timestamp), []).append(node_id)

        edges = [
            {
                "source": nodes[index - 1]["id"],
                "target": nodes[index]["id"],
                "relation": "temporal_precedes",
                "confidence": 0.5,
                "rationale": "temporal order",
            }
            for index in range(1, len(nodes))
        ]
        if kind == "symptom":
            node_by_id = {node["id"]: node for node in nodes}
            for label, ids in index_by_symptom.items():
                ordered = sorted(
                    ids, key=lambda node_id: node_by_id[node_id]["timestamp_day"]
                )
                for index in range(1, len(ordered)):
                    edges.append(
                        {
                            "source": ordered[index - 1],
                            "target": ordered[index],
                            "relation": "persists",
                            "confidence": 0.75,
                            "rationale": "same symptom appears again",
                        }
                    )

        episodes: list[dict[str, Any]] = []
        if nodes:
            window = max(1, int(getattr(self.configs, "coc_episode_window_days", 7)))
            grouped: dict[int, list[dict[str, Any]]] = {}
            for node in nodes:
                bucket = node["time_norm"]["days_ago"] // window
                grouped.setdefault(bucket, []).append(node)
            # Ascending bucket order = most recent episode (E_0) first, matching
            # upstream build_episodes_by_window.
            for bucket in sorted(grouped):
                episode_nodes = sorted(
                    grouped[bucket], key=lambda node: node["timestamp_day"]
                )
                episodes.append(
                    {
                        "episode_id": f"E_{bucket}",
                        "window_days": window,
                        "time_range": self.episode_time_range(bucket, window),
                        "salient_node_ids": [node["id"] for node in episode_nodes],
                    }
                )
        nodes_by_id = {node["id"]: node for node in nodes}
        cards = [
            self.render_memory_card(
                episode,
                [nodes_by_id[node_id] for node_id in episode["salient_node_ids"]],
            )
            for episode in episodes
        ]
        return {
            "graph": {
                "time_axis": {
                    "anchor_day": latest,
                    "unit": "day",
                },
                "timeline_type": kind,
                "nodes": nodes,
                "edges": edges,
                "index": {
                    "by_day": index_by_day,
                    "by_symptom": index_by_symptom if kind == "symptom" else None,
                },
            },
            "episodes": episodes,
            "cards": cards,
        }

    def build_timeline_memory(
        self,
        symptom: ds.SymptomTimeline,
        life_event: ds.LifeEventTimeline,
    ) -> ds.TimelineMemory:
        return ds.TimelineMemory(
            symptom=self.process_timeline("symptom", symptom.timeline),
            life_event=self.process_timeline("life_event", life_event.timeline),
        )

    def upsert_output(self, character: ds.DeprofileCharacter) -> None:
        path = Path(self.configs.output_path)
        records: list[dict[str, Any]] = []
        if path.exists():
            records = load_json(str(path))
            if not isinstance(records, list):
                raise ValueError(f"Deprofile output must be a JSON list: {path}")
        dumped = character.model_dump(mode="json")
        records = [
            record
            for record in records
            if record.get("profile_id") != character.profile_id
        ]
        records.append(dumped)
        save_json(records, str(path), overwrite=True)

    def select_candidate(
        self, profile: ds.ClinicalProfile
    ) -> tuple[str, ds.MatchMetadata]:
        rank = int(self.configs.candidate_rank)
        if profile.candidate_id:
            if 0 <= rank < len(profile.candidate_id):
                return self.select_index_candidate(profile)
            raise IndexError(
                f"candidate_rank {rank} is invalid for "
                f"{len(profile.candidate_id)} indexed candidates"
            )
        return self.select_rematched_candidate(profile)

    def generate_character(self) -> ds.DeprofileCharacter:
        profile = self.load_clinical_profile()
        assessment, counseling = self.load_dialogues()
        user_id, match = self.select_candidate(profile)
        symptom, life_event = self.load_timelines(user_id)
        timeline_memory = self.build_timeline_memory(symptom, life_event)

        character = ds.DeprofileCharacter(
            profile_id=str(self.configs.profile_id),
            clinical_profile=profile,
            assessment_dialogue=assessment,
            counseling_dialogue=counseling,
            social_user_id=user_id,
            symptom_timeline=symptom,
            life_event_timeline=life_event,
            timeline_memory=timeline_memory,
            match_metadata=match,
            provenance=ds.Provenance(
                generator_version="1",
                language=str(self.configs.lang),
                source_paths={
                    "clinical_profiles": (
                        f"{self.resource_dir}/deprofiles_complete_index.json"
                    ),
                    "social_profiles": str(self.configs.social_profiles_path),
                    "assessment_dialogues": (
                        f"{self.resource_dir}/assessment_dialogues.json"
                    ),
                    "counseling_dialogues": (
                        f"{self.resource_dir}/counseling_dialogues.json"
                    ),
                    "symptom_timelines": (
                        f"{self.resource_dir}/symptom_timelines.json"
                    ),
                    "life_event_timelines": (
                        f"{self.resource_dir}/life_event_timelines.json"
                    ),
                },
                completeness={
                    "assessment": True,
                    "counseling": True,
                    "symptom_timeline": True,
                    "life_event_timeline": True,
                },
            ),
        )
        self.upsert_output(character)
        return character
