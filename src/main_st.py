import os
import json
import argparse
import streamlit as st
from components.character import Character
from agents import BasicClient, BasicTherapist
from langchain_openai import ChatOpenAI
from dotenv import load_dotenv
from datetime import datetime


load_dotenv(".env")

model = ChatOpenAI(
    model=os.environ.get("MODEL_NAME"),
    base_url=os.environ.get("BASE_URL"),
    api_key=os.environ.get("API_KEY"),
    temperature=0.6,
)


CLIENTS = json.load(open("data/characters/clients.json"))
THERAPISTS = json.load(open("data/characters/therapists.json"))


st.set_page_config(layout="wide")
st.html("<style>" + open("./assets/styles.css").read() + "</style>")


state = {
    "therapy_session": None,
    "active": False,
}

for k, v in state.items():
    if k not in st.session_state:
        st.session_state[k] = v


class TherapySession:
    def __init__(self, client_data, therapist_data):
        self.messages = []
        self.active = True
        self.homework = ""
        self.start_time = datetime.now()
        self.turn_count = 0
        self.set_client(client_data)
        self.set_therapist(therapist_data)

    def set_client(self, data):
        self.client = BasicClient(model, data)
        print(f"Set client: {data['demographics']['name']}")

    def set_therapist(self, data):
        self.therapist = BasicTherapist(model, data)
        print(f"Set therapist: {data['demographics']['name']}")

    def set_agenda(self):
        self.therapist.generate_agenda()

    def add_interaction(self, role: str, message: str):
        self.messages.append(
            {
                "turn": self.turn_count + 1,
                "role": role,
                "content": message,
            }
        )

    def generate_response(self):
        chat_history = "\n".join(
            f"{msg['role']}: {msg['content']}" for msg in self.messages
        )
        if self.turn_count % 2 == 0:
            msg = self.therapist.generate_response(chat_history)
            self.add_interaction("Therapist", msg)
        else:
            msg = self.client.generate_response(chat_history)
            self.add_interaction("Client", msg)

        self.turn_count += 1
        # Return the new message for immediate display
        return self.messages[-1]

    def get_conv_len(self):
        return len(self.messages)

    def simulate(self):
        # Setting the agenda at the beginning of the session
        self.set_agenda()
        return self.generate_response()

    def end_session(self):
        self.active = False
        self.end_time = datetime.now()
        print(f"Session ended at {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.save_session()

    def save_session(self):
        with open(f"session_{self.start_time.strftime('%Y%m%d_%H%M%S')}.txt", "w") as f:
            for msg in self.messages:
                f.write(
                    f"{msg.get('timestamp', '')} [{msg['role']}] {msg['content']}\n"
                )

    def reset(self):
        self.messages = []
        self.active = True
        self.homework = ""
        self.start_time = datetime.now()
        self.turn_count = 0
        self.therapist.reset_agent()
        self.client.reset_agent()
        print("Session reset.")


if __name__ == "__main__":
    # Initialize session state
    if st.session_state.therapy_session is None:
        therapy_session = TherapySession(CLIENTS[0], THERAPISTS[0])

    client_col, chat_col, therapist_col = st.columns([1, 3, 1])

    # Display character information if session exists
    if st.session_state.therapy_session is not None:
        ts = st.session_state.therapy_session
        client_col.write(ts.client.sys_prompt)
        if hasattr(ts.therapist, "agenda"):
            print(ts.therapist.agenda)
        therapist_col.write(ts.therapist.sys_prompt)

    # Create chat containers
    chatbox_container = chat_col.container(height=600, border=True, key="chatbox")

    # Display all current messages
    if st.session_state.therapy_session is not None:
        ts = st.session_state.therapy_session
        with chatbox_container:
            for msg in ts.messages:
                st.chat_message(msg["role"]).markdown(msg["content"])

    # Control buttons
    if chat_col.button("Start Simulation"):
        print("Starting simulation...")
        if st.session_state.therapy_session is None:
            st.session_state.therapy_session = TherapySession(CLIENTS[0], THERAPISTS[0])
        st.session_state.active = True
        # Generate first response immediately
        new_msg = st.session_state.therapy_session.simulate()
        st.rerun()

    if (
        chat_col.button("Continue Simulation")
        and st.session_state.therapy_session is not None
    ):
        if st.session_state.therapy_session.turn_count < 4:
            new_msg = st.session_state.therapy_session.generate_response()
            st.rerun()
        else:
            st.session_state.active = False

    if chat_col.button("Reset Simulation"):
        if st.session_state.therapy_session is not None:
            print("Resetting simulation...")
            st.session_state.therapy_session.reset()
            st.session_state.active = False
            st.rerun()

    # Auto-continue simulation if active
    if st.session_state.active and st.session_state.therapy_session is not None:
        if st.session_state.therapy_session.turn_count < 4:
            # Use a small delay to make the conversation feel more natural
            import time

            time.sleep(1)
            new_msg = st.session_state.therapy_session.generate_response()
            st.rerun()
        else:
            st.session_state.active = False
