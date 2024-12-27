import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from .auth import oauth
from .auth import router as auth_router
from .sessions import router as sessions_router
from .streaks import router as streaks_router
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8080"],  # Update with your frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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
app.include_router(streaks_router)