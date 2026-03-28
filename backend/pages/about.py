import streamlit as st

def render_about_page():
    if st.button("Home"):
        st.experimental_set_query_params(page="dashboard")

    st.title("About Diagnoze AI")

    tab1, tab2, tab3 = st.tabs(["About Us", "Privacy Policy", "Terms of Service"])

    with tab1:
        st.header("Our Mission")
        st.markdown(
            """
            Our mission is to empower individuals with accessible and intelligent health information.
            We believe that understanding your symptoms is the first step towards better health, and we're
            building tools to make that process simpler, faster, and more informative.
            """
        )

        st.header("The Technology")
        st.markdown(
            """
            Diagnoze AI is powered by a sophisticated stack of modern technologies:
            - **Backend API:** Built with FastAPI (Python), providing a robust and fast interface to our core logic.
            - **Frontend:** An interactive web application built with Streamlit (Python).
            - **AI Model:** A custom-trained machine learning model for symptom analysis and prediction.
            - **Database:** SQLite for development and PostgreSQL for production.
            - **Deployment:** Containerized with Docker and deployed on a cloud platform.
            """
        )

        st.header("Contact Us")
        st.markdown(
            """
            For any inquiries, please contact us at:
            - **Email:** contact@diagnoze-ai.com
            - **Address:** P.M.S., Prayagraj, 211016
            """
        )
        st.info("Version: 1.0.0")


    with tab2:
        st.header("Privacy Policy")
        st.markdown(
            """
            **Last Updated:** March 26, 2026

            Your privacy is important to us. It is Diagnoze AI's policy to respect your privacy regarding any information we may collect from you across our website.

            **1. Information We Collect**
            - **Log Data:** We log information about your device and how you use the app, such as IP address, browser type, and pages visited.
            - **Personal Information:** We may ask for personal information, such as your name and email address, when you register for an account.
            - **Health Information:** We collect symptom and health-related information that you voluntarily provide during chat sessions.

            **2. Use of Information**
            The information we collect is used to:
            - Provide, operate, and maintain our service.
            - Improve, personalize, and expand our service.
            - Understand and analyze how you use our service.
            - Develop new products, services, features, and functionality.
            - Communicate with you for customer service, to provide you with updates and other information relating to the website, and for marketing purposes.
            - For research and analysis, in an aggregated and anonymized form.

            **3. Data Security**
            We use industry-standard security measures to protect your information. However, no method of transmission over the internet is 100% secure.
            """
        )

    with tab3:
        st.header("Terms of Service")
        st.markdown(
            """
            **Last Updated:** March 26, 2026

            By accessing this website, you are agreeing to be bound by these terms of service, all applicable laws and regulations, and agree that you are responsible for compliance with any applicable local laws.

            **1. Use License**
            Permission is granted to temporarily download one copy of the materials on Diagnoze AI's website for personal, non-commercial transitory viewing only.

            **2. Disclaimer**
            The materials on Diagnoze AI's website are provided on an 'as is' basis. Diagnoze AI makes no warranties, expressed or implied, and hereby disclaims and negates all other warranties including, without limitation, implied warranties or conditions of merchantability, fitness for a particular purpose, or non-infringement of intellectual property or other violation of rights.

            **3. Limitations**
            In no event shall Diagnoze AI or its suppliers be liable for any damages (including, without limitation, damages for loss of data or profit, or due to business interruption) arising out of the use or inability to use the materials on Diagnoze AI's website.

            **4. Governing Law**
            These terms and conditions are governed by and construed in accordance with the laws of California and you irrevocably submit to the exclusive jurisdiction of the courts in that State or location.
            """
        )

def render_page():
    return render_about_page()

if __name__ == "__main__":
    render_page()
