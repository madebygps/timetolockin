import uuid
import httpx
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timedelta, timezone

import requests
from .database import sessions_container, users_container
from azure.cosmos.exceptions import CosmosResourceNotFoundError

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
async def complete_session(session_id: str, user_id: str):
    try:
        # Fetch session from Cosmos DB
        session = sessions_container.read_item(item=session_id, partition_key=user_id)

        # Fetch commits from GitHub
        headers = {"Authorization": f"Bearer {session['access_token']}"}
        commits_url = f"https://api.github.com/repos/{user_id}/{session['repo']}/commits"
        response = requests.get(commits_url, headers=headers)
        response.raise_for_status()
        commits = response.json()

        # Validate commit timestamps
        start_time = datetime.fromisoformat(session["start_time"]).replace(tzinfo=timezone.utc)
        end_time = datetime.fromisoformat(session["end_time"]).replace(tzinfo=timezone.utc)
        current_date = datetime.now(timezone.utc).date()

        for commit in commits:
            commit_time = datetime.strptime(commit["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if start_time <= commit_time <= end_time:
                session["is_valid"] = True
                sessions_container.upsert_item(session)

                # Update user streak
                user = users_container.read_item(item=user_id, partition_key=user_id)
                last_valid_session_date = user.get("last_valid_session_date")

                if last_valid_session_date:
                    last_valid_date = datetime.fromisoformat(last_valid_session_date).date()
                    if current_date == last_valid_date:
                        pass  # Same day, streak doesn't change
                    elif current_date == last_valid_date + timedelta(days=1):
                        user["streak"] += 1  # Increment streak
                    else:
                        user["streak"] = 1  # Reset streak to 1
                else:
                    user["streak"] = 1  # First valid session

                # Update longest streak
                if user["streak"] > user.get("longest_streak", 0):
                    user["longest_streak"] = user["streak"]

                # Update last valid session date
                user["last_valid_session_date"] = current_date.isoformat()
                users_container.upsert_item(user)

                return {
                    "message": "Session completed successfully",
                    "is_valid": True,
                    "streak": user["streak"],
                    "longest_streak": user["longest_streak"],
                }

        # If no valid commits, reset streak
        session["is_valid"] = False
        sessions_container.upsert_item(session)

        user = users_container.read_item(item=user_id, partition_key=user_id)
        user["streak"] = 0  # Reset streak
        users_container.upsert_item(user)

        return {
            "message": "No valid commits found",
            "is_valid": False,
            "streak": user["streak"],
            "longest_streak": user.get("longest_streak", 0),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error completing session: {str(e)}")


@router.post("/sessions/update")
async def update_pomodoro(session_id: str, user_id: str, request: Request):
    try:
        session = sessions_container.read_item(item=session_id, partition_key=user_id)

        # Update the current Pomodoro count
        session["current_pomodoro"] += 1

        # Check if the session is complete
        if session["current_pomodoro"] >= session["total_pomodoros"]:
            session["is_valid"] = True

        # Update the end time for the next Pomodoro or break
        session["end_time"] = (
            datetime.now(timezone.utc) + timedelta(minutes=25 if session["current_pomodoro"] % 2 == 1 else 2)
        ).isoformat()

        sessions_container.upsert_item(session)
        return {"message": "Pomodoro updated", "session": session}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating Pomodoro: {str(e)}")

