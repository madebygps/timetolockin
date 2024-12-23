import uuid
import requests
from fastapi import APIRouter
from datetime import datetime, timedelta
from .database import sessions_container

router = APIRouter()

@router.post("/sessions/start")
async def start_session(repo: str, intention: str, user_id: str):
    session_data = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "repo": repo,
        "intention": intention,
        "start_time": datetime.utcnow().isoformat(),
        "end_time": (datetime.utcnow() + timedelta(minutes=25)).isoformat(),
        "is_valid": False
    }
    sessions_container.create_item(body=session_data)
    return {"message": "Session started", "session_id": session_data["id"]}

@router.post("/sessions/complete")
async def complete_session(session_id: str, user_id: str):
    session = sessions_container.read_item(item=session_id, partition_key=user_id)
    access_token = session["access_token"]
    headers = {"Authorization": f"token {access_token}"}
    commits_url = f"https://api.github.com/repos/{session['repo']}/commits"
    response = requests.get(commits_url, headers=headers)
    commits = response.json()

    start_time = datetime.fromisoformat(session["start_time"])
    end_time = datetime.fromisoformat(session["end_time"])
    for commit in commits:
        commit_time = datetime.strptime(commit["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ")
        if start_time <= commit_time <= end_time:
            session["is_valid"] = True
            sessions_container.upsert_item(session)
            return {"message": "Session completed", "is_valid": True}

    return {"message": "No valid commits found", "is_valid": False}