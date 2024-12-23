import os
from fastapi import FastAPI
from dotenv import load_dotenv
from .auth import oauth, login_via_github, auth_callback
from .auth import router as auth_router
from .sessions import start_session, complete_session   
from .sessions import router as sessions_router
from starlette.middleware.sessions import SessionMiddleware

load_dotenv()

app = FastAPI()

# Add SessionMiddleware
app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv('SECRET_KEY'),  # Strong secret key
    max_age=86400,  # Session expires in 1 day
    same_site='lax',  # Allows cookies for navigation requests
    https_only=False,  # Set to True in production
  
)


# Register OAuth
oauth.register(
    name='github',
    client_id=os.getenv('GITHUB_CLIENT_ID'),
    client_secret=os.getenv('GITHUB_CLIENT_SECRET'),
    access_token_url='https://github.com/login/oauth/access_token',
    authorize_url='https://github.com/login/oauth/authorize',
    client_kwargs={'scope': 'repo user'},
)

app.include_router(auth_router)
app.include_router(sessions_router)