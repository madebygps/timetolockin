from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class User(BaseModel):
    id: str  # GitHub username
    access_token: str
    streak: int = 0

class Session(BaseModel):
    id: str
    user_id: str
    repo: str
    intention: str
    start_time: datetime
    end_time: datetime
    is_valid: Optional[bool] = False
    access_token: str