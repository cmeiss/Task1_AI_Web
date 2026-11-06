import streamlit as st
import numpy as np
import pandas as pd


#Initialize session state variables if they don't exist yet:
if 'number of guesses' not in st.session_state:
    st.session_state['number of guesses'] = 0

if 'correct guesses' not in st.session_state:
    st.session_state['correct guesses'] = 0

#choose a random animal from the list for now, change this to LLM later
if 'target animal' not in st.session_state:
    st.session_state['target animal'] = np.random.choice(['cat', 'dog', 'elephant', 'giraffe', 'lion', 'tiger', 'bear', 'monkey', 'zebra', 'kangaroo'])

if 'target stats' not in st.session_state:
    st.session_state['target stats'] = []


##Actual page code starts here##
st.header("Let's Guess Animals")

st.markdown("""

Welcome to our Animal Guessing Game!

""")

#ask for a guess from user
prompt = st.text_input("Enter your guess for the animal:")
if prompt:
    st.write(f"You guessed: {prompt}. Let's see if you're right!")
    st.session_state['number of guesses'] += 1   #keep track of number of guesses

#check if the guess is correct and provide feedback
if prompt.lower() == st.session_state['target animal']:
    st.success(f"Congratulations! You guessed the correct animal: {st.session_state['target animal']}!")
    st.session_state['correct guesses'] += 1  #keep track of number of correct guesses
    st.session_state['target stats'].append(st.session_state['target animal']) # keep track of chosen true animals
    st.session_state['target animal'] = np.random.choice(['cat', 'dog', 'elephant', 'giraffe', 'lion', 'tiger', 'bear', 'monkey', 'zebra', 'kangaroo'])  #choose new animal from list, replace with LLM later (write funciton for this?)
else:
    st.error(f"Sorry, that's not correct. Try again!")

#button to go to statistics page
if st.button("Go to Statistics"):
    st.switch_page("statistics.py")
