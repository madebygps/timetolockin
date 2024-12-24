import uuid
import httpx
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timedelta, timezone
from .database import sessions_container

router = APIRouter()

@router.post("/sessions/start")
async def start_session(repo: str, intention: str, request: Request):
    # Ensure the user is authenticated
    access_token = request.session.get("access_token")
    user_id = request.session.get("user_id")
    if not access_token or not user_id:
        raise HTTPException(status_code=401, detail="User is not authenticated")

    # Create session data
    session_data = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "repo": repo,
        "intention": intention,
        "start_time": datetime.now(timezone.utc).isoformat(),
        "end_time": (datetime.now(timezone.utc) + timedelta(minutes=25)).isoformat(),
        "is_valid": False,
        "access_token": access_token,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Save session to Cosmos DB
    try:
        sessions_container.create_item(body=session_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving session: {str(e)}")

    return {"message": "Session started", "session_id": session_data["id"]}


@router.post("/sessions/complete")
async def complete_session(session_id: str, request: Request):
    # Ensure the user is authenticated
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(status_code=401, detail="User is not authenticated")

    try:
        # Fetch the session data from Cosmos DB
        session = sessions_container.read_item(item=session_id, partition_key=user_id)

        # Fetch commits from GitHub
        headers = {"Authorization": f"Bearer {session['access_token']}"}
        commits_url = f"https://api.github.com/repos/{session['user_id']}/{session['repo']}/commits"
        async with httpx.AsyncClient() as client:
            response = await client.get(commits_url, headers=headers)
            response.raise_for_status()
            commits = response.json()

        # Validate commit timestamps
        start_time = datetime.fromisoformat(session["start_time"])
        end_time = datetime.fromisoformat(session["end_time"])

        for commit in commits:
            commit_time = datetime.strptime(
                commit["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ"
            )
            if start_time <= commit_time <= end_time:
                session["is_valid"] = True
                sessions_container.upsert_item(session)
                return {"message": "Session completed successfully", "is_valid": True}

        return {"message": "No valid commits found within the session timeframe", "is_valid": False}

    except sessions_container.exceptions.CosmosResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Session not found")
    except httpx.HTTPStatusError as http_err:
        raise HTTPException(
            status_code=http_err.response.status_code,
            detail=f"Error fetching commits from GitHub: {http_err.response.text}",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing session: {str(e)}")
