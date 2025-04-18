import streamlit as st
from main import ConcertTourManager
import os
import warnings

# Suppress warnings in CLI
warnings.filterwarnings("ignore")
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

# Initialize session state
if 'manager' not in st.session_state:
    st.session_state.manager = ConcertTourManager()
if 'conversation' not in st.session_state:
    st.session_state.conversation = []

# UI Configuration
st.set_page_config(page_title="🎵 Concert Tour Assistant")
st.title("🎵 Concert Tour Assistant")

col1, col2 = st.columns(2)
with col1:
    if st.button("Clear", use_container_width=True):
        st.session_state.conversation = []
        st.rerun()
with col2:
    if st.button("Exit", use_container_width=True):
        st.warning("Please close this browser tab to exit")
        st.stop()

# Chat interface
for speaker, message in st.session_state.conversation:
    if speaker == "You":
        with st.chat_message("user"):
            st.write(message)
    else:
        with st.chat_message("assistant"):
            st.write(message)

# Chat input
user_input = st.chat_input("Ask about concerts or type 'exit' to quit...")
if user_input:
    if user_input.strip().lower() == 'exit':
        st.warning("Please close this browser tab to exit")
        st.stop()
    st.session_state.conversation.append(("You", user_input))
    response = st.session_state.manager.handle_input(user_input)
    st.session_state.conversation.append(("System", response))
    st.rerun()