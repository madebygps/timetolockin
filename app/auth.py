from datetime import datetime
import uuid
from fastapi import APIRouter, Request, HTTPException
from authlib.integrations.starlette_client import OAuth
import httpx
from .database import sessions_container, users_container

oauth = OAuth()
router = APIRouter()

@router.get('/auth/login')
async def login_via_github(request: Request):
    state = str(uuid.uuid4())  # Generate a random state
    request.session['state'] = state  # Store state in the session
    print('Generated state:', state)
    
    redirect_uri = 'http://127.0.0.1:8000/auth/callback'
    return await oauth.github.authorize_redirect(request, redirect_uri, state=state)


@router.get("/auth/callback")
async def auth_callback(request: Request):
    try:
        code = request.query_params.get("code")
        state = request.query_params.get("state")

        # Validate state
        if state != request.session.get("state"):
            raise HTTPException(status_code=400, detail="Invalid state parameter")

        # Exchange the authorization code for an access token
        token = await oauth.github.authorize_access_token(request)
        
        # Fetch user info from GitHub
        user_info_url = "https://api.github.com/user"
        headers = {"Authorization": f"Bearer {token['access_token']}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(user_info_url, headers=headers)
            response.raise_for_status()
            user_info = response.json()

        # Save user data to Cosmos DB
        user_id = user_info["login"]
        user_data = {
            "id": user_id,
            "github_id": user_info["id"],
            "avatar_url": user_info["avatar_url"],
            "name": user_info.get("name"),
            "email": user_info.get("email"),
            "bio": user_info.get("bio"),
            "company": user_info.get("company"),
            "created_at": datetime.utcnow().isoformat(),
        }
        users_container.upsert_item(user_data)

        # Save session data to Cosmos DB
        session_data = {
            "id": str(uuid.uuid4()),
            "user_id": user_id,
            "access_token": token["access_token"],
            "refresh_token": token.get("refresh_token"),
            "token_expiry": token.get("expires_at"),
            "created_at": datetime.utcnow().isoformat(),
        }
        sessions_container.upsert_item(session_data)

        # Store session info in the request session
        request.session["access_token"] = token["access_token"]
        request.session["user_id"] = user_id

        return {"message": "Login successful", "user_info": user_info}

    except httpx.HTTPStatusError as http_err:
        raise HTTPException(
            status_code=http_err.response.status_code,
            detail=f"Error fetching user info: {http_err.response.text}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OAuth callback failed: {str(e)}")

