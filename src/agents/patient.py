from .base import BaseAgent
from pydantic import BaseModel, Field
from prompts import get_prompt
from utils import parse_json_response, to_bullet_list
from langchain_core.output_parsers import PydanticOutputParser


class BasePatientResponse(BaseModel):
    emotion: str = Field(description="Current emotion. Could be either sad/angry/happy")
    content: str = Field(description="Your generated response based on your emotions")


class BasicPatient(BaseAgent):
    def __init__(self, client):
        super().__init__(client)
        self.parser = PydanticOutputParser(pydantic_object=BasePatientResponse)

    def set_prompt(self, prompt):
        self.sys_prompt = prompt

    def fill_prompt(self, profile):
        demographics = profile["demographics"]
        personality = profile["personality"]
        current_issue = profile["current_issue"]
        coping_mechanisms = current_issue["coping_mechanisms"]
        mechanisms = coping_mechanisms["Negative"] + coping_mechanisms["Positive"]

        self.sys_prompt = self.sys_prompt.format(
            demographics=to_bullet_list(demographics),
            personality=to_bullet_list(personality),
            social_circle=len(profile["social_circle"]),
            description=current_issue["description"],
            duration=current_issue["duration"],
            severity=current_issue["severity"],
            triggers=(", ").join(current_issue["triggers"]),
            coping_mechanisms=to_bullet_list(mechanisms),
        )
        self.sys_prompt += "\n # Output\n\n" + self.parser.get_format_instructions()
        self.messages = [{"role": "system", "content": self.sys_prompt}]

    def receive_message(self, msg):
        self.messages.append(
            {
                "role": "user",
                "content": msg,
            }
        )
        return self.generate_response()

    def generate_response(self):
        res = self.model.invoke(self.messages)
        res = parse_json_response(res.content)
        return f"{res['emotion']} -> {res['content']}"
        # return res.content


class PatientPsiResponse(BaseModel):
    content: str = Field(description="Your generated response")


class PatientPsi(BaseAgent):
    r"""
    Patient-{Psi} Agent
    Based on the paper "PATIENT-Ψ: Using Large Language Models to Simulate Patients for Training Mental Health Professionals"
    """

    def __init__(self, client):
        super().__init__(role="patient", client=client)
        self.agent_name = "patient-psi"
        self.sys_prompt = get_prompt(self.role, self.agent_name)
        self.parser = PydanticOutputParser(pydantic_object=PatientPsiResponse)

    def set_prompt(self, data):
        sys_prompt = self.sys_prompt.render(
            data=data,
            patientTypeContent="You should try your best to act like a patient who talks a lot: 1) you may provide detailed responses to questions, even if directly relevant, 2) you may elaborate on personal experiences, thoughts, and feelings extensively, and 3) you may demonstrate difficulty in allowing the therapist to guide the conversation. But you must not exceed 8 sentences each turn. Attention: The most important thing is to be as natural as possible and you should be verbose in some turns and be concise in other turns. You could listen to the therapist more as the session goes when you feel more trust in the therapist.",
        )
        self.messages = [
            {
                "role": "system",
                "content": sys_prompt,
            }
        ]

    def receive_message(self, msg):
        self.messages.append(
            {
                "role": "user",
                "content": msg,
            }
        )
        return self.generate_response()

    def generate_response(self):
        res = self.client.invoke(self.messages)
        # res = parse_json_response(res.content)
        return res.content
