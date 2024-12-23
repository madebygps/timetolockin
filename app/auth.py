
import os
from fastapi import APIRouter, Request
from authlib.integrations.starlette_client import OAuth

oauth = OAuth()
router = APIRouter()

@router.get("/auth/login")
async def login_via_github(request: Request):
    redirect_uri = "https://64b8-24-193-199-213.ngrok-free.app/auth/callback"
    response = await oauth.github.authorize_redirect(request, redirect_uri)
    print("Generated state:", request.session.get("state"))
    return response

@router.get("/auth/callback")
async def auth_callback(request: Request):
    print("Returned state:", request.query_params.get("state"))
    print("Session state:", request.session.get("state"))
    token = await oauth.github.authorize_access_token(request)
    user_info = await oauth.github.get("user", token=token)
    return user_info.json()