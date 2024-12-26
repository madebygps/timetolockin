from fastapi import APIRouter, HTTPException, Request
from datetime import datetime

from .database import sessions_container, users_container

router = APIRouter()

@router.get("/streak")
async def get_streak(request: Request):
    """
    Endpoint to get the user's streak information.

    Args:
        request (Request): The request object containing session information.

    Returns:
        dict: A dictionary containing the user's current streak, longest streak, and the date of the last valid session.

    Raises:
        HTTPException: If the user is not authenticated (status code 401) or if there is an error fetching the streak (status code 500).
    """
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="User is not authenticated")

        user = users_container.read_item(item=user_id, partition_key=user_id)
        return {
            "streak": user.get("streak", 0),
            "longest_streak": user.get("longest_streak", 0),
            "last_valid_session_date": user.get("last_valid_session_date"),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching streak: {str(e)}")



@router.get("/streaks/{user_id}")
async def get_weekly_streaks(user_id: str):
    """
    Fetches the weekly streaks for a given user.

    This function queries the sessions container to retrieve all sessions for the specified user.
    It then processes these sessions to determine the unique days on which the user has completed sessions.

    Args:
        user_id (str): The ID of the user for whom to fetch the weekly streaks.

    Returns:
        dict: A dictionary containing a list of unique completed days in ISO format.

    Raises:
        HTTPException: If there is an error fetching the streak data.
    """
    try:
        sessions = sessions_container.query_items(
            query="SELECT * FROM c WHERE c.user_id=@user_id",
            parameters=[{"name": "@user_id", "value": user_id}],
            enable_cross_partition_query=True,
        )

        completed_days = set()

        for session in sessions:
            if "start_time" not in session:
                continue  # Skip sessions without a start_time

            start_time = datetime.fromisoformat(session["start_time"])
            completed_days.add(start_time.date().isoformat())

        return {"completed_days": list(completed_days)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching streak data: {str(e)}")
