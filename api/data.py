"""
Central file for all data and dependencies to avoid circular imports
"""
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from datetime import datetime, timedelta
from typing import Dict, Any
import uuid

# Security
security = HTTPBearer()

# ========== DUMMY DATABASES ==========
users_db = {}
sessions_db = {}
chats_db = {}
symptoms_db = {}
diseases_db = {}
chat_sessions_db = {}
chat_history_db = {}
medical_symptoms_db = []
medical_diseases_db = []
educational_content_db = {}
admin_logs_db = []
admin_analytics_db = {}

# ========== INITIALIZE DUMMY DATA ==========
def init_dummy_data():
    """Initialize all dummy data"""
    
    # Clear existing data
    users_db.clear()
    sessions_db.clear()
    chats_db.clear()
    symptoms_db.clear()
    diseases_db.clear()
    chat_sessions_db.clear()
    chat_history_db.clear()
    medical_symptoms_db.clear()
    medical_diseases_db.clear()
    educational_content_db.clear()
    admin_logs_db.clear()
    admin_analytics_db.clear()
    
    # Dummy users
    users_db["user1@example.com"] = {
        "id": "user_001",
        "email": "user1@example.com",
        "password_hash": "hashed_password_123",
        "first_name": "John",
        "last_name": "Doe",
        "age": 30,
        "gender": "Male",
        "account_type": "user",
        "created_at": "2024-01-01T10:00:00",
        "last_login": "2024-03-15T14:30:00",
        "preferences": {}
    }
    
    users_db["admin@diagnoze.ai"] = {
        "id": "admin_001",
        "email": "admin@diagnoze.ai",
        "password_hash": "hashed_admin_123",
        "first_name": "Admin",
        "last_name": "User",
        "age": 35,
        "gender": "Other",
        "account_type": "admin",
        "created_at": "2024-01-01T09:00:00",
        "last_login": "2024-03-15T15:00:00",
        "preferences": {}
    }
    
    # Dummy symptoms
    symptoms_db["headache"] = {
        "id": "symp_001",
        "name": "Headache",
        "category": "Neurological",
        "description": "Pain in the head or upper neck"
    }
    
    symptoms_db["fever"] = {
        "id": "symp_002",
        "name": "Fever",
        "category": "General",
        "description": "Elevated body temperature"
    }
    
    # Medical symptoms list
    medical_symptoms_db.extend([
        {
            "id": "symp_001",
            "name": "Headache",
            "category": "Neurological",
            "description": "Pain in the head or upper neck area.",
            "common_causes": ["Stress", "Dehydration", "Migraine", "Tension"],
            "severity_levels": ["Mild", "Moderate", "Severe"]
        },
        {
            "id": "symp_002",
            "name": "Fever",
            "category": "General",
            "description": "Elevated body temperature above normal range.",
            "common_causes": ["Infection", "Inflammation", "Heat exhaustion"],
            "severity_levels": ["Low-grade", "Moderate", "High"]
        },
        {
            "id": "symp_003",
            "name": "Cough",
            "category": "Respiratory",
            "description": "Sudden expulsion of air from lungs.",
            "common_causes": ["Common cold", "Flu", "Allergies", "Asthma"],
            "severity_levels": ["Dry", "Productive", "Persistent"]
        },
        {
            "id": "symp_004",
            "name": "Fatigue",
            "category": "General",
            "description": "Extreme tiredness or lack of energy.",
            "common_causes": ["Lack of sleep", "Stress", "Anemia", "Infection"],
            "severity_levels": ["Mild", "Moderate", "Severe"]
        },
        {
            "id": "symp_005",
            "name": "Nausea",
            "category": "Digestive",
            "description": "Feeling of sickness with inclination to vomit.",
            "common_causes": ["Food poisoning", "Migraine", "Motion sickness", "Pregnancy"],
            "severity_levels": ["Mild", "Moderate", "Severe"]
        }
    ])
    
    # Medical diseases
    medical_diseases_db.extend([
        {
            "id": "dis_001",
            "name": "Migraine",
            "category": "Neurological",
            "severity": "moderate",
            "description": "A neurological condition characterized by recurrent moderate to severe headaches, often accompanied by nausea, vomiting, and sensitivity to light and sound.",
            "symptoms": ["Headache", "Nausea", "Light sensitivity", "Sound sensitivity"],
            "common_triggers": ["Stress", "Certain foods", "Hormonal changes", "Sleep disturbances"],
            "emergency": False,
            "self_care_tips": [
                "Rest in a dark, quiet room",
                "Apply cold compress to forehead or neck",
                "Stay hydrated",
                "Practice relaxation techniques"
            ],
            "when_to_see_doctor": [
                "Sudden, severe headache like a thunderclap",
                "Headache with fever, stiff neck, confusion",
                "Headache after head injury",
                "Chronic headaches that worsen"
            ],
            "prevention_tips": [
                "Identify and avoid triggers",
                "Maintain regular sleep schedule",
                "Stay hydrated",
                "Manage stress through exercise and meditation"
            ]
        },
        {
            "id": "dis_002",
            "name": "Viral Infection (Common Cold/Flu)",
            "category": "Infectious",
            "severity": "mild",
            "description": "Viral infection affecting the upper respiratory tract, characterized by fever, cough, sore throat, runny nose, and fatigue.",
            "symptoms": ["Fever", "Cough", "Sore throat", "Runny nose", "Fatigue", "Body aches"],
            "common_triggers": ["Virus exposure", "Weakened immune system", "Seasonal changes"],
            "emergency": False,
            "self_care_tips": [
                "Rest and get plenty of sleep",
                "Stay hydrated with water and warm fluids",
                "Use over-the-counter fever reducers if needed",
                "Gargle with salt water for sore throat"
            ],
            "when_to_see_doctor": [
                "Fever above 103°F (39.4°C)",
                "Symptoms worsen after 3 days",
                "Difficulty breathing or shortness of breath",
                "Severe headache or chest pain"
            ],
            "prevention_tips": [
                "Wash hands frequently",
                "Avoid close contact with sick people",
                "Get annual flu vaccine",
                "Maintain healthy lifestyle"
            ]
        }
    ])
    
    # Diseases for chat predictions
    diseases_db["migraine"] = {
        "id": "dis_001",
        "name": "Migraine",
        "category": "Neurological",
        "severity": "moderate",
        "description": "A neurological condition causing severe headache attacks.",
        "symptoms": ["headache", "nausea", "light_sensitivity"],
        "emergency": False,
        "self_care_tips": [
            "Rest in a dark, quiet room",
            "Stay hydrated",
            "Apply cold compress to forehead",
            "Avoid triggers like bright lights"
        ],
        "when_to_see_doctor": [
            "Sudden, severe headache like a thunderclap",
            "Headache with fever, stiff neck, confusion",
            "Headache after head injury"
        ]
    }
    
    diseases_db["viral_infection"] = {
        "id": "dis_002",
        "name": "Viral Infection",
        "category": "Infectious",
        "severity": "mild",
        "description": "Common viral illness like flu or cold.",
        "symptoms": ["fever", "headache", "fatigue", "body_aches"],
        "emergency": False,
        "self_care_tips": [
            "Rest and stay hydrated",
            "Over-the-counter fever reducers",
            "Warm fluids for throat comfort"
        ],
        "when_to_see_doctor": [
            "Fever above 103°F (39.4°C)",
            "Symptoms worsen after 3 days",
            "Difficulty breathing"
        ]
    }
    
    # Educational content
    educational_content_db["migraine"] = {
        "disease_id": "dis_001",
        "sections": [
            {
                "title": "Understanding Migraine",
                "content": "Migraine is more than just a headache. It's a complex neurological condition that affects millions of people worldwide.",
                "image_url": None
            },
            {
                "title": "Self-Care Tips",
                "content": "• Rest in a dark, quiet room\n• Apply cold compress\n• Stay hydrated\n• Avoid triggers",
                "image_url": None
            }
        ],
        "references": ["International Headache Society"]
    }
    
    # Initial admin logs
    admin_logs_db.extend([
        {
            "id": "log_001",
            "timestamp": "2024-03-15T10:00:00",
            "action": "system_start",
            "admin_id": "admin_001",
            "details": {"message": "System initialized with dummy data"}
        }
    ])

# ========== DEPENDENCIES ==========
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user"""
    token = credentials.credentials
    
    if token not in sessions_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
    
    session = sessions_db[token]
    
    # Check if session expired
    if datetime.fromisoformat(session["expires_at"]) < datetime.now():
        del sessions_db[token]
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session expired"
        )
    
    # Get user
    user_email = session["user_email"]
    if user_email not in users_db:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return users_db[user_email]

async def get_current_admin(user: Dict = Depends(get_current_user)):
    """Get current admin user"""
    if user.get("account_type") != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return user

# ========== HELPER FUNCTIONS ==========
def create_token():
    """Create a new session token"""
    return f"token_{uuid.uuid4().hex}"

def create_user_id():
    """Create a new user ID"""
    return f"user_{uuid.uuid4().hex[:8]}"

def create_chat_id():
    """Create a new chat ID"""
    return f"chat_{uuid.uuid4().hex[:8]}"

def create_session_id():
    """Create a new session ID"""
    return f"session_{uuid.uuid4().hex[:8]}"

# Initialize data
init_dummy_data()

