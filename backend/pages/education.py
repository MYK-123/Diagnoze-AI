import streamlit as st
from utils.auth import check_authentication
from utils.api_connect import get_api_client

def render_education_page():
    """
    Renders the Educational Library page (P12).
    Allows browsing diseases and symptoms. Requires authentication.
    """
    st.set_page_config(page_title="Educational Library - Diagnoze AI", layout="wide")

    if not check_authentication():
        st.error("You must be logged in to view this page.")
        st.stop()

    st.title("📚 Educational Library")
    st.write("Browse our library of diseases, symptoms, and educational content.")

    api = get_api_client()

    # Initialize session state for details view
    if 'selected_disease' not in st.session_state:
        st.session_state.selected_disease = None

    # If a disease is selected, show its details
    if st.session_state.selected_disease:
        render_disease_details(st.session_state.selected_disease, api)
        if st.button("⬅️ Back to Library"):
            st.session_state.selected_disease = None
            st.experimental_rerun()
        return

    # Search and filter UI
    col1, col2 = st.columns([3, 1])
    with col1:
        search_query = st.text_input("Search for diseases or symptoms", "")
    with col2:
        category = st.selectbox("Filter by category", ["All", "Neurological", "Infectious", "Cardiovascular", "Respiratory", "Gastrointestinal", "Dermatological"])

    # Fetch and display data
    try:
        if search_query:
            diseases = api.get_diseases(search=search_query)
        else:
            # Filtering logic would be applied here if the API supports it
            # For now, we fetch all and filter client-side as a fallback
            diseases = api.get_diseases()

        if category != "All":
            # This is a placeholder for client-side filtering.
            # Ideally, the API would handle category filtering.
            diseases = [d for d in diseases if d.get('category', 'N/A') == category]

        if not diseases:
            st.info("No diseases found matching your criteria.")
            st.stop()

        # Grid layout for disease cards
        cols = st.columns(3)
        for i, disease in enumerate(diseases):
            with cols[i % 3]:
                with st.container():
                    st.subheader(disease.get("name", "N/A"))
                    st.write(disease.get("description", "No description available.")[:100] + "...")
                    if st.button("Learn More", key=f"disease_{disease.get('id')}"):
                        st.session_state.selected_disease = disease
                        st.experimental_rerun()
    
    except Exception as e:
        st.error(f"Failed to load educational content: {e}")
        st.button("Retry")

def render_disease_details(disease, api):
    """Renders the detailed view for a selected disease."""
    st.header(disease.get("name", "N/A"))
    st.write(disease.get("description", "No description available."))

    try:
        # Fetch detailed info
        details = api.get_disease_info(disease.get("id"))
        
        st.subheader("Symptoms")
        symptoms = details.get("symptoms", [])
        if symptoms:
            for sym in symptoms:
                st.markdown(f"- **{sym.get('name')}**: {sym.get('description')}")
        else:
            st.write("No specific symptoms listed for this disease.")

        st.subheader("Educational Resources")
        educational_content = api.get_educational_content(disease.get("id"))
        if educational_content:
            for article in educational_content:
                with st.expander(article.get("title")):
                    st.write(article.get("content"))
        else:
            st.write("No educational articles available for this disease at the moment.")
            
    except Exception as e:
        st.error(f"Could not fetch details for {disease.get('name', 'N/A')}: {e}")

if __name__ == "__main__":
    # This part is for direct testing of the page
    # You would need to mock the API calls and authentication
    # For example:
    # st.session_state['authenticated'] = True
    # st.session_state['user_profile'] = {'name': 'Test User'}
    render_education_page()