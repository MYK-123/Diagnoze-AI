#!/bin/env python3

from operator import index
from numpy import log
import streamlit as st
from auth.login import login
import core



st.set_page_config(
    page_title="Diagnoze AI - Home",
    page_icon="🏠",
    layout="wide",
)


def page1():
    st.write("Welcome to the Diagnoze AI application!")
    st.write("Use the sidebar to navigate through different sections.")
    st.write("This application helps in diagnosing medical conditions using AI.")

    if st.button("Go to Login Page"):
        st.session_state['page'] = 'Direct Login'
        st.switch_page(st.Page(login))
    

def page2():
    st.write("## About Diagnoze AI")
    st.write("Diagnoze AI is an innovative platform that leverages artificial intelligence to assist healthcare professionals in diagnosing medical conditions more accurately and efficiently.")
    st.write("Our mission is to enhance patient care through cutting-edge technology.")
    st.write("### Features:")
    st.write("- AI-powered diagnostic tools")
    st.write("- User-friendly interface")
    st.write("- Secure data handling")
    st.write("### Team Members:")
    st.write("- Alice Smith - Lead Developer")
    st.write("- Bob Johnson - Data Scientist")
    st.write("- Carol Williams - UX Designer")

def add_chat(text:str , by:str = "human"):
    chat_container = st.container(border=True, width="stretch", height="stretch")
    with chat_container.chat_message(by):
        chat_container.write(text)
    return chat_container

def chat_page():
    st.title("Chat Page")
    with st.container(border=True, width="stretch", height="stretch"):
        add_chat("tttsa")
        imp = st.chat_input()
        if imp is not None:
            add_chat(imp)
    
    

pg = st.navigation([
    st.Page(chat_page, title="Main Chat Page"),
    st.Page(page1, title="DSAHDJ"),
    st.Page(page2, title="HHH"),
    st.Page(login, title="Direct Login"),
    st.Page("about.py", title="About"),
], position="hidden")
pg.run()

