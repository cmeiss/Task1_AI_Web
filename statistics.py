import streamlit as st

#very basic statistics page, just showing number of incorrect guesses vs. number of total guesses

st.header("Game Statistics")

st.metric(label="Number of incorrect guesses", value=st.session_state['number of guesses'] - st.session_state['correct guesses'])

st.metric(label="Number of won games", value=st.session_state['correct guesses'])