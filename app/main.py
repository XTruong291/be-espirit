from fastapi import FastAPI, Depends, HTTPException
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import AsyncSession
# pyrefly: ignore [missing-import]
from sqlalchemy import text
from app.core.database import get_db

app = FastAPI(title="FastAPI Async MySQL Starter")

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI Async MySQL Starter API"}

@app.get("/db-check")
async def db_check(db: AsyncSession = Depends(get_db)):
    try:
        # Execute raw query SELECT 1 to verify connection
        result = await db.execute(text("SELECT 1"))
        result.fetchone()
        return {"database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Database connection failed: {str(e)}"
        )
