import ssl
from typing import AsyncGenerator
# pyrefly: ignore [missing-import]
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# Bật SSL khi kết nối ra Cloud (như TiDB Cloud), tắt khi chạy localhost/docker-compose local
connect_args = {}
if settings.MYSQL_SERVER not in ("localhost", "127.0.0.1", "db"):
    ssl_context = ssl.create_default_context()
    connect_args["ssl"] = ssl_context

engine = create_async_engine(
    settings.DATABASE_URL,
    connect_args=connect_args,
    echo=False,  # Tắt echo để log Render gọn hơn
    pool_pre_ping=True,
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session