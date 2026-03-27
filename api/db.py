import os
import asyncpg
from dotenv import load_dotenv

load_dotenv()
pool: asyncpg.Pool = None

async def init_pool():
    global pool
    pool = await asyncpg.create_pool(os.environ["DATABASE_URL"], min_size=5, max_size=20)

async def get_pool():
    return pool
