import streamlit as st
import pandas as pd
from collections import Counter

#very basic statistics page, just showing number of incorrect guesses vs. number of total guesses

st.header("Game Statistics")

st.metric(label="Number of incorrect guesses", value=st.session_state['number of guesses'] - st.session_state['correct guesses'])

st.metric(label="Number of won games", value=st.session_state['correct guesses'])

count = Counter(st.session_state['target stats'])
st.bar_chart(count)

# num_guess_per_game = {"Number of games": st.session_state['correct guesses'], "Number of guesses": st.session_state['number of guesses']}
# df_num_guess_per_game = pd.DataFrame()
# st.bar_chart(df_num_guess_per_game)

#st.metric(label="Number of games played", value=st.session_state[''])