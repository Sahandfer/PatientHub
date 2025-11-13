import streamlit as st


class Character:
    def __init__(self, data):
        self.data = data

    def get_character(self, st_column):
        # Demographics
        demographics = self.data.get("demographics", {})
        with st_column.container(border=True):

            for k, v in demographics.items():
                st.markdown(f"{k} = {v}")

    def get_mental_state(self, mental_state, st_column, title=""):
        # Mental State
        with st_column.container(border=True):
            st.markdown(f"### {title}")
            for k, v in mental_state.items():
                st.markdown(f"{k} = {v}")
