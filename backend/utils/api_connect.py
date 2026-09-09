import requests
import streamlit as st
from typing import Dict, List, Any, Optional

class APIClient:
    def __init__(self):
        self.base_url = st.secrets.get("API_BASE_URL", "http://localhost:8889/api/v1")

    def _get_headers(self, headers: Optional[Dict] = None) -> Dict:
        """Get headers with authentication token."""
        token = st.session_state.get("auth_token")
        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json"
        }
        if token:
            default_headers["Authorization"] = f"Bearer {token}"
        if headers:
            default_headers.update(headers)
        return default_headers

    def _make_request(self, method: str, endpoint: str, **kwargs) -> Dict:
        """Make HTTP request to API."""
        url = f"{self.base_url}{endpoint}"
        headers = self._get_headers(kwargs.pop("headers", {}))
        try:
            response = requests.request(method=method, url=url, headers=headers, **kwargs)
            if response.status_code == 401:
                st.session_state.update({"authenticated": False, "auth_token": None})
                st.error("Session expired. Please login again.")
                st.rerun()
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            st.error(f"API Error: {e}")
            return {"error": str(e), "success": False}

    def login(self, email: str, password: str) -> Dict:
        """User login."""
        return self._make_request("POST", "/auth/login", json={"email": email, "password": password})

    def register(self, user_data: Dict) -> Dict:
        """User registration."""
        return self._make_request("POST", "/auth/register", json=user_data)

    def logout(self) -> Dict:
        """User logout."""
        return self._make_request("POST", "/auth/logout")

    def get_user_profile(self) -> Dict:
        """Get current user profile."""
        return self._make_request("GET", "/users/profile")

    def update_user_profile(self, profile_data: Dict) -> Dict:
        """Update user profile."""
        return self._make_request("PUT", "/users/profile", json=profile_data)

    def get_chat_history(self, page: int = 1, limit: int = 10) -> Dict:
        """Get user's chat history."""
        return self._make_request("GET", "/users/history", params={"page": page, "limit": limit})

    def get_chat_by_id(self, chat_id: str) -> Dict:
        """Get specific chat by ID."""
        return self._make_request("GET", f"/users/history/{chat_id}")

    def delete_chat(self, chat_id: str) -> Dict:
        """Delete chat from history."""
        return self._make_request("DELETE", f"/users/history/{chat_id}")

    def get_symptoms(self, search: str = None, category: str = None) -> Dict:
        """Get symptoms list."""
        params = {}
        if search:
            params["q"] = search
        if category:
            params["category"] = category
        return self._make_request("GET", "/medical/symptoms", params=params if params else None)

    def get_symptom(self, symptom_id: int) -> Dict:
        """Get specific symptom."""
        return self._make_request("GET", f"/medical/symptoms/{symptom_id}")

    def get_diseases(self, search: str = "", category: str = "", severity: str = "") -> Dict:
        """Get diseases list."""
        params = {}
        if search:
            params["q"] = search
        if category:
            params["category"] = category
        if severity:
            params["severity"] = severity
        return self._make_request("GET", "/medical/diseases", params=params if params else None)

    def get_disease_info(self, disease_id: int) -> Dict:
        """Get detailed disease information."""
        return self._make_request("GET", f"/medical/diseases/{disease_id}")

    def search_medical(self, query: str, type: str = None, limit: int = 10) -> Dict:
        """Search medical information."""
        params = {"q": query, "limit": limit}
        if type:
            params["type"] = type
        return self._make_request("GET", "/medical/search", params=params)

    def get_educational_content(self, disease_id: int) -> Dict:
        """Get educational content for disease."""
        return self._make_request("GET", f"/medical/educational/{disease_id}")

    # Chat endpoints
    def start_chat_session(self) -> Dict:
        """Start a new chat session."""
        return self._make_request("POST", "/chat/start-session")

    def send_chat_message(self, session_id: str, message: str, symptoms: List[str] = None) -> Dict:
        """Send a message in chat session."""
        payload = {
            "session_id": session_id,
            "message": message
        }
        if symptoms:
            payload["symptoms"] = symptoms
        return self._make_request("POST", "/chat/send-message", json=payload)

    def generate_prediction(self, symptoms: List[str]) -> Dict:
        """Generate prediction from symptoms."""
        return self._make_request("POST", "/chat/generate-prediction", json={"symptoms": symptoms})

    def save_chat_session(self, session_id: str, title: str = None) -> Dict:
        """Save chat session to history."""
        payload = {"session_id": session_id}
        if title:
            payload["title"] = title
        return self._make_request("POST", "/chat/save-session", json=payload)

    def get_chat_session(self, session_id: str) -> Dict:
        """Get chat session by ID."""
        return self._make_request("GET", f"/chat/session/{session_id}")

    def delete_chat_session(self, session_id: str) -> Dict:
        """Delete chat session."""
        return self._make_request("DELETE", f"/chat/session/{session_id}")

@st.cache_resource
def get_api_client() -> APIClient:
    """Get a cached instance of the API client."""
    return APIClient()

