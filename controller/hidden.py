import streamlit as st

def hidden():
    return st.markdown("""
    <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        [data-testid="stToolbar"] {
            display: none;
        }
    </style>
    """, unsafe_allow_html=True)
    
