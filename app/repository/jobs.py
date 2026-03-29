async def get_jobs(conn, query="", limit=20, offset=0):
    return await conn.fetch("""
        SELECT * FROM jobs
        WHERE title ILIKE $1
        ORDER BY posted_at DESC
        LIMIT $2 OFFSET $3
    """, f"%{query}%", limit, offset)