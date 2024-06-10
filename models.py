import datetime
from pydantic import BaseModel

class ScoreEntry(BaseModel):
    username: str
    score: int


class ScoreResponse(BaseModel):
    id: int
    username: str
    score: int
    timestamp: datetime.datetime