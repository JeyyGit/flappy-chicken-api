from fastapi import FastAPI, HTTPException, Query, Header, Depends
import asyncpg
import datetime
from dotenv import load_dotenv
import os
import pytz
from models import ScoreEntry, ScoreResponse

load_dotenv()

app = FastAPI()


class Database:
    async def create_pool(self):
        self.pool = await asyncpg.create_pool(
            host=os.getenv("DBHOST"),
            database=os.getenv("DBNAME"),
            user=os.getenv("DBUSER"),
            password=os.getenv("DBPASS"),
        )


db = Database()

async def authorize(api_key: str = Header(None)):
    if api_key != os.getenv("APIKEY"):
        raise HTTPException(status_code=401, detail="Unauthorized")
    return True

@app.on_event("startup")
async def startup():
    await db.create_pool()


@app.on_event("shutdown")
async def shutdown():
    await db.pool.close()


@app.post("/leaderboard", response_model=ScoreResponse)
async def add_score(username: str = Query(...), score: int = Query(...), authorized: bool = Depends(authorize)):
    query = """
    INSERT INTO leaderboard (username, score, timestamp)
    VALUES ($1, $2, $3)
    RETURNING id, username, score, timestamp
    """
    timestamp = datetime.datetime.now(tz=pytz.timezone("Asia/Jakarta")).replace(
        tzinfo=None
    )
    record = await db.pool.fetchrow(query, username, score, timestamp)
    if not record:
        raise HTTPException(status_code=500, detail="Failed to insert score")
    return ScoreResponse(**record)


@app.get("/leaderboard/top", response_model=list[ScoreResponse])
async def get_top_leaderboard(limit: int = Query(10, ge=1), authorized: bool = Depends(authorize)):
    query = """
    SELECT id, username, score, timestamp
    FROM leaderboard
    ORDER BY score DESC
    LIMIT $1
    """
    records = await db.pool.fetch(query, limit)
    return [ScoreResponse(**record) for record in records]


@app.get("/leaderboard/user/{username}", response_model=list[ScoreResponse])
async def get_user_leaderboard(username: str, authorized: bool = Depends(authorize)):
    query = """
    SELECT id, username, score, timestamp
    FROM leaderboard
    WHERE username = $1
    ORDER BY score DESC
    """
    records = await db.pool.fetch(query, username)
    return [ScoreResponse(**record) for record in records]
