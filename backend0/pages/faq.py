
import streamlit as st

def render_faq_page():
    """
    Renders the FAQ / Help Center page (P15).
    Provides answers to frequently asked questions and offers support options.
    """
    st.set_page_config(page_title="FAQ & Help Center", layout="wide")
    st.title("🙋‍♂️ FAQ & Help Center")

    # --- Search Bar ---
    st.text_input("Search for a question...", key="faq_search")

    # --- Categorized Questions ---
    categories = {
        "Getting Started": {
            "What is Diagnoze AI?": "Diagnoze AI is an educational tool to help you understand medical symptoms and conditions. It is not a diagnostic tool and should not replace professional medical advice.",
            "How do I create an account?": "You can create an account by clicking the 'Sign Up' button on the login page and filling out the required information.",
            "Is Diagnoze AI free?": "Yes, the basic features of Diagnoze AI are free to use for educational purposes.",
        },
        "Using the Symptom Checker": {
            "How does the symptom checker work?": "Our AI analyzes the symptoms you provide and cross-references them with a vast database of medical information to suggest possible related conditions for educational purposes.",
            "What should I do with the results?": "The results are for informational purposes only. You should always consult with a qualified healthcare professional for a real diagnosis.",
            "Can I save my chat history?": "Yes, your chat history is automatically saved to your profile. You can review it at any time from the 'History' page.",
        },
        "Account & Profile": {
            "How do I change my password?": "You can change your password from the 'Profile' page. You will be asked to enter your old password and a new one.",
            "How is my data protected?": "We take data privacy seriously. All personal data is encrypted, and symptom information is anonymized. Please see our Privacy Policy for more details.",
            "How can I delete my account?": "To delete your account, please go to your Profile page and find the 'Delete Account' section. Please be aware that this action is irreversible."
        }
    }

    for category, questions in categories.items():
        st.header(category)
        for question, answer in questions.items():
            with st.expander(question):
                st.write(answer)
    
    st.markdown("---")

    # --- Video Tutorials (Placeholders) ---
    st.header("🎥 Video Tutorials")
    st.info("Video tutorials are coming soon!")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("How to Use the Symptom Checker")
        st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ") # Placeholder video
    with col2:
        st.subheader("Understanding Your Dashboard")
        st.video("https://www.youtube.com/watch?v=dQw4w9WgXcQ") # Placeholder video

    st.markdown("---")

    # --- Contact and Feedback ---
    st.header("Still Need Help?")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("✉️ Contact Support")
        st.write("If you can't find the answer you're looking for, feel free to contact our support team.")
        if st.button("Contact Us"):
            st.switch_page("pages/public.py") # Assume public page has contact form

    with col2:
        st.subheader("📝 Give Feedback")
        st.write("Have suggestions to improve our app? We'd love to hear from you!")
        with st.form("feedback_form"):
            feedback = st.text_area("Your Feedback")
            submitted = st.form_submit_button("Submit Feedback")
            if submitted:
                st.success("Thank you for your feedback!")
                # In a real app, this would send an email or save to a database.

if __name__ == "__main__":
    render_faq_page()
