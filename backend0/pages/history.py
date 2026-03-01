import streamlit as st
from utils.api_connect import get_api_client
import pandas as pd
from datetime import datetime
import json

def render_history_page(router):
    """Chat history page"""
    st.title("📋 Chat History")
    
    # Get history from API
    api = get_api_client()
    response = api.get_chat_history()
    
    if not response.get("success"):
        st.error("Unable to load chat history")
        return
    
    chats = response.get("data", {}).get("chats", [])
    
    # Search and filter
    col1, col2, col3 = st.columns(3)
    with col1:
        search_term = st.text_input("Search chats...")
    with col2:
        date_filter = st.selectbox("Filter by date", ["All time", "Last week", "Last month", "Last 3 months"])
    with col3:
        disease_filter = st.selectbox("Filter by disease", ["All diseases", "Migraine", "Viral Infection", "Allergy", "Sinusitis"])
    
    # Filter chats
    filtered_chats = chats
    if search_term:
        filtered_chats = [c for c in filtered_chats if search_term.lower() in c.get("title", "").lower()]
    
    # Display chats
    if not filtered_chats:
        st.info("No chat history found. Start your first chat!")
        if st.button("Start New Chat"):
            router.redirect(*router.build("chat"))
        return
    
    # Display as cards
    for chat in filtered_chats:
        with st.container(border=True):
            col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
            
            with col1:
                st.write(f"### {chat.get('title', 'Untitled Chat')}")
                st.caption(f"{chat.get('date', 'Unknown date')} • {len(chat.get('symptoms', []))} symptoms")
                
                # Display symptoms
                symptoms = chat.get('symptoms', [])
                if symptoms:
                    symptom_text = ", ".join(symptoms[:3])
                    if len(symptoms) > 3:
                        symptom_text += f" +{len(symptoms)-3} more"
                    st.write(f"**Symptoms:** {symptom_text}")
            
            with col2:
                if chat.get('predictions'):
                    top_pred = chat['predictions'][0]
                    st.metric("Top Match", f"{top_pred.get('confidence', 0)}%")
            
            with col3:
                if st.button("View", key=f"view_{chat['id']}"):
                    view_chat_details(chat['id'])
            
            with col4:
                if st.button("Delete", key=f"delete_{chat['id']}"):
                    delete_chat(chat['id'])
    
    # Pagination
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.write(f"Page 1 of {response['data'].get('total_pages', 1)}")
        col_a, col_b, col_c = st.columns(3)
        with col_a:
            if st.button("← Previous"):
                pass  # Load previous page
        with col_b:
            st.write("1")
        with col_c:
            if st.button("Next →"):
                pass  # Load next page

def view_chat_details(chat_id):
    """View detailed chat"""
    api = get_api_client()
    response = api.get_chat_by_id(chat_id)
    
    if response.get("success"):
        chat = response["data"]
        
        with st.expander(f"Chat Details: {chat.get('title')}", expanded=True):
            st.write(f"**Date:** {chat.get('date')}")
            st.write(f"**Duration:** {chat.get('duration', 'N/A')}")
            
            st.write("### Symptoms")
            for symptom in chat.get('symptoms', []):
                st.write(f"- {symptom}")
            
            st.write("### Predictions")
            for pred in chat.get('predictions', []):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**{pred['name']}**")
                    st.write(f"Matching: {', '.join(pred.get('matching_symptoms', []))}")
                with col2:
                    st.metric("Confidence", f"{pred['confidence']}%")
            
            st.write("### Conversation")
            for msg in chat.get('messages', []):
                if msg['role'] == 'user':
                    st.chat_message("user").write(msg['content'])
                else:
                    st.chat_message("assistant").write(msg['content'])
            
            # Export options
            st.download_button(
                "Export as JSON",
                data=json.dumps(chat, indent=2),
                file_name=f"chat_{chat_id}.json",
                mime="application/json"
            )
    else:
        st.error("Unable to load chat details")

def delete_chat(chat_id):
    """Delete a chat"""
    api = get_api_client()
    response = api.delete_chat(chat_id)
    
    if response.get("success"):
        st.success("Chat deleted successfully")
        st.rerun()
    else:
        st.error("Failed to delete chat")

if __name__ == "__main__":
    render_history_page(None)


