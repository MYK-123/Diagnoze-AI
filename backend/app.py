#!/bin/env python3

import streamlit as st
import streamlit_router as strouter
from auth.login import login
from backend.char_interface import chat_interface

router = strouter.StreamlitRouter()

@router.map("/")
def index(router: strouter.StreamlitRouter):
    st.write("# Welcome to Diagnoze AI")
    st.write("This is the home page of the Diagnoze AI application.")
    st.write("Use the sidebar to navigate to different sections of the app.")
    if st.button("Go to About Page"):
        router.redirect("/about")

@router.map("/about")
def about_page(router: strouter.StreamlitRouter):
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
    from backend import char_interface
    chat_interface()
    
    

pg = st.navigation([
    st.Page(chat_page, title="Main Chat Page"),
    st.Page(page1, title="DSAHDJ"),
    st.Page(page2, title="HHH"),
    st.Page(login, title="Direct Login"),
    st.Page("about.py", title="About"),
], position="hidden")
# pg.run()


router.serve()

