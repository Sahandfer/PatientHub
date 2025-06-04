from .base import BaseAgent
from pydantic import BaseModel, Field
from prompts import get_prompt
from utils import parse_json_response, get_model_client
from typing import Dict, Any
from brain import MentalState
from camel.agents import ChatAgent


class BasicClientResponse(BaseModel):
    # mental_state: Dict[str, MentalState] = Field(
    #     description="Your current mental state"
    # )
    response: str = Field(
        description="Your generated response based on your profile and mental state"
    )


class BasicClient(BaseAgent):
    def __init__(self, model_name: str, data: Dict[str, Any]):
        self.role = "Client"
        self.agent_type = "basic"
        self.model_client = get_model_client(model_name)
        self.data = data
        self.agent = self.create_agent()
        self.messages = []
        self.mental_state = MentalState().model_dump(mode="json")

    def create_agent(self):
        self.sys_prompt = get_prompt(self.role, self.agent_type).render(
            data=self.data, therapist={"name": "Sarah", "specialization": "CBT"}
        )
        return ChatAgent(model=self.model_client, system_message=self.sys_prompt)

    def init_mental_state(self):
        # ms_pt = """Based on your profile, generate your initial mental state."""
        # res = self.agent.step(ms_pt, response_format=MentalState)
        # self.mental_state = parse_json_response(res.msgs[0].content)
        self.mental_state = {
            "Beliefs": "I believe I'm constantly under pressure to perform well, and it's difficult to meet everyone's expectations.",
            "Desires": "I want to manage my anxiety better and feel more at ease with my work responsibilities.",
            "Emotion": "Anxiety",
            "Intents": "I'm here to explore techniques that can help me cope and improve my situation.",
            "Trust_Level": 0,
        }

    def generate_response(self, msg: str):
        res = self.agent.step(msg, response_format=BasicClientResponse)
        return parse_json_response(res.msgs[0].content)

    def reset(self):
        self.agent.reset()

        # class BasicClient(BaseAgent):
        #     def __init__(self, model, data):
        #         super().__init__(role="client", model=model)
        #         self.agent_name = "basic"
        #         self.mental_state = {
        #             "Emotion": "Unknown",
        #             "Beliefs": "Unknown",
        #             "Desires": "Unknown",
        #             "Intents": "Unknown",
        #             "Trust Level": 0,
        #         }
        #         self.data = data
        #         self.sys_prompt = ""

        #     def set_sys_prompt(self, mode: str):
        #         self.sys_prompt = get_prompt(self.role, self.agent_name).render(
        #             data=self.data,
        #             response_format=self.parser.get_format_instructions(),
        #             mode=mode,
        #             therapist={"name": "Sarah", "specialization": "CBT"},
        #         )
        #         self.messages = [{"role": "system", "content": self.sys_prompt}]

        #     def generate(self, messages):
        #         # Retry up to 3 times in case of failure
        #         for i in range(3):
        #             try:
        #                 res = self.model.invoke(messages)
        #                 res = parse_json_response(res.content)
        #                 return res
        #             except Exception as e:
        #                 print(f"Error generating response: {e}")
        #                 sleep(2)
        #         return {}

        #     def init_mental_state(self, data):
        #         #
        #         # self.set_prompt(mode="mental_state")
        #         # res = self.model.invoke(self.messages)
        #         # self.mental_state = parse_json_response(res.content)
        #         # print(res)
        #         pass

        #     def generate_response(self, chat_history):
        #         self.parser = PydanticOutputParser(pydantic_object=BasicClientResponse)
        #         self.set_sys_prompt(mode="conversation")

        #         msg = f"Generate your response for the next turn:\n\n{chat_history}\n\n"
        #         messages = self.messages + [{"role": "user", "content": msg}]

        #         res = self.generate(messages)

        #         self.mental_state = res["mental_state"]
        #         response = res["response"]

        #         return response

        #     def reset_agent(self):
        #         self.__init__(self.model, self.data)

        # class PatientPsiResponse(BaseModel):
        #     content: str = Field(description="Your generated response")

        # class PatientPsi(BaseAgent):
        #     r"""
        #     Patient-{Psi} Agent
        #     Based on the paper "PATIENT-Ψ: Using Large Language Models to Simulate Patients for Training Mental Health Professionals"
        #     """

        #     def __init__(self, client):
        #         super().__init__(role="patient", client=client)
        #         self.agent_name = "patient-psi"
        #         self.sys_prompt = get_prompt(self.role, self.agent_name)
        #         self.parser = PydanticOutputParser(pydantic_object=PatientPsiResponse)

        #     def set_prompt(self, data):
        #         sys_prompt = self.sys_prompt.render(
        #             data=data,
        #             patientTypeContent="You should try your best to act like a patient who talks a lot: 1) you may provide detailed responses to questions, even if directly relevant, 2) you may elaborate on personal experiences, thoughts, and feelings extensively, and 3) you may demonstrate difficulty in allowing the therapist to guide the conversation. But you must not exceed 8 sentences each turn. Attention: The most important thing is to be as natural as possible and you should be verbose in some turns and be concise in other turns. You could listen to the therapist more as the session goes when you feel more trust in the therapist.",
        #         )
        #         self.messages = [
        #             {
        #                 "role": "system",
        #                 "content": sys_prompt,
        #             }
        #         ]

        #     def receive_message(self, msg):
        #         self.messages.append(
        #             {
        #                 "role": "user",
        #                 "content": msg,
        #             }
        #         )
        #         return self.generate_response()

        #     def generate_response(self):
        #         res = self.client.invoke(self.messages)
        #         # res = parse_json_response(res.content)
        # return res.content
