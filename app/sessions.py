import uuid
from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timedelta, timezone
import requests
from .database import sessions_container, users_container
from azure.cosmos.exceptions import CosmosResourceNotFoundError

router = APIRouter()

@router.post("/sessions/create")
async def create_session(
    request: Request,
    repo: str,
    intention: str,
    total_pomodoros: int = 1,  # Default: 1 Pomodoro
    pomodoro_length: int = 25,  # Default: 25 minutes
    break_length: int = 2  # Default: 2 minutes
):
    """
    Creates a new Pomodoro session.

    Args:
        repo (str): The repository associated with the session.
        intention (str): The user's intention for the session.
        total_pomodoros (int): Total number of Pomodoros (1-10, default: 1).
        pomodoro_length (int): Length of each Pomodoro in minutes (25-60, default: 25).
        break_length (int): Length of breaks between Pomodoros in minutes (2-5, default: 2).

    Returns:
        dict: A message confirming session creation and the session ID.
    """
    # Ensure the user is authenticated
    access_token = request.session.get("access_token")
    user_id = request.session.get("user_id")
    if not access_token or not user_id:
        raise HTTPException(
            status_code=401, detail="User is not authenticated"
        )

    # Validate inputs
    if not repo or not intention:
        raise HTTPException(
            status_code=400, detail="Repository and intention are required"
        )

    if total_pomodoros < 1 or total_pomodoros > 10:
        raise HTTPException(
            status_code=400, detail="Number of Pomodoros must be between 1 and 10"
        )

    if pomodoro_length < 25 or pomodoro_length > 60:
        raise HTTPException(
            status_code=400, detail="Pomodoro length must be between 25 and 60 minutes"
        )

    if break_length < 2 or break_length > 5:
        raise HTTPException(
            status_code=400, detail="Break length must be between 2 and 5 minutes"
        )

    # Create session data without starting it
    session_data = {
        "id": str(uuid.uuid4()),
        "user_id": user_id,
        "repo": repo,
        "intention": intention,
        "total_pomodoros": total_pomodoros,
        "pomodoro_length": pomodoro_length,
        "break_length": break_length,
        "is_valid": False,
        "access_token": access_token,
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Save session to Cosmos DB
    try:
        sessions_container.create_item(body=session_data)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error creating session: {str(e)}"
        )

    return {"message": "Session created", "session_id": session_data["id"]}

@router.post("/sessions/complete")
async def complete_session(session_id: str, user_id: str):
    """
    Completes a session and checks for valid commits within the session timeframe.
    """
    try:
        # Fetch session from Cosmos DB
        session = sessions_container.read_item(
            item=session_id, partition_key=user_id)

        # Fetch commits from GitHub
        headers = {"Authorization": f"Bearer {session['access_token']}"}
        commits_url = f"https://api.github.com/repos/{
            user_id}/{session['repo']}/commits"
        response = requests.get(commits_url, headers=headers)
        response.raise_for_status()
        commits = response.json()

        # Validate commit timestamps
        start_time = datetime.fromisoformat(
            session["start_time"]).replace(tzinfo=timezone.utc)
        end_time = datetime.fromisoformat(
            session["end_time"]).replace(tzinfo=timezone.utc)
        current_date = datetime.now(timezone.utc).date()

        for commit in commits:
            commit_time = datetime.strptime(
                commit["commit"]["committer"]["date"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc)
            if start_time <= commit_time <= end_time:
                session["is_valid"] = True
                sessions_container.upsert_item(session)

                # Update user streak
                user = users_container.read_item(
                    item=user_id, partition_key=user_id)
                last_valid_session_date = user.get("last_valid_session_date")

                if last_valid_session_date:
                    last_valid_date = datetime.fromisoformat(
                        last_valid_session_date).date()
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
        raise HTTPException(
            status_code=500, detail=f"Error completing session: {str(e)}")

@router.post("/sessions/update")
async def update_pomodoro(session_id: str, user_id: str, request: Request):
    try:
        session = sessions_container.read_item(
            item=session_id, partition_key=user_id
        )

        # Determine whether the next step is a Pomodoro or a Break
        next_is_pomodoro = session["current_step"] % 2 == 0
        session["current_step"] += 1
        session["current_label"] = (
            f"Pomodoro {session['current_step'] // 2}"
            if next_is_pomodoro
            else f"Break {session['current_step'] // 2}"
        )

        # Update end time
        if next_is_pomodoro:
            session["end_time"] = (
                datetime.now(timezone.utc)
                + timedelta(minutes=session.get("pomodoro_length", 25))
            ).isoformat()
        else:
            break_length = (
                session.get("long_break_length", 15)
                if session["current_step"] // 2 % session.get("total_pomodoros", 4) == 0
                else session.get("break_length", 5)
            )
            session["end_time"] = (
                datetime.now(timezone.utc) + timedelta(minutes=break_length)
            ).isoformat()

        sessions_container.upsert_item(session)
        return {"message": "Pomodoro updated", "session": session}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error updating Pomodoro: {str(e)}"
        )

@router.post("/sessions/start")
async def start_session(session_id: str, request: Request):
    """
    Marks a session as started by updating the `start_time` and initial `end_time`.

    Args:
        session_id (str): The session ID.

    Returns:
        dict: A message confirming the session has started.
    """
    user_id = request.session.get("user_id")
    if not user_id:
        raise HTTPException(
            status_code=401, detail="User is not authenticated"
        )

    try:
        # Fetch session from Cosmos DB
        session = sessions_container.read_item(
            item=session_id, partition_key=user_id
        )

        # Update start and end times
        session["start_time"] = datetime.now(timezone.utc).isoformat()
        session["end_time"] = (
            datetime.now(timezone.utc) +
            timedelta(minutes=session["pomodoro_length"])
        ).isoformat()
        session["current_pomodoro"] = 0  # Initialize Pomodoro count

        # Save the updated session
        sessions_container.upsert_item(session)

        return {"message": "Session started", "session_id": session_id}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error starting session: {str(e)}"
        )

@router.get("/sessions/{session_id}")
async def get_session_state(session_id: str, request: Request):
    """
    Retrieve the current state of a session.

    Args:
        session_id (str): The ID of the session to retrieve.
        request (Request): The request object to get session context.

    Returns:
        dict: Current session state, including the step, label, and end time.

    Raises:
        HTTPException: If the session is not found or an error occurs.
    """
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User is not authenticated")

        # Fetch the session from the database
        session = sessions_container.read_item(item=session_id, partition_key=user_id)

        # Build response with the session state
        return {
            "session_id": session["id"],
            "user_id": session["user_id"],
            "current_label": session.get("current_label", "Pomodoro 1"),
            "current_step": session.get("current_step", 1),
            "total_pomodoros": session.get("total_pomodoros", 1),
            "pomodoro_length": session.get("pomodoro_length", 25),
            "break_length": session.get("break_length", 2),
            "long_break_length": session.get("long_break_length", 15),
            "end_time": session.get("end_time"),
            "is_valid": session.get("is_valid", False),
        }

    except CosmosResourceNotFoundError:
        raise HTTPException(
            status_code=404, detail=f"Session with ID {session_id} not found"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching session state: {str(e)}"
        )
