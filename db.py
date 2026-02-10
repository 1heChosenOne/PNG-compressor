from sqlalchemy.ext.asyncio import create_async_engine
from config import db_settings
from sqlalchemy import text

engine=create_async_engine(url=db_settings.DB_GET_URL,echo=True)

async def get_async_conn():
    async with engine.connect() as conn:
        yield conn
        
async def create_tables():
    async with engine.begin() as conn:
        await conn.execute(text("""CREATE TABLE IF NOT EXISTS compresses (
                        id SERIAL PRIMARY KEY,
                        datetime TIMESTAMP DEFAULT NOW(),
                        file_name VARCHAR(255))"""))
        
