# coding=utf-8
# Licensed under the MIT License;

"""Adapter schema for psyche characters."""

from pydantic import Field

from .base import CharacterModel


class PsycheCharacter(CharacterModel):
    class MFCProfile(CharacterModel):
        class IdentifyingData(CharacterModel):
            age: str = Field(alias="Age")
            sex: str = Field(alias="Sex")
            marital_status: str = Field(alias="Marital status")
            occupation: str = Field(alias="Occupation")

        class ChiefComplaint(CharacterModel):
            description: str = Field(alias="Description")

        class PresentIllness(CharacterModel):
            class Symptom(CharacterModel):
                name: str = Field(alias="Name")
                length: str = Field(alias="Length")
                alleviating_factor: str = Field(alias="Alleviating factor")
                exacerbating_factor: str = Field(alias="Exacerbating factor")
                triggering_factor: str = Field(alias="Triggering factor")
                stressor: str = Field(alias="Stressor")

            symptom: Symptom = Field(alias="Symptom")

        class PastPsychiatricHistory(CharacterModel):
            presence: str = Field(alias="Presence")
            description: str | None = Field(alias="Description")

        class PastMedicalHistory(CharacterModel):
            presence: str = Field(alias="Presence")
            history: str = Field(alias="History")

        class CurrentMedication(CharacterModel):
            medication_name: str = Field(alias="Medication name")
            duration: str = Field(alias="Duration")
            compliance: str = Field(alias="Compliance")
            effect: str = Field(alias="Effect")
            side_effect: str = Field(alias="Side effect")

        class FamilyHistory(CharacterModel):
            diagnosis: str = Field(alias="Diagnosis")
            substance_use: str = Field(alias="Substance use")

        class DevelopmentalSocialHistory(CharacterModel):
            class ChildhoodHistory(CharacterModel):
                home_environment: str = Field(alias="Home environment")
                members_of_family: str = Field(alias="Members of family")
                social_environment: str = Field(alias="Social environment")

            childhood_history: ChildhoodHistory = Field(alias="Childhood history")
            school_history: str = Field(alias="School history")
            work_history: str = Field(alias="Work history")

        class Impulsivity(CharacterModel):
            suicidal_ideation: str = Field(alias="Suicidal ideation")
            suicidal_plan: str = Field(alias="Suicidal plan")
            suicidal_attempt: str = Field(alias="Suicidal attempt")
            self_mutilating_behavior_risk: str = Field(
                alias="Self-mutilating behavior risk"
            )
            homicide_risk: str = Field(alias="Homicide risk")

        identifying_data: IdentifyingData = Field(alias="Identifying data")
        chief_complaint: ChiefComplaint = Field(alias="Chief complaint")
        present_illness: PresentIllness = Field(alias="Present illness")
        past_psychiatric_history: PastPsychiatricHistory = Field(
            alias="Past psychiatric history"
        )
        past_medical_history: PastMedicalHistory = Field(
            alias="Past medical history"
        )
        current_medication: CurrentMedication = Field(alias="Current medication")
        family_history: FamilyHistory = Field(alias="Family history")
        developmental_social_history: DevelopmentalSocialHistory = Field(
            alias="Developmental/social history"
        )
        impulsivity: Impulsivity = Field(alias="Impulsivity")

    class MFCBehavior(CharacterModel):
        general_appearance_attitude_behavior: str = Field(
            alias="General appearance/attitude/behavior"
        )
        mood: str = Field(alias="Mood")
        affect: str = Field(alias="Affect")
        spontaneity: str = Field(alias="Spontaneity")
        verbal_productivity: str = Field(alias="Verbal productivity")
        tone_of_voice: str = Field(alias="Tone of voice")
        social_judgement: str = Field(alias="Social judgement")
        insight: str = Field(alias="Insight")
        reliability: str = Field(alias="Reliability")
        perception: str = Field(alias="Perception")
        thought_process: str = Field(alias="Thought process")
        thought_content: str = Field(alias="Thought content")

    MFC_Profile: MFCProfile = Field(alias="MFC-Profile")
    MFC_History: str = Field(alias="MFC-History")
    MFC_Behavior: MFCBehavior = Field(alias="MFC-Behavior")
