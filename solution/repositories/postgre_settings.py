import asyncpg
import os
pool = None

DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT"))
DB_NAME = os.getenv("POSTGRES_DB")
DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")



async def init_db():
    global pool
    if pool is None:
        pool = await asyncpg.create_pool(
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME,
            host=DB_HOST,
            port=DB_PORT,
            min_size=1,
            max_size=10
        )
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            email VARCHAR(254) UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            full_name VARCHAR(200) NOT NULL,
            age INT CHECK (age >= 18 AND age <= 120),
            region VARCHAR(32),
            gender VARCHAR(6) CHECK (gender IN ('MALE', 'FEMALE')),
            marital_status VARCHAR(10) CHECK (marital_status IN ('SINGLE', 'MARRIED', 'DIVORCED', 'WIDOWED')),
            role VARCHAR(10) NOT NULL DEFAULT 'USER',
            is_active BOOLEAN NOT NULL DEFAULT TRUE,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
            );
        """)
        await conn.execute("""
        CREATE TABLE IF NOT EXISTS fraud_rules (
            id UUID PRIMARY KEY,
            name VARCHAR(120) NOT NULL UNIQUE,
            description VARCHAR(500),
            dsl_expression TEXT NOT NULL,
            enabled BOOLEAN NOT NULL DEFAULT TRUE,
            priority INTEGER NOT NULL DEFAULT 100,
            created_at TIMESTAMP NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP NOT NULL DEFAULT NOW()
        );""")
    return pool

async def get_db():
    global pool
    if pool is None:
        await init_db()
    async with pool.acquire() as conn:
        yield conn