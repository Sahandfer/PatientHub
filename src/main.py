import os
import json
import argparse
import streamlit as st
from agents import get_patient, get_therapist


PATIENTS = json.load(open("src/config/patients.json"))
THERAPISTS = json.load(open("src/config/therapists.json"))


st.html("<style>" + open("./assets/styles.css").read() + "</style>")

state = {"messages": []}

for k, v in state.items():
    if k not in st.session_state:
        st.session_state[k] = v


def generate_response(agent, msg, idx=0):
    if not idx:
        res = agent.generate_response()
    else:
        res = agent.receive_message(msg)
    st.session_state.messages.append({"role": agent.role, "content": res})
    return res


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
    # Parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--model_type", type=str, default="openai")
    parser.add_argument("--model_path", type=str, default="gpt-4o")
    parser.add_argument("--lang", type=str, default="all", choices=["en", "zh"])
    parser.add_argument("--device", type=int, default=-1)
    args = parser.parse_args()

    patient = get_patient("basic")

    # patient.fill_prompt(patients[0])

    therapist = get_therapist("basic")
    # therapist.fill_prompt(therapists[0])

    # st.write(patient.sys_prompt)

    # st.markdown("# Therapy Simulation")

    # chatbox_container = st.container(height=500, border=True, key="chatbox")
    # chat_container = chatbox_container.container(
    #     height=500, border=False, key="chat_box"
    # )

    # st.button(
    #     "Start Simulation",
    #     on_click=start_simulation,
    #     args=(patient, therapist, chat_container),
    # )

    # with chatbox_container:
    #     with chat_container:
    #         for msg in st.session_state.messages:
    #             st.chat_message(msg["role"]).markdown(msg["content"])
