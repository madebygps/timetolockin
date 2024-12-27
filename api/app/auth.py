import uuid
from fastapi import APIRouter, Request, HTTPException
from authlib.integrations.starlette_client import OAuth
from fastapi.responses import RedirectResponse
import httpx
from .database import users_container

oauth = OAuth()
router = APIRouter()

@router.get('/auth/login')
async def login_via_github(request: Request):
    state = str(uuid.uuid4())  
    request.session['state'] = state  
    redirect_uri = 'http://127.0.0.1:8000/auth/callback'
    return await oauth.github.authorize_redirect(request, redirect_uri, state=state)

@router.post('/auth/logout')
async def logout(request: Request):
    """
    Clears the user's session and logs them out.
    """
    try:
        # Clear session data
        request.session.clear()

        # Optionally log logout activity
        print("User logged out successfully.")

        # Return a success message or status
        return {"message": "Logout successful"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to log out: {str(e)}")


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

        # Fetch user info
        user_info_url = "https://api.github.com/user"
        headers = {"Authorization": f"Bearer {token['access_token']}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(user_info_url, headers=headers)
            response.raise_for_status()
            user_info = response.json()

        # Save user info and token to Cosmos DB
        user_id = user_info["login"]
        user_data = {
            "id": user_id,
            "access_token": token["access_token"],
            "streak": 0,
            "longest_streak": 0,  # Initialize longest streak
            "last_valid_session_date": None,
        }

        # Check if user exists, else create a new record
        try:
            existing_user = users_container.read_item(item=user_id, partition_key=user_id)
            user_data["streak"] = existing_user.get("streak", 0)
            user_data["longest_streak"] = existing_user.get("longest_streak", 0)
            user_data["last_valid_session_date"] = existing_user.get("last_valid_session_date")
        except Exception:  # User doesn't exist
            pass

        users_container.upsert_item(user_data)

        # Save token and user ID to session
        request.session["access_token"] = token["access_token"]
        request.session["user_id"] = user_id

        # Redirect to pomodoro page 8080
        return RedirectResponse(url="http://localhost:5173/streaks")
        
    except Exception as e:
        raise HTTPException(status_code=500, detail="OAuth callback failed")