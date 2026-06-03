from typing import Optional
import httpx
from backend.config import get_settings

settings = get_settings()


async def verify_google_token(id_token: str) -> Optional[dict]:
    """Verify Google ID token and return user info."""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://oauth2.googleapis.com/tokeninfo",
            params={"id_token": id_token},
        )
        if response.status_code != 200:
            return None
        data = response.json()
        if settings.GOOGLE_CLIENT_ID and data.get("aud") != settings.GOOGLE_CLIENT_ID:
            return None
        return {
            "google_id": data.get("sub"),
            "email": data.get("email"),
            "full_name": data.get("name", data.get("email", "User")),
            "profile_picture": data.get("picture"),
        }


async def exchange_google_code(code: str, redirect_uri: str) -> Optional[dict]:
    """Exchange authorization code for tokens."""
    async with httpx.AsyncClient() as client:
        token_response = await client.post(
            "https://oauth2.googleapis.com/token",
            data={
                "code": code,
                "client_id": settings.GOOGLE_CLIENT_ID,
                "client_secret": settings.GOOGLE_CLIENT_SECRET,
                "redirect_uri": redirect_uri,
                "grant_type": "authorization_code",
            },
        )
        if token_response.status_code != 200:
            return None
        tokens = token_response.json()
        id_token = tokens.get("id_token")
        if not id_token:
            return None
        return await verify_google_token(id_token)
