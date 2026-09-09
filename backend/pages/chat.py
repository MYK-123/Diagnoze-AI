import streamlit as st
import content
from utils.api_connect import get_api_client
from datetime import datetime
import time
import json
from pathlib import Path


def _load_stylesheet():
    """Load backend/styles.css and inject into the Streamlit page."""
    try:
        css_path = Path(__file__).resolve().parent.parent / "styles.css"
        if css_path.exists():
            css = css_path.read_text(encoding="utf-8")
            st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    except Exception:
        # Fail silently if stylesheet can't be loaded
        pass


def render_chat_page(router):
    """Main chat interface page - ONLY CHAT PAGE"""
    # Inject custom stylesheet
    _load_stylesheet()
    
    # Page header
    col1, col2, col3 = st.columns([1, 2, 1])
    with col1:
        st.markdown("### 🏥 Diagnoze AI")
    with col2:
        st.markdown("##### 💬 Symptom Analysis Chat")
    with col3:
        col3a, col3b, col3c = st.columns(3)
        with col3a:
            if st.button("🏠", help="Go to Dashboard"):
                router.redirect(*router.build("dashboard"))
        with col3b:
            if st.button("💾", help="Save Chat"):
                save_current_chat()
        with col3c:
            if st.button("🆕", help="Start New Chat"):
                start_new_chat()
    
    # Safety disclaimer
    st.warning("""
    ⚠️ **IMPORTANT**: This is an educational tool, not a diagnostic tool. 
    Always consult a healthcare professional for medical advice. 
    If you have emergency symptoms (chest pain, difficulty breathing, severe bleeding), 
    call emergency services immediately.
    """)
    
    # Initialize chat session
    if "chat_session_id" not in st.session_state:
        start_new_chat()
    
    # Chat container
    chat_container = st.container(height=500, border=True)
    
    with chat_container:
        # Display chat messages
        if "chat_messages" in st.session_state:
            for message_index, message in enumerate(st.session_state.chat_messages):
                display_message(message, message_index)
    
    # Input area
    st.markdown("---")
    user_input = st.chat_input("Describe your symptoms or ask a question...")
    
    if user_input:
        process_user_input(user_input)

# Chat session management
def start_new_chat():
    """Start a new chat session"""
    api = get_api_client()
    response = api.start_chat_session()
    
    if response.get("success"):
        st.session_state.chat_session_id = response["data"]["session_id"]
        st.session_state.chat_messages = [
            {
                "role": "assistant",
                "content": response["data"]["message"],
                "timestamp": datetime.now().strftime("%H:%M"),
                "type": "welcome"
            }
        ]
        st.session_state.chat_state = "awaiting_input"
        st.session_state.collected_symptoms = []
        st.rerun()
    else:
        st.error("Failed to start chat session")

def save_current_chat():
    """Save current chat to history"""
    if "chat_session_id" not in st.session_state:
        st.warning("No active chat to save")
        return
    
    api = get_api_client()
    
    # Get title from user
    col1, col2 = st.columns([3, 1])
    with col1:
        title = st.text_input("Chat title (optional):", "")
    with col2:
        if st.button("Save"):
            response = api.save_chat_session(st.session_state.chat_session_id, title)
            st.write(f"TYPE: {type(response)}")
            st.write(f"DATA: {response}")
            if response.get("success"):
                st.success("Chat saved to history!")
                st.session_state.chat_session_id = None
                st.rerun()
            else:
                st.error("Failed to save chat")

# Message display
def display_message(message, message_index):
    """Display a chat message (rendered inside a bubble)."""
    role = message.get("role", "assistant")
    timestamp = message.get("timestamp", "")
    content = message.get("content", "")

    # Use Streamlit's chat message wrapper but render our own bubble HTML inside so CSS in styles.css can style it.
    with st.chat_message(role):
        st.markdown(
            f'<div class="chat-row {role}">'
            f'<div class="bubble {role}">{content}</div>'
            f'</div>',
            unsafe_allow_html=True)
        st.caption(timestamp)

    # Handle special message types
    if message.get("type") == "prediction":
        display_predictions(message.get("predictions", []), message_index)
    elif message.get("type") == "question":
        display_question(message.get("question", {}))
    elif message.get("type") == "emergency":
        display_emergency_warning(message.get("warning", {}))

def display_predictions(predictions, message_index):
    """Display disease predictions as cards using core data"""
    for pred in predictions:
        with st.container(border=True):
            col1, col2 = st.columns([3, 1])
            with col1:
                severity_emoji = "🔴" if pred['severity'].lower() == 'high' else "🟡" if pred['severity'].lower() == 'medium' else "🟢"
                st.markdown(f"### 🏥 {pred['name']}")
                st.write(f"**Category:** {pred.get('category', 'N/A')}")
                st.write(f"**Severity:** {severity_emoji} {pred['severity']}")
                st.write(f"**Matching symptoms:** {', '.join(pred.get('matching_symptoms', []))}")
            with col2:
                st.metric("Confidence", f"{pred['confidence']}%")
            
            # Confidence bar
            st.progress(pred['confidence'] / 100)
            
            # Action buttons
            col1, col2, col3 = st.columns(3)
            with col1:
                if st.button("📋 Details", key=f"explain_{message_index}_{pred['id']}"):
                    show_disease_explanation(pred)
            with col2:
                if st.button("📚 Learn", key=f"learn_{message_index}_{pred['id']}"):
                    show_educational_content(pred['id'])
            with col3:
                if st.button("➕ Add Symptom", key=f"add_{message_index}_{pred['id']}"):
                    st.session_state.show_add_symptom = True
            
            # Emergency warning if applicable
            if pred.get("emergency", False):
                st.error("⚠️ **URGENT**: This condition may require immediate medical attention!")

def display_question(question):
    """Display a question with quick reply options"""
    st.markdown("---")
    st.write(question.get("text", ""))

def display_emergency_warning(warning):
    """Display emergency warning"""
    st.error(f"""
    ⚠️ **EMERGENCY WARNING** ⚠️
    
    {warning.get('message', 'Based on your symptoms, you may need immediate medical attention.')}
    
    **Recommended Action:** {warning.get('action', 'Call emergency services or go to the nearest hospital.')}
    
    **Emergency Numbers:**
    - Medical Emergency: 108
    - Ambulance: 102
    - National Emergency: 112
    """)

# User input processing
def process_user_input(text):
    """Process user input and get AI response"""
    # Add user message
    st.session_state.chat_messages.append({
        "role": "user",
        "content": text,
        "timestamp": datetime.now().strftime("%H:%M"),
        "type": "text"
    })
    
    # Get AI response
    with st.spinner("Analyzing symptoms..."):
        api = get_api_client()
        response = api.send_chat_message(
            session_id=st.session_state.chat_session_id,
            message=text,
            symptoms=st.session_state.get("collected_symptoms", [])
        )
        
        if response.get("success"):
            ai_data = response["data"]
            
            # Update collected symptoms
            if "symptoms" in ai_data:
                st.session_state.collected_symptoms = list(set(
                    st.session_state.get("collected_symptoms", []) + ai_data["symptoms"]
                ))
            
            # Add AI response
            ai_message = {
                "role": "assistant",
                "content": ai_data.get("response", ""),
                "timestamp": datetime.now().strftime("%H:%M"),
                "type": "text"
            }
            
            # Add prediction if available
            if "predictions" in ai_data:
                ai_message["type"] = "prediction"
                ai_message["predictions"] = ai_data["predictions"]
            
            # Add question if available
            if "question" in ai_data:
                ai_message["type"] = "question"
                ai_message["question"] = ai_data["question"]
            
            # Add emergency warning if needed
            if ai_data.get("emergency"):
                ai_message["type"] = "emergency"
                ai_message["warning"] = ai_data["emergency"]
            
            st.session_state.chat_messages.append(ai_message)
            
            # Update chat state
            st.session_state.chat_state = ai_data.get("next_state", "awaiting_input")
        
        else:
            st.session_state.chat_messages.append({
                "role": "assistant",
                "content": "I'm having trouble processing that. Could you please rephrase or provide more details?",
                "timestamp": datetime.now().strftime("%H:%M"),
                "type": "error"
            })
    
    st.rerun()

# Additional features
def show_disease_explanation(disease):
    """Show detailed disease explanation"""
    with st.expander(f"📋 Details: {disease['name']}", expanded=True):
        st.markdown(f"### {disease['name']}")
        st.markdown(f"**ID:** {disease['id']}")
        st.markdown(f"**Category:** {disease['category']}")
        st.markdown(f"**Severity:** {disease['severity']}")
        st.markdown(f"**Confidence:** {disease['confidence']}%")
        
        st.markdown("#### Matching Symptoms")
        for symptom in disease.get("matching_symptoms", []):
            st.write(f"- {symptom}")

def show_educational_content(disease_id):
    """Show educational content for disease from core"""
    with st.expander("📚 Educational Content", expanded=True):
        api = get_api_client()
        response = api.get_educational_content(disease_id)
        
        if response.get("success"):
            data = response["data"]
            
            st.markdown(f"### {data.get('disease_name', 'Disease')}")
            
            for section in data.get("sections", []):
                st.markdown(f"#### {section['title']}")
                st.write(section['content'])
                
                if section.get("verified"):
                    st.info("✓ Verified Content")
        else:
            st.write("Educational content not available.")


