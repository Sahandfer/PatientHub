import streamlit as st
from agents.therapist import TherapistAgent
from agents.client import ClientAgent
from datetime import datetime

class TherapySession:
    def __init__(self):
        self.start_time = datetime.now()
        self.turn_count = 0
        self.agenda = []
        self.homework = ""
        self.history = []
        self.active = True

    def add_interaction(self, speaker: str, message: str):
        self.history.append({
            "turn": self.turn_count,
            "speaker": speaker,
            "message": message,
            "timestamp": datetime.now().strftime("%H:%M:%S")
        })
        self.turn_count += 1
        
# Initialize session state
if 'session' not in st.session_state:
    st.session_state.session = None
    st.session_state.agenda_set = False

# Add to streamlit_app.py
def set_agenda():
    st.header("Session Setup")
    agenda_items = st.multiselect(
        "Select session agenda items:",
        options=["Mood Check", "Thought Patterns", "Behavior Analysis", 
                 "Homework Review", "Coping Strategies", "Goal Setting"],
        default=["Mood Check"]
    )
    custom_item = st.text_input("Add custom agenda item:")
    
    if custom_item:
        agenda_items.append(custom_item)
    
    if st.button("Start Session"):
        st.session_state.session = TherapySession()
        st.session_state.session.agenda = agenda_items
        st.session_state.agenda_set = True
    
# Add to streamlit_app.py
def main_session():
    st.header("Therapy Session Progress")
    
    # Initialize agents
    therapist = TherapistAgent(agenda=st.session_state.session.agenda)
    client = ClientAgent()
    
    # Session controls
    col1, col2 = st.columns(2)
    with col1:
        st.progress(st.session_state.session.turn_count / 30)
        st.caption(f"Turns remaining: {30 - st.session_state.session.turn_count}")
    
    # Display chat history
    for msg in st.session_state.session.history:
        with st.chat_message(msg["speaker"].lower()):
            st.write(f"{msg['speaker']}: {msg['message']}")
    
    # Handle session termination
    if st.session_state.session.turn_count >= 30 or not st.session_state.session.active:
        homework = therapist.assign_homework(st.session_state.session.history)
        st.session_state.session.homework = homework
        show_conclusion()
        return
    
    # Therapist's turn
    if st.session_state.session.turn_count % 2 == 0:
        therapist_msg = therapist.generate_response(st.session_state.session.history)
        st.session_state.session.add_interaction("Therapist", therapist_msg)
        st.rerun()
    
    # Client's turn
    else:
        client_msg = client.generate_response(st.session_state.session.history)
        st.session_state.session.add_interaction("Client", client_msg)
        st.rerun()

# Add to streamlit_app.py
def show_conclusion():
    st.header("Session Conclusion")
    st.subheader("Assigned Homework")
    st.write(st.session_state.session.homework)
    
    st.subheader("Session Summary")
    for item in st.session_state.session.agenda:
        status = "✅" if therapist.agenda_item_completed(item) else "◻️"
        st.write(f"{status} {item}")
    
    if st.button("Start New Session"):
        st.session_state.clear()
        st.rerun()

# Add to streamlit_app.py
def main():
    if not st.session_state.agenda_set:
        set_agenda()
    else:
        main_session()

if __name__ == "__main__":
    main()