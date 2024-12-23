import uuid
from fastapi import APIRouter, Request, HTTPException
from authlib.integrations.starlette_client import OAuth
import httpx

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

        print(f"Received code: {code}")
        print(f"Returned state: {state}")
        print(f"Session state: {request.session.get('state')}")

        # Validate state
        if state != request.session.get("state"):
            raise HTTPException(status_code=400, detail="Invalid state parameter")

        # Exchange the authorization code for an access token
        token = await oauth.github.authorize_access_token(request)
        print(f"Token received: {token}")

        # Fetch user info
        user_info_url = "https://api.github.com/user"
        headers = {"Authorization": f"Bearer {token['access_token']}"}
        async with httpx.AsyncClient() as client:
            response = await client.get(user_info_url, headers=headers)
            response.raise_for_status()
            user_info = response.json()

        return {"user_info": user_info}

    except Exception as e:
        print(f"Error during OAuth callback: {e}")
        raise HTTPException(status_code=500, detail="OAuth callback failed")
