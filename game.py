import streamlit as st
from constants import *
import numpy as np
import pandas as pd
from openai import OpenAI, AuthenticationError, OpenAIError

# TODO: Save API key somehow?

# TODO: possibly state for game won?
# TODO: alternate spellings
# TODO: what to do with nonsense input

# TODO: clear field when guess is correct? (or in general and print in answer?)
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

## ── Actual game code starts here ──────────────────────────────────────────── ##
#Initialize session state variables if they don't exist yet:
if 'n_guess' not in st.session_state:
    st.session_state['n_guess'] = 0

if 'correct_guesses' not in st.session_state:
    st.session_state['correct_guesses'] = 0

#game history dataframe to build the memory for the LLM + use for evaluation page
if 'game_history' not in st.session_state:
    st.session_state.game_history = pd.DataFrame(
        columns = [
            "round_idx",
            "guessed_animal",
            "correct_animal",
            "AI_hint"
        ]
    )

#choose a random animal from the list for now
if 'target_animal' not in st.session_state:
    st.session_state['target_animal'] = np.random.choice(ANIMALS)

if 'target_stats' not in st.session_state:
    st.session_state['target_stats'] = []

if 'round_idx' not in st.session_state:
    st.session_state['round_idx'] = 1

if 'evaluation_scores' not in st.session_state:
    st.session_state['evaluation_scores'] = dict()

## ── Actual page code starts here ──────────────────────────────────────────── ##
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
    st.session_state['n_guess'] += 1   #keep track of number of guesses

    #check if the guess is correct, if yes, congratulate, update statistics
    if user_input.lower() == st.session_state['target_animal']:
        st.success(f"Congratulations! You guessed the correct animal: {st.session_state['target_animal']}!")
        st.session_state['correct_guesses'] += 1  #keep track of number of correct guesses
        st.session_state['target_stats'].append(st.session_state['target_animal']) # keep track of chosen true animals

    #if user is wrong, let them know and let the LLM provide a hint (while keeping track of previous hints)
    else:
        AI_prompt = f"""You are a hint-provider in an animal guessing game. 
        The user guessed the following animal: {user_input}. 
        The correct animal is: {st.session_state['target_animal']}. 
        Please provide a one sentence hint to help the user guess the right animal. 
        Do not use complicated/scientific vocabulary so users can easily understand your hints. 
        Do not repeat hints that you already gave in this round. 
        Here are the previous hints you have given in this round: {st.session_state['game_history'][st.session_state['game_history']['round_idx'] == st.session_state['round_idx']]['AI_hint'].tolist()}. 
        Please provide a new hint that is not in the list of previous hints."""
        print(AI_prompt)
        st.error(f"Sorry, that's not correct. We'll give you a hint and you can try again!")
        try:
            with st.spinner("Hint is being generated …"):
                response = client.chat.completions.create(
                    model="google/gemma-4-E4B-it",
                    messages=[
                        {"role": "user", "content": AI_prompt},
                    ],
                )
            hint = response.choices[0].message.content
            st.write(hint)

        except AuthenticationError:
            st.error("API was not accepted. Please check it.")

        except OpenAIError:
            st.error(
                "AI API request failed. Please check it and try again. "
            )

    #update game history dataframe
    st.session_state.game_history = pd.concat(
        [
            st.session_state.game_history,
            pd.DataFrame(
                {
                    "round_idx": [st.session_state['round_idx']],
                    "guessed_animal": [user_input.lower()],
                    "correct_animal": [st.session_state['target_animal']],
                    "AI_hint": [hint],
                }
            ),
        ],
        ignore_index=True,  #needed to clean indices during concatination and avoid duplicate indices
    )

    # after updating game history, evaluate guess and pick new animal
    if user_input.lower() == st.session_state['target_animal']:
        # use LLM to evaluate user input
        # TODO: fix evaluation procedure
        # e.g.: guess 1 hint 1 array or provide example
        # OR embed guess and true animal, calculate cosine difference
        API_eval_prompt = f"""You are an evaluator of user guesses in an animal guessing game. 
        The correct animal was: {st.session_state['target_animal']}. 
        The user starts with a guess and if it is incorrect they gets a hint. 
        The user's guesses, in order, were:  {st.session_state['game_history'][st.session_state['game_history']['round_idx'] == st.session_state['round_idx']]['guessed_animal'].tolist()}. 
        The provided hints, in order, were:  {st.session_state['game_history'][st.session_state['game_history']['round_idx'] == st.session_state['round_idx']]['AI_hint'].tolist()}. 
        After this final hint, they now correctly identified the animal. For each guess, look at previous hints to see if the guessed animal fulfills the mentioned qualities. 
        Please evaluate the user's overall adherence to the hints on a scale of 1 (strong adherence) to 5 (no adherence). Please only answer with a single integer."""
        print(API_eval_prompt)
        try:
            with st.spinner("Want to know how well you did? We are evaluating the quality of your guesses …"):
                response = client.chat.completions.create(
                    model="google/gemma-4-E4B-it",
                    messages=[
                        {"role": "user", "content": API_eval_prompt},
                    ],
                )

            st.write(f"On a scale from 1 (strong adherence) to 5 (no adherence), you scored: {response.choices[0].message.content}")
            st.session_state['evaluation_scores'].update({st.session_state['round_idx']: (int(response.choices[0].message.content))})
            print(st.session_state['evaluation_scores'])

        except AuthenticationError:
            st.error("API was not accept. Please check it.")

        except OpenAIError:
            st.error(
                "AI API request failed. Please check it and try again. "
            )   

        # update variables for next round
        st.session_state['round_idx'] += 1  #increment round number
        st.session_state['target_animal'] = np.random.choice(ANIMALS)  #choose new animal from list, replace with LLM later (write funciton for this?)

#button to go to statistics page
if st.button("Go to Statistics"):
    st.switch_page("statistics.py")
