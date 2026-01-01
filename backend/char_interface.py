#!/bin/env python3

import streamlit as st
import time

def chat_interface():
    # Page Config
    st.set_page_config(page_title="Chat App", layout="wide")


    # Custom CSS for chat styling
    st.markdown("""
            <style>
                /* Main Chat window */
                .chat-container {
                    max-width: 800px;
                    margin: 0 auto;
                    padding: 20px;
                }

                /* User Message Bubble */
                .user-message {
                    background-color: #007AFF;
                    color: white;
                    border-radius: 18px 18px 4px 18px;
                    padding: 12px 16px;
                    margin: 8px 0;
                    max-width: 70%;
                    margin-left: auto;
                    word-wrap: break-work;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                }

                /* Assistant Message Bubble */
                .assistant-message {
                    background-color: #F0F0F0;
                    color: #333;
                    border-radius: 18px 18px 18px 4px;
                    padding: 12px 16px;
                    margin: 8px 0;
                    max-width: 70%;
                    word-wrap: break-work;
                    box-shadow: 0 2px 4px rgba(0,0,0,0.5);
                }

                /* Timestamp */
                .timestamp {
                    font-size: 0.8em;
                    color: #666;
                    margin-top: 4px;
                }

                /* Message Container */
                .message-container {
                    display: flex;
                    flex-direction: coloumn;
                }

            </style>
                """, unsafe_allow_html=True)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "input_key" not in st.session_state:
        st.session_state.input_key = 0

    st.title("Chat Interface")
    st.markdown("---")

    col1, col2 = st.columns([3, 1])

    with col1:
        chat_container = st.container(height=500, border=True)
        
        with chat_container:
            for message in st.session_state.messages:
                if message["role"] == "user":
                    st.markdown(f"""
                        <div class="message-container">
                                <div class="user-message">
                                    <strong>You</strong>
                                    {message["content"]}
                                    <div class="timestamp">{message.get("time", "")}</div>
                                </div>
                        </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                        <div class="message-container">
                                <div class="assistant-message">
                                    <strong>Assistant</strong>
                                    {message["content"]}
                                    <div class="timestamp">{message.get("time", "")}</div>
                                </div>
                        </div>
                    """, unsafe_allow_html=True)

    with col2:
        st.header("Controls")

        if st.button("Clear Chat", use_container_width=True):
            st.session_state.messages = []
            st.session_state.input_key += 1
            st.rerun()
        
        st.markdown("---")
        st.subheader("Settings")

        persona = st.selectbox(
            "Assistant Persona",
            ["General Assistant", "Tutor", "Professional", "Friendly"]
        )

        st.markdown("---")
        st.subheader("Stats")
        st.write(f"Messages: {len(st.session_state.messages)}")
        st.write(f"User: {len([m for m in st.session_state.messages if m['role'] == 'user'])}")
        st.write(f"Assistant: {len([m for m in st.session_state.messages if m['role'] == 'assistant'])}")

    st.markdown("---")
    chat_input = st.chat_input("Type your message here...", key=f"input_{st.session_state.input_key}")
    if chat_input:
        current_time = time.strftime("%H:%M:%S")
        st.session_state.messages.append({
            "role": "user",
            "content": chat_input,
            "time": current_time
        })
        st.rerun()

        with st.spinner("Thinking..."):
            time.sleep(2.0)

            responses = {
                "hello": "Hello There",
                "bye": "Bye Bye"
            }

            assistant_response = responses.get(chat_input.lower(), 
                    f"received your message: {chat_input}. This is simulated response. from assistans as {persona}")
            
            current_time = time.strftime("%H:%M:%S")
            st.session_state.messages.append({
                "role": "assistant",
                "content": assistant_response,
                "time": current_time
            })
        st.rerun()

