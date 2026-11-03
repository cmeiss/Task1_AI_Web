import streamlit as st

page1 = st.Page("game.py", title="Let's Guess", icon="🤔")
page2 = st.Page("statistics.py", title="Game Statistics", icon="📈")



pg = st.navigation(pages=[page1, page2])
pg.run()
