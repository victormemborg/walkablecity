from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from db import init_pool, get_pool
from models import BoundingBox

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_pool()
    yield

app = FastAPI(lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000", "http://localhost:3002",  "http://127.0.0.1:3002"]
)

@app.get("/api/bbox")
async def get_grid(bbox: BoundingBox = Depends(), pool=Depends(get_pool)):
    sql_string = f"""
        SELECT MIN(score), MAX(score)
        FROM {bbox.table}
        WHERE geometry && ST_MakeEnvelope($1, $2, $3, $4, 4326)
        """
    async with pool.acquire() as conn:
        row = await conn.fetchrow(sql_string, bbox.minlon, bbox.minlat, bbox.maxlon, bbox.maxlat)
    return dict(row)