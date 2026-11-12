import streamlit as st
import pandas as pd
from collections import Counter

#very basic statistics page, just showing number of incorrect guesses vs. number of total guesses

st.header("Game Statistics")

# st.metric(label="Number of incorrect guesses:", value=st.session_state['n_guess'] - st.session_state['correct_guesses'])

# Number of games played
st.metric(label="Number of games won:", value=st.session_state['correct_guesses'])

# Average number of guesses per game
# TODO: figure out how to round that
st.metric(label="Average number of guesses per game:", value=(st.session_state['n_guess'] / st.session_state['correct_guesses']))

# Create eval dataframe
eval_df = pd.DataFrame(
    columns = [
        "n_rounds",
        "hint_adherence",
        "n_guesses",
        "eval_score"
    ]
)
for round, hint_ad in st.session_state['evaluation_scores'].items():
#for i in range(1, st.session_state['round_idx']):
    n_guesses = int(st.session_state.game_history['round_idx'].value_counts().get(round, 0))
    # print(f"Eval score = {hint_ad} * {n_guesses} = {hint_ad * n_guesses}")
    # print(f"Hint ad tyoe = {type(hint_ad)}")
    # eval_score = int(hint_ad * n_guesses)
    eval_df = pd.concat(
        [
            eval_df,
            pd.DataFrame(
                {
                    "n_rounds": round,
                    "hint_adherence": hint_ad,
                    "n_guesses": n_guesses,
                    "eval_score": hint_ad * n_guesses
                },
                index =[0]
            ),
        ],
        ignore_index=True,  #needed to clean indices during concatination and avoid duplicate indices
    )
eval_df = eval_df.set_index("n_rounds")

# Construct guesses per game from history
st.markdown("""

Wow, so quick! Below you can see the amount of guesses for each round ...

""")

st.bar_chart(eval_df.drop(["hint_adherence", "eval_score"], axis=1), x_label= "Round", y_label="Number of guesses")

#Old version of that
# n_guess_per_game = []
# for i in range(1, st.session_state['round_idx']):
#     n_guess_per_game.append(st.session_state.game_history['round_idx'].value_counts().get(i, 0))
# df = pd.DataFrame(n_guess_per_game)
# df.index = range(1, len(df) + 1)
# st.bar_chart(df, x_label= "Round", y_label="Number of guesses")

st.markdown("""

... and how well you adhered to the given hints:

""")

st.bar_chart(eval_df.drop(["n_guesses", "eval_score"], axis=1), x_label= "Round", y_label="Hint adherence score (1 to 7)", color = "red")

# TODO: represent estimated guessing quality in interesting and transparent way to user
st.markdown("""

Your guesses are evaluated based on amount of guesses needed, and adherence to hints. The lower the score, the better:

""")

st.bar_chart(eval_df.drop(["n_guesses", "hint_adherence"], axis=1), x_label= "Round", y_label="Score", color = "violet")


st.markdown("""

Your favourite animal guesses from all rounds are:

""")

# TODO: change guessed animal to user_input.lower()
count = Counter(st.session_state.game_history['guessed_animal'].str.lower())
st.bar_chart(count, color="orange")

