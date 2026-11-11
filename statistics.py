import streamlit as st
import pandas as pd
from collections import Counter

#very basic statistics page, just showing number of incorrect guesses vs. number of total guesses

st.header("Game Statistics")

# st.metric(label="Number of incorrect guesses:", value=st.session_state['number of guesses'] - st.session_state['correct guesses'])

# Number of games played
st.metric(label="Number of games won:", value=st.session_state['correct guesses'])

# Average number of guesses per game
st.metric(label="Average number of guesses per game:", value=(st.session_state['number of guesses'] / st.session_state['correct guesses']))

# Construct guesses per game from history
st.markdown("""

Wow, so quick! Below you can see the amount of guesses for each round:

""")

n_guess_per_game = []
for i in range(1, st.session_state['round number']):
    n_guess_per_game.append(st.session_state.game_history['round number'].value_counts().get(i, 0))
df = pd.DataFrame(n_guess_per_game)
df.index = range(1, len(df) + 1)

st.bar_chart(df, x_label= "Round", y_label="Number of guesses")

st.markdown("""

Your favourite animal guesses from all rounds are:

""")

# TODO: change guessed animal to user_input.lower()
count = Counter(st.session_state.game_history['guessed animal'].str.lower())
st.bar_chart(count)
