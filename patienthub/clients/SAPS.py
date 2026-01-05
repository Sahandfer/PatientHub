import random
from typing import Any, Dict, List, Literal
from dataclasses import dataclass
from pydantic import BaseModel, Field
from jinja2 import Template

from patienthub.base import ChatAgent
from patienthub.configs import APIModelConfig
from patienthub.utils import load_json, get_chat_model, save_json, load_yaml

from omegaconf import DictConfig
from langchain_core.messages import (
    AIMessage,
    HumanMessage,
    SystemMessage,
)


@dataclass
class SAPSClientConfig(APIModelConfig):
    """Configuration for the SAPSClient agent."""
    
    agent_type: str = "SAPS"
    data_path: str = "data/characters/SAPS.json"
    raw_data_dir: str = "data/resources/SAPS/"
    data_idx: int = 0


# Pydantic models for state detection and response
class StateDetectionStageI(BaseModel):
    """Stage I: five types of doctor's questions classification"""
    
    question_type: Literal["A", "B", "C", "D", "E"] = Field()


class StateDetectionStageII(BaseModel):
    """Stage II: determine the question is specific or broad"""
    
    specificity: Literal["具体", "宽泛", "Specific", "Broad"] = Field(
        description="Whether the question/advise is 具体Specific还是宽泛Broad"
    )


class MemoryExtraction(BaseModel):
    """Stage III: Memory extraction"""
    
    has_relevant_info: bool = Field(
        description="Whether there is relevant information in the medical record"
    )
    extracted_text: str = Field(
        default="",
        description="The extracted text fragment, if there is no relevant information, it is empty"
    )


class PatientResponse(BaseModel):
    """Patient final response"""
    
    content: str = Field(
        description="The content of the patient's response"
    )


class SAPSClient(ChatAgent):
    """State-Aware Patient Simulator Client.
    
    Implement three-stage state detection process:
    1. Stage I: classify the doctor's questions into five types: A/B/C/D/E
    2. Stage II: determine the question is specific or broad (only A/B)
    3. Stage III: extract relevant information from the complete medical record (only A-A/B-A)
    4. select the corresponding state_instruction prompt based on the final state (A-A-A/A-A-B/A-B/B-A-A/B-A-B/B-B)
    5. generate patient's response and update the history
    """
    
    def __init__(self, configs: DictConfig):
        self.configs = configs 
        
        # create case data
        self.data = self._load_random_case()    
        self.name = self.data.get("name", "Patient")
            
        self.chat_model = get_chat_model(configs)
        # Load prompts with nested structure support
        self.prompts = self._load_prompts_nested(configs.lang)
        
        # Initialize conversation history
        self.messages: List[Any] = []
        self.therapist = "Doctor"
    
    def _load_prompts_nested(self, lang: str) -> Dict[str, Any]:
        """Load prompts with nested structure"""
        path = "data/prompts/client/SAPS.yaml"
        data = load_yaml(path)[lang]
        
        def process_prompts(obj):
            if isinstance(obj, str):
                return Template(obj)
            elif isinstance(obj, dict):
                return {k: process_prompts(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [process_prompts(item) for item in obj]
            else:
                return obj
        
        return process_prompts(data)
    
    def _load_random_case(self) -> Dict[str, Any]:
        """Randomly select a case from the corresponding dataset based on language and save it to SAPS.json"""
        
        if self.configs.lang == "zh":
            dataset_file = random.choice([
                "HospitalCases.json",
                "Patient_Simulator_Test.json"
            ])
        else:  # en
            dataset_file = "MedicalExam.json"
        
        dataset_path = f"{self.configs.raw_data_dir}{dataset_file}"
        cases = load_json(dataset_path)
        selected_case = random.choice(cases)
        
        # extract core fields
        raw_data = selected_case.get("raw_data") or {}
        patient_info = raw_data.get("question", "")
        case_data = {
            "id": selected_case.get("id", 0),
            "patient_info": patient_info,
            "source": dataset_file
        }
        
        # save to data/characters/SAPS.json
        save_json(case_data, self.configs.data_path, overwrite=True)
        return case_data
    
    def _detect_state_stage_I(self, doctor_question: str) -> str:
        """Stage I: (A/B/C/D/E)"""
        
        prompt = self.prompts["state_detection"]["stage_I"].render(
            question=doctor_question
        )
        
        result = self.generate(
            messages=[SystemMessage(content=prompt)],
            response_format=StateDetectionStageI
        )
        return result.question_type
    
    def _detect_state_stage_II(self, doctor_question: str, question_type: str) -> str:
        
        if question_type not in ["A", "B"]:
            return ""
        
        prompt = self.prompts["state_detection"]["stage_II"][question_type].render(
            question=doctor_question
        )
        
        result = self.generate(
            messages=[SystemMessage(content=prompt)],
            response_format=StateDetectionStageII
        )
        
        # Normalize output to A (具体/Specific) or B (宽泛/Broad)
        if result.specificity in ["具体", "Specific"]:
            return "A"
        else:
            return "B"
    
    def _extract_memory_stage_III(
        self, 
        doctor_question: str, 
        question_type: str,
        patient_info: str
    ) -> str:
        """Stage III: (only for A-A or B-A)"""
        
        prompt = self.prompts["state_detection"]["stage_III"][question_type].render(
            question=doctor_question,
            patient_info=patient_info
        )
        
        result = self.generate(
            messages=[SystemMessage(content=prompt)],
            response_format=MemoryExtraction
        )
        return result.extracted_text if result.has_relevant_info else ""
    
    def set_therapist(
        self, 
        therapist: Dict[str, Any], 
        prev_sessions: List[Dict[str, str]] | None = None
    ):
        self.therapist = therapist.get("name", "Doctor")
    
    def generate(
        self, 
        messages: List[Any], 
        response_format: BaseModel
    ) -> BaseModel:
        """Generate response using structured output"""
        chat_model = self.chat_model.with_structured_output(response_format)
        res = chat_model.invoke(messages)
        return res
    
    def generate_response(self, msg: str) -> PatientResponse:
        """Main entry: receive doctor's message and generate patient's response"""
        
        self.messages.append(HumanMessage(content=msg))
        
        # 1. Stage I
        question_type = self._detect_state_stage_I(msg)
        
        # 2. initialize the state and memory
        final_state = question_type
        memory = ""
        
        # 3. Stage II: (only A/B)
        if question_type in ["A", "B"]:
            specificity = self._detect_state_stage_II(msg, question_type)
            final_state = f"{question_type}-{specificity}"
            
            # 4. Stage III
            if specificity == "A":
                memory = self._extract_memory_stage_III(
                    msg, 
                    question_type, 
                    self.data["patient_info"]
                )
                has_memory = "A" if memory else "B"
                final_state = f"{question_type}-{specificity}-{has_memory}"
        
        # 5. final response prompt
        instruction_prompt = self.prompts["state_instruction"][final_state].render(
            patient_info=memory or ""  # only provide the extracted memory fragment
        )
        
        # 6. system instruction + conversation history
        full_messages = [SystemMessage(content=instruction_prompt)] + self.messages
        
        result = self.generate(
            messages=full_messages,
            response_format=PatientResponse
        )
        
        self.messages.append(AIMessage(content=result.content))
        
        return result
    
    def reset(self):
        """Reset the conversation state"""
        self.messages = []
        self.therapist = "Doctor"
