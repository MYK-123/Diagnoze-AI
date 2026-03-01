import streamlit as st
import pandas as pd
from streamlit_router import StreamlitRouter

def render_contact_page():
    """P34 - Contact Us"""
    st.title("📞 Contact Us")

    st.subheader("Get in Touch")
    st.write("Have questions or feedback? We'd love to hear from you.")

    with st.form("contact_form"):
        name = st.text_input("Your Name*")
        email = st.text_input("Your Email*")
        message = st.text_area("Message*", height=200)
        submitted = st.form_submit_button("Send Message")
        if submitted:
            if not name or not email or not message:
                st.warning("Please fill out all required fields.")
            else:
                # In a real app, this would send an email or save to a database.
                # api.submit_contact_form(name=name, email=email, message=message)
                st.success("Thank you for your message! We will get back to you shortly.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Our Office")
        st.write("123 Health Tech Ave, Suite 100")
        st.write("MedCity, MC 54321")
        # Provide mock data for the map
        mock_data = pd.DataFrame({
            'latitude': [37.7749],
            'longitude': [-122.4194]
        })
        st.map(mock_data)

    with col2:
        st.subheader("Support Hours")
        st.write("**Monday - Friday:** 9:00 AM - 5:00 PM (UTC)")
        st.write("**Email:** support@diagnoze.ai")
        st.write("**Phone:** +1 (555) 123-4567")

    if st.button("Home"):
        st.experimental_set_query_params(page="dashboard")

def render_research_page():
    """P35 - Research References"""
    st.title("🔬 Research & References")
    
    st.header("Medical Sources & Bibliography")
    st.write("Our AI model is trained on a wide variety of public medical data and literature. Key sources include:")
    st.markdown("""
        - Public health datasets (e.g., from WHO, CDC)
        - Anonymized clinical trial data
        - Medical textbooks and journals
        - Reputable online health encyclopedias
    """)

    st.header("Dataset Citations")
    st.code("Citation for Dataset X, (2023), MedLink Repository.")
    st.code("Citation for Dataset Y, (2022), HealthData.gov.")

    st.header("API Documentation")
    st.write("For developers interested in using our API, please refer to our full documentation.")
    st.page_link("https://api.diagnoze.ai/docs", label="View API Docs")

def render_demo_page():
    """P36 - Demo Page"""
    st.title("🚀 Live Demo")
    st.write("Experience a limited-functionality demonstration of the Diagnoze AI symptom checker.")

    st.info("This is a mock chat. The responses are pre-defined and do not use the live AI model.")

    # Mock chat interface
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "Hello! I'm a demo assistant. Tell me a symptom like 'headache'."}]

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("Describe a symptom..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            response = "This is a pre-canned response for the demo. In the full version, an AI would analyze this symptom. Would you like to know more?"
            st.markdown(response)
        st.session_state.messages.append({"role": "assistant", "content": response})

    st.subheader("Ready for the full experience?")
    st.write("Sign up for a free account to get personalized insights, track your symptoms, and more.")
    if st.button("Sign Up Now"):
        st.switch_page("pages/auth.py")

def register_routes(router: StreamlitRouter):
    router.map("/public/contact", methods=["GET"])(render_contact_page)
    router.map("/public/research", methods=["GET"])(render_research_page)
    router.map("/public/demo", methods=["GET"])(render_demo_page)

if __name__ == "__main__":
    router = StreamlitRouter()
    register_routes(router)
    router.serve()
