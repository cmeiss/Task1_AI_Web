import streamlit as st
import pandas as pd
from collections import Counter
import matplotlib.pyplot as plt

st.header("Game Statistics")

# Number of games played
st.metric(label="Number of games won:", value=st.session_state['correct_guesses'])

st.text("") #create whitespace between metrics

# Create eval dataframe
eval_df = pd.DataFrame(
    columns = [
        "n_rounds",
        "hint_adherence",
        "n_guesses",
        "eval_score"
    ]
)

total_hint_ad = 0
for round, hint_ad in st.session_state['evaluation_scores'].items():
    n_guesses = int(st.session_state.game_history['round_idx'].value_counts().get(round, 0))
    total_hint_ad += hint_ad
    eval_df = pd.concat(
        [
            eval_df,
            pd.DataFrame(
                {
                    "n_rounds": round,
                    "hint_adherence": hint_ad,
                    "n_guesses": n_guesses,
                    "eval_score": 0.5*hint_ad + 0.5*n_guesses
                },
                index =[0]
            ),
        ],
        ignore_index=True,  #needed to clean indices during concatination and avoid duplicate indices
    )
eval_df = eval_df.set_index("n_rounds")

# Number of guesses per game and on average (rounded to two decimal points) 
st.markdown("""

Wow, so quick! Below you can see the amount of guesses for each round ...

""")

st.text("") #create whitespace between metrics

if st.session_state['correct_guesses'] > 0:
    st.metric(label="Average number of guesses per game:", value= f"{(st.session_state['n_guess'] / st.session_state['correct_guesses']):.2f}")
else:
    st.metric(label="Average number of guesses per game:", value= "N/A")

st.text("") #create whitespace between metrics

st.bar_chart(eval_df.drop(["hint_adherence", "eval_score"], axis=1), x_label= "Round", y_label="Number of guesses")

# Hint adherence per game and on average (rounded to two decimal points)
st.markdown("""

... and how well you adhered to the given hints:

""")

st.text("") #create whitespace between metrics

if st.session_state['correct_guesses'] > 0:
    st.metric(label="Average hint adherence:", value= f"{(total_hint_ad / st.session_state['correct_guesses']):.2f}")
else:
    st.metric(label="Average hint adherence:", value= "N/A")

st.text("") #create whitespace between metrics

# Bar chart showing the evaluation score for each round
st.bar_chart(eval_df.drop(["n_guesses", "eval_score"], axis=1), x_label= "Round", y_label="Hint adherence score (1 to 5)", color = "red")

st.text("") #create whitespace between metrics

st.markdown("""

Your guesses are evaluated based on amount of guesses needed, and adherence to hints. The lower the score, the better:

""")


st.text("") #create whitespace between metrics

# Bar chart showing hint adherence score for each round
st.bar_chart(eval_df.drop(["n_guesses", "hint_adherence"], axis=1), x_label= "Round", y_label="Score", color = "violet")


st.text("") #create whitespace between metrics

#Pie Chart showing the distribution of guessed animals across all rounds
st.markdown("""

Your favourite animal guesses from all rounds are:

""")

st.text("") #create whitespace between metrics

count = Counter(st.session_state.game_history['guessed_animal'].str.lower())

if len(count) == 0:
    st.write("No guesses made yet.")
else:
    fig, ax = plt.subplots()
    ax.pie(count.values(), labels=count.keys(), autopct='%1.1f%%', startangle=90)
    ax.axis('equal')  # to make round

    st.pyplot(fig)

