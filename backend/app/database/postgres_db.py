from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
import os

class PostgresDBManager:
    def __init__(self):
        self._engine = None
        self._session_factory = None
    
    def initialize(self):
        postgres_url = os.getenv(
            "POSTGRES_URL",
            "postgresql+asyncpg://postgres:postgres@localhost:5432/cephalon_onni"
        )
        self._engine = create_async_engine(
            postgres_url,
            pool_size=10,
            max_overflow=20,
            echo=False
        )
        self._session_factory = async_sessionmaker(
            self._engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def get_session(self) -> AsyncSession:
        if not self._engine:
            self.initialize()
        async with self._session_factory() as session:
            yield session
    
    async def create_tables(self):
        from models.postgres.base import Base
        async with self._engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def close(self):
        await self._engine.dispose()

postgres_db = PostgresDBManager()
