import datetime
from pydantic import BaseModel


class ScoreResponse(BaseModel):
    id: int
    username: str
    score: int
    timestamp: datetime.datetime
