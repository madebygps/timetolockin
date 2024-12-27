from fastapi import APIRouter, HTTPException, Request
from datetime import datetime, timedelta

from .database import sessions_container, users_container

router = APIRouter()

@router.get("/streaks/{user_id}")
async def get_weekly_streaks(user_id: str):
    """
    Fetches the weekly streaks for a given user.
    """
    try:
        # Query for valid sessions only
        sessions = sessions_container.query_items(
            query="SELECT * FROM c WHERE c.user_id=@user_id AND c.is_valid=true",
            parameters=[{"name": "@user_id", "value": user_id}],
            enable_cross_partition_query=True,
        )

        completed_days = set()

        for session in sessions:
            start_time = session.get("start_time")
            if not start_time:
                continue  # Skip sessions without a start_time

            try:
                # Convert start_time to a date and add to the set
                start_time_date = datetime.fromisoformat(
                    start_time).date().isoformat()
                completed_days.add(start_time_date)
            except ValueError:
                continue  # Skip invalid dates

        # Sorted list for consistency
        return {"completed_days": sorted(completed_days)}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching streak data: {str(e)}")


@router.get("/streaks")
async def get_streaks(user_id: str, timeframe: str = "weekly"):
    """
    Fetch streak data for the user based on the specified timeframe.

    Args:
        user_id (str): The ID of the user.
        timeframe (str): The timeframe for streak data (weekly, monthly, yearly).

    Returns:
        dict: Streak data for the specified timeframe.

    Raises:
        HTTPException: If the timeframe is invalid or an error occurs.
    """
    try:
        if timeframe not in {"weekly", "monthly", "yearly"}:
            raise HTTPException(status_code=400, detail="Invalid timeframe")

        sessions = sessions_container.query_items(
            query="SELECT * FROM c WHERE c.user_id=@user_id",
            parameters=[{"name": "@user_id", "value": user_id}],
            enable_cross_partition_query=True,
        )

        completed_days = set()
        for session in sessions:
            if "start_time" not in session:
                continue
            start_time = datetime.fromisoformat(session["start_time"])
            completed_days.add(start_time.date())

        # Filter or group data based on the timeframe
        now = datetime.utcnow().date()
        if timeframe == "weekly":
            streak_data = [day.isoformat()
                           for day in completed_days if now - day <= timedelta(days=7)]
        elif timeframe == "monthly":
            streak_data = [day.isoformat(
            ) for day in completed_days if now.month == day.month and now.year == day.year]
        elif timeframe == "yearly":
            streak_data = [day.isoformat()
                           for day in completed_days if now.year == day.year]

        return {"timeframe": timeframe, "completed_days": streak_data}

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error fetching streak data: {str(e)}")
