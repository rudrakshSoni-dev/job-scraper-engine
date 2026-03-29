import asyncpg

pool = None

async def init_db():
    global pool
    pool = await asyncpg.create_pool(
        dsn="postgresql://user:pass@postgres:5432/jobs",
        min_size=1,
        max_size=5
    )

async def get_conn():
    return pool
