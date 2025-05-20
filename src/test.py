import os
import json
import argparse
import streamlit as st
from langchain_openai import ChatOpenAI
from agents import get_patient, get_therapist
from dotenv import load_dotenv


load_dotenv(".env")

client = ChatOpenAI(
    model=os.environ.get("MODEL_NAME"),
    base_url=os.environ.get("API_URL"),
    api_key=os.environ.get("API_KEY"),
    temperature=0.6,
)


MODE = "interactive"
PATIENTS = json.load(open("data/Patient Psi CM Dataset.json"))
THERAPISTS = json.load(open("data/therapists.json"))


st.html("<style>" + open("./assets/styles.css").read() + "</style>")

state = {"messages": []}

for k, v in state.items():
    if k not in st.session_state:
        st.session_state[k] = v


def generate_response(agent, msg, idx=0, mode=MODE):
    if mode == "interactive":
        res = agent.receive_message(msg)
        return res
    elif mode == "simulation":
        if not idx:
            res = agent.generate_response()
        else:
            res = agent.receive_message(msg)
        st.session_state.messages.append({"role": agent.role, "content": res})
        return res
    else:
        print("Mode not supported")


def reset_simulation(patient, therapist):
    patient.reset_messages()
    therapist.reset_messages()
    st.session_state.messages = []


def start_simulation(patient, therapist, chat_container):
    reset_simulation(patient, therapist)
    conv_len = 3
    prev_res = ""
    for i in range(conv_len):
        role = "patient" if i % 2 == 0 else "therapist"
        prev_res = generate_response(therapist if i % 2 == 0 else patient, prev_res, i)
        chat_container.chat_message(role).markdown(prev_res)


if __name__ == "__main__":

    patient = get_patient("patient-psi")(client)
    patient.set_prompt(PATIENTS[0])

    # patient.fill_prompt(patients[0])

    # therapist = get_therapist("basic")
    # therapist.fill_prompt(therapists[0])

    # st.write(patient.sys_prompt)

    st.markdown("# Therapy Simulation")
    chatbox_container = st.container(height=1000, border=True, key="chatbox")
    chat_container = chatbox_container.container(
        height=900, border=False, key="chat_box"
    )
    input_container = chatbox_container.container(
        height=100, border=False, key="input_box"
    )

    chat_input = input_container.chat_input(
        placeholder="Type a message", key="chat_input"
    )
    if chat_input:
        st.session_state.messages.append({"role": "user", "content": chat_input})
        response = generate_response(patient, chat_input)
        st.session_state.messages.append({"role": patient.role, "content": response})

    # st.button(
    #     "Start Simulation",
    #     on_click=start_simulation,
    #     args=(patient, therapist, chat_container),
    # )

    with chatbox_container:
        with chat_container:
            for msg in st.session_state.messages:
                st.chat_message(msg["role"]).markdown(msg["content"])
