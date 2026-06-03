import os
import requests
from typing import Optional, Dict, Any

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


class APIClient:
    def __init__(self, base_url: str = BACKEND_URL):
        self.base_url = base_url.rstrip("/")

    def _headers(self, token: Optional[str] = None) -> dict:
        headers = {"Content-Type": "application/json"}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        return headers

    def _request(self, method: str, endpoint: str, token: Optional[str] = None, **kwargs) -> Dict[str, Any]:
        url = f"{self.base_url}{endpoint}"
        try:
            response = requests.request(
                method,
                url,
                headers=self._headers(token),
                timeout=120,
                **kwargs,
            )
            if response.status_code >= 400:
                detail = "Request failed"
                try:
                    detail = response.json().get("detail", detail)
                    if isinstance(detail, list):
                        detail = detail[0].get("msg", str(detail)) if detail else detail
                except Exception:
                    detail = response.text or detail
                return {"error": detail, "status_code": response.status_code}
            if response.headers.get("content-type", "").startswith("application/pdf"):
                return {"content": response.content, "headers": dict(response.headers)}
            if "text/plain" in response.headers.get("content-type", ""):
                return {"content": response.text, "headers": dict(response.headers)}
            return response.json()
        except requests.exceptions.ConnectionError:
            return {"error": "Cannot connect to backend. Ensure the API server is running on port 8000."}
        except requests.exceptions.Timeout:
            return {"error": "Request timed out. Please try again."}
        except Exception as e:
            return {"error": str(e)}

    def signup(self, full_name: str, email: str, password: str) -> dict:
        return self._request("POST", "/auth/signup", json={"full_name": full_name, "email": email, "password": password})

    def login(self, email: str, password: str) -> dict:
        return self._request("POST", "/auth/login", json={"email": email, "password": password})

    def google_login(self, id_token: str = "", code: str = "", redirect_uri: str = "http://localhost:8501") -> dict:
        return self._request(
            "POST",
            "/auth/google-login",
            json={"id_token": id_token, "code": code, "redirect_uri": redirect_uri},
        )

    def forgot_password(self, email: str) -> dict:
        return self._request("POST", "/auth/forgot-password", json={"email": email})

    def reset_password(self, token: str, new_password: str) -> dict:
        return self._request("POST", "/auth/reset-password", json={"token": token, "new_password": new_password})

    def logout(self, token: str) -> dict:
        return self._request("POST", "/auth/logout", token=token)

    def get_profile(self, token: str) -> dict:
        return self._request("GET", "/profile", token=token)

    def update_profile(self, token: str, data: dict) -> dict:
        return self._request("PUT", "/profile", token=token, json=data)

    def change_password(self, token: str, current_password: str, new_password: str) -> dict:
        return self._request(
            "PUT",
            "/profile/password",
            token=token,
            json={"current_password": current_password, "new_password": new_password},
        )

    def update_settings(self, token: str, data: dict) -> dict:
        return self._request("PUT", "/profile/settings", token=token, json=data)

    def send_chat(self, token: str, message: str, category: str, chat_id: Optional[int] = None) -> dict:
        payload = {"message": message, "category": category}
        if chat_id:
            payload["chat_id"] = chat_id
        return self._request("POST", "/chat", token=token, json=payload)

    def get_chat_history(self, token: str, search: Optional[str] = None) -> dict:
        params = {"search": search} if search else {}
        return self._request("GET", "/chat/history", token=token, params=params)

    def get_chat(self, token: str, chat_id: int) -> dict:
        return self._request("GET", f"/chat/{chat_id}", token=token)

    def delete_chat(self, token: str, chat_id: int) -> dict:
        return self._request("DELETE", f"/chat/{chat_id}", token=token)

    def rename_chat(self, token: str, chat_id: int, title: str) -> dict:
        return self._request("PUT", f"/chat/{chat_id}/rename", token=token, json={"title": title})

    def export_txt(self, token: str, chat_id: int) -> dict:
        return self._request("GET", f"/export/txt/{chat_id}", token=token)

    def export_pdf(self, token: str, chat_id: int) -> dict:
        return self._request("GET", f"/export/pdf/{chat_id}", token=token)

    def share_chat(self, token: str, chat_id: int) -> dict:
        return self._request("GET", f"/export/share/{chat_id}", token=token)

    def health(self) -> dict:
        return self._request("GET", "/health")
