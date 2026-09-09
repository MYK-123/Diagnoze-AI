import streamlit as st
from utils.auth import check_authentication

def render_emergency_page(router):
    """
    Renders the Emergency Guidelines page (P14).
    This page requires authentication.
    """

    if st.button("Home"):
        router.redirect(*router.build("home"))
    
    st.set_page_config(page_title="Emergency Guidelines - Diagnoze AI", layout="wide")

    if not check_authentication():
        st.error("You must be logged in to view this page.")
        st.stop()

    st.title("🚨 Emergency Medical Guidelines")
    st.warning(
        "**DISCLAIMER:** This is not a substitute for professional medical advice. "
        "If you believe you are having a medical emergency, call your local emergency number immediately."
    )

    st.header("When to Call for an Ambulance Immediately")
    st.markdown("""
    Call for an ambulance or go to the nearest emergency department for any of the following life-threatening conditions:
    - **Severe Chest Pain or Pressure:** Especially if it radiates to your arm, jaw, or back, as it could be a heart attack.
    - **Difficulty Breathing or Shortness of Breath:** Gasping for air, unable to speak in full sentences.
    - **Sudden Severe Headache:** Often described as the "worst headache of your life," which could signal an aneurysm or stroke.
    - **Weakness, Numbness, or Drooping on One Side of the Body:** Classic signs of a stroke (think F.A.S.T.: Face, Arms, Speech, Time).
    - **Loss of Consciousness or Fainting:** Any unexplained fainting spell needs urgent evaluation.
    - **Seizures:** Especially if it's the first time, lasts longer than 5 minutes, or if the person does not regain consciousness.
    - **Uncontrolled Bleeding:** Bleeding that does not stop after 10-15 minutes of direct pressure.
    - **Severe Abdominal Pain:** Particularly if it's sudden, sharp, and accompanied by a fever or vomiting.
    - **Major Trauma:** Such as from a car accident, a significant fall, or a deep wound.
    - **Severe Allergic Reaction (Anaphylaxis):** Characterized by hives, swelling of the face or throat, and difficulty breathing.
    """)

    st.header("When to Visit a Doctor or Urgent Care Clinic")
    st.markdown("""
    For less severe issues that still require prompt attention, consider visiting a doctor or an urgent care clinic:
    - **Fever:** A high fever (above 103°F / 39.4°C) or a fever that lasts for more than a few days.
    - **Vomiting or Diarrhea:** If it's persistent, severe, or you see signs of dehydration.
    - **Sprains and Strains:** If you can't bear weight on a joint or if a limb looks deformed.
    - **Minor Cuts:** That might need stitches but are not bleeding uncontrollably.
    - **Urinary Tract Infection (UTI) Symptoms:** Painful urination, urgency, and frequency.
    - **Mild to Moderate Asthma Attacks:** That are controlled with a rescue inhaler but are more frequent than usual.
    - **Skin Rashes or Infections:** Such as cellulitis or abscesses that are worsening.
    """)
    
    st.header("Emergency Contact Numbers by Country")
    st.info("This is a partial list. Always confirm the number for your specific location.")
    contact_data = {
        "Country": ["United States", "Canada", "United Kingdom", "Australia", "India", "Germany", "France", "Japan"],
        "Emergency Number": ["911", "911", "999 or 112", "000", "112", "112", "112", "119 (Fire/Ambulance), 110 (Police)"]
    }
    st.table(contact_data)

    st.header("Basic First Aid Guidelines")
    st.markdown("""
    While waiting for medical help, some basic first aid can be critical.
    - **For Bleeding:** Apply firm, direct pressure to the wound with a clean cloth.
    - **For Burns:** Cool the burn with cool (not cold) running water for at least 10 minutes. Do not apply ice or ointments.
    - **For Seizures:** Ease the person to the floor, turn them onto their side, and clear the area of hard or sharp objects. Do not restrain them or put anything in their mouth.
    - **For Choking:** Perform the Heimlich maneuver (abdominal thrusts).
    - **For someone who is unresponsive and not breathing:** Start CPR if you are trained to do so.
    """)

    st.header("Check Your Symptom")
    symptom_check = st.text_input("Enter a symptom to check if it's commonly associated with an emergency:", placeholder="e.g., 'dizziness'")
    if symptom_check:
        emergency_symptoms = [
            "chest pain", "breathing difficulty", "numbness", "weakness", "severe headache", 
            "fainting", "seizure", "uncontrolled bleeding", "severe abdominal pain"
        ]
        if any(emergency_symptom in symptom_check.lower() for emergency_symptom in emergency_symptoms):
            st.error(f"**'{symptom_check.capitalize()}'** can be a sign of a medical emergency. Please seek immediate medical attention or call for help if it is severe.")
        else:
            st.success(f"**'{symptom_check.capitalize()}'** is not always an emergency, but if it is severe, persistent, or worrying you, it's best to consult a healthcare professional.")

    st.markdown("---")
    if st.button("Download or Print Guidelines"):
        st.info("Print functionality would be implemented here. For now, please use your browser's print function (Ctrl+P).")

