import streamlit as st
import pandas as pd
from datetime import datetime
from utils.auth import check_authentication
from utils.api_connect import get_api_client

def render_tracker_page(router):
    """
    Renders the Symptom Tracker page.
    Allows users to log and visualize their symptoms over time.
    """
    if not check_authentication():
        return

    st.set_page_config(page_title="Symptom Tracker", layout="wide")
    st.title("📈 Symptom Tracker")

    if st.button("Home"):
        router.redirect(*router.build("dashboard"))

    api = get_api_client()

    # Fetch Tracker History
    try:
        with st.spinner("Loading your symptom history..."):
            history = [] # api.get_tracker_history()
            df = pd.DataFrame(history) if history else pd.DataFrame(columns=['date', 'symptom', 'severity', 'notes'])
            df['date'] = pd.to_datetime(df['date'], errors='coerce')
    except Exception as e:
        st.error(f"Failed to load your tracking history: {e}")
        if st.button("Retry"):
            st.rerun()
        return

    tab1, tab2, tab3 = st.tabs(["📊 Dashboard", "📝 Log a Symptom", "📤 Export Data"])

    # Dashboard Tab
    with tab1:
        st.header("Your Symptom Dashboard")
        if not df.empty:
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Symptom Frequency Over Time")
                freq_df = df.groupby(df['date'].dt.date).size().reset_index(name='count')
                fig_freq = px.line(freq_df, x='date', y='count', title="Daily Symptom Logs", markers=True)
                st.plotly_chart(fig_freq, use_container_width=True)

            with col2:
                st.subheader("Most Common Symptoms")
                symptom_counts = df['symptom'].value_counts().reset_index()
                symptom_counts.columns = ['symptom', 'count']
                fig_bar = px.bar(symptom_counts.head(10), x='symptom', y='count', title="Top 10 Logged Symptoms")
                st.plotly_chart(fig_bar, use_container_width=True)

            st.subheader("Recent Symptom Logs")
            st.dataframe(df.sort_values('date', ascending=False).head(10))
        else:
            st.info("You haven't logged any symptoms yet. Go to the 'Log a Symptom' tab to get started!")

    # Log a Symptom Tab
    with tab2:
        st.header("Add a New Symptom Log")
        with st.form("symptom_log_form"):
            symptom_name = st.text_input("Symptom Name*", help="e.g., Headache, Fatigue")
            log_date = st.date_input("Date*", datetime.now())
            severity = st.select_slider(
                "Severity*",
                options=["Mild", "Moderate", "Severe", "Very Severe"],
                value="Moderate"
            )
            notes = st.text_area("Notes", help="Add any relevant details, like triggers or duration.")

            submitted = st.form_submit_button("Log Symptom")

            if submitted:
                if not symptom_name:
                    st.warning("Symptom name is required.")
                else:
                    try:
                        log_data = {
                            "symptom": symptom_name,
                            "date": log_date.isoformat(),
                            "severity": severity,
                            "notes": notes
                        }
                        # api.add_symptom_log(log_data)
                        st.success(f"Successfully logged '{symptom_name}'.")
                        st.rerun()
                    except Exception as e:
                        st.error(f"Failed to log symptom: {e}")

    # Export Data Tab
    with tab3:
        st.header("Export Your Symptom Data")
        if not df.empty:
            st.write("Download your complete symptom history in CSV format.")

            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📤 Download as CSV",
                data=csv,
                file_name="symptom_tracker_history.csv",
                mime="text/csv",
            )
        else:
            st.info("No data to export.")


