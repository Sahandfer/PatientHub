from .base import BaseAgent
from pydantic import BaseModel, Field
from langchain_core.output_parsers import PydanticOutputParser


class BaseTherapistResponse(BaseModel):
    reasoning: str = Field(
        description="reason about the patients' thoughts and feelings in 1-2 sentences."
    )
    # patient_mental_state: Dict[str, MentalState] = Field(
    #     description="Current mental state of the patient"
    # )
    content: str = Field(description="Your generated response based on your reasoning")


class BasicTherapist(BaseAgent):
    def __init__(self, client):
        super().__init__(client)
        self.parser = PydanticOutputParser(pydantic_object=BaseTherapistResponse)

    def set_prompt(self, prompt):
        self.sys_prompt = prompt

    def fill_prompt(self, profile):
        demographics = profile["demographics"]
        personality = profile["personality"]
        self.sys_prompt = self.sys_prompt.format(
            demographics=to_bullet_list(profile["demographics"]),
            personality=to_bullet_list(profile["personality"]),
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
        print(res)

        return f"[{res['reasoning']}] -> {res['content']}"
