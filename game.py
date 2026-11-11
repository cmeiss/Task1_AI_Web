import streamlit as st
from constants import *
import numpy as np
import pandas as pd
from openai import OpenAI, AuthenticationError, OpenAIError

st.set_page_config(page_title="Welcome to our Animal Guessing Game!")

# ── ask for API Key, stop if not yet provided  ────────────────────────────────────────────
with st.sidebar:
    api_key = st.text_input(
        "UOS AI API-Key",
        type="password",
        key="uos_api_key",
        placeholder="sk-...",
    ).strip()

if not api_key:
    st.info("Please enter your Uni Osnabrück API key. If you don't have one, you can obtain it from https://ai-keys.uni-osnabrueck.de.")
    st.stop()

# pass the entered key
client = OpenAI(
    base_url="https://litellm.uni-osnabrueck.de/v1",
    api_key=api_key
)

##Actual game code starts here
#Initialize session state variables if they don't exist yet:
if 'number of guesses' not in st.session_state:
    st.session_state['number of guesses'] = 0

if 'correct guesses' not in st.session_state:
    st.session_state['correct guesses'] = 0

#game history dataframe to build the memory for the LLM + use for evaluation page
if 'game_history' not in st.session_state:
    st.session_state.game_history = pd.DataFrame(
        columns = [
            "round number",
            "guessed animal",
            "correct animal",
            "AI hint"
        ]
    )



#choose a random animal from the list for now
if 'target animal' not in st.session_state:
    st.session_state['target animal'] = np.random.choice(ANIMALS)

if 'target stats' not in st.session_state:
    st.session_state['target stats'] = []

if 'round number' not in st.session_state:
    st.session_state['round number'] = 1


##Actual page code starts here##
st.header("Let's Guess Animals")

st.markdown("""

Welcome to our Animal Guessing Game!

""")

#ask for a guess from user
with st.form("guess_form"):
    user_input = st.text_input("Enter your guess for the animal:")
    submitted = st.form_submit_button("Submit Guess")

if submitted:   
    #update number of guesses and clear previous error/congratulation messages
    hint = ""
    st.session_state['number of guesses'] += 1   #keep track of number of guesses


    #check if the guess is correct, if yes, congratulate, update statistics and pick new animal
    if user_input.lower() == st.session_state['target animal']:
        st.success(f"Congratulations! You guessed the correct animal: {st.session_state['target animal']}!")
        st.session_state['correct guesses'] += 1  #keep track of number of correct guesses
        st.session_state['target stats'].append(st.session_state['target animal']) # keep track of chosen true animals
        st.session_state['round number'] += 1  #increment round number
        st.session_state['target animal'] = np.random.choice(ANIMALS)  #choose new animal from list, replace with LLM later (write funciton for this?)
        API_eval_prompt = f"You are an evaluator of user guesses in an animal guessing game. The correct animal was: {st.session_state['target animal']}. The user starts with a guess and if it is incorrect they gets a hint. The user's guesses, in order, were:  {st.session_state['game_history'][st.session_state['game_history']['round number'] == st.session_state['round number']]['guessed animal'].tolist()}. The provided hints, in order, were:  {st.session_state['game_history'][st.session_state['game_history']['round number'] == st.session_state['round number']]['AI hint'].tolist()}. After this final hint, they now correctly identified the animal. Please evaluate the user's adherence to the hints on a scale of 1 (no adherence) to 7 (strong adherence). Please only answer with a single integer."
        try:
            with st.spinner("Your guesses are being evaluated …"):
                response = client.chat.completions.create(
                    model="google/gemma-4-E4B-it",
                    messages=[
                        {"role": "user", "content": API_eval_prompt},
                    ],
                )

            st.write(response.choices[0].message.content)

        except AuthenticationError:
            st.error("API was not accept. Please check it.")

        except OpenAIError:
            st.error(
                "AI API request failed. Please check it and try again. "
            )   
    #if user is wrong, let them know and let the LLM provide a hint (while keeping track of previous hints)
    else:
        AI_prompt = f"You are a hint-provider in an animal guessing game. The user guessed the following animal: {user_input}. The correct animal is: {st.session_state['target animal']}. Please provide a one sentence hint to help the user guess the right animal. Do not use complicated/scientific vocabulary so users can easily understand your hints. Do not repeat hints that you already gave in this round. Here are the previous hints you have given in this round: {st.session_state['game_history'][st.session_state['game_history']['round number'] == st.session_state['round number']]['AI hint'].tolist()}. Please provide a new hint that is not in the list of previous hints."
        print(AI_prompt)
        st.error(f"Sorry, that's not correct. Try again!")
        try:
            with st.spinner("Answer is being created …"):
                response = client.chat.completions.create(
                    model="google/gemma-4-E4B-it",
                    messages=[
                        {"role": "user", "content": AI_prompt},
                    ],
                )
            hint = response.choices[0].message.content
            st.write(hint)

        except AuthenticationError:
            st.error("API was not accept. Please check it.")

        except OpenAIError:
            st.error(
                "AI API request failed. Please check it and try again. "
            )

    # NOTE: moved that up one, I think otherwise it is not updated for winning round?
    #update game history dataframe
    st.session_state.game_history = pd.concat(
        [
            st.session_state.game_history,
            pd.DataFrame(
                {
                    "round number": [st.session_state['round number']],
                    "guessed animal": [user_input],
                    "correct animal": [st.session_state['target animal']],
                    "AI hint": [hint],
                }
            ),
        ],
        ignore_index=True,  #needed to clean indices during concatination and avoid duplicate indices
    )

#button to go to statistics page
if st.button("Go to Statistics"):
    st.switch_page("statistics.py")
