from .postgre_settings import get_db
import os
from solution.core import hash_password

async def exist_user(email: str):
    async for conn in get_db():
        return await conn.fetchval("SELECT EXISTS(SELECT 1 FROM users WHERE email = $1)", email)


async def create_user(email: str, hashed_password: str, full_name: str, age: int, region: str, gender: str, marital_status: str, role: str):
    async for conn in get_db():
        await conn.execute("""INSERT INTO users (email, hashed_password, full_name, age, region, gender, marital_status, role) VALUES ($1, $2, $3, $4, $5, $6, $7, $8)""", email, hashed_password, full_name, age, region, gender, marital_status, role)
        user = await conn.fetch("SELECT * FROM users WHERE email = $1", email)
        return [dict(line) for line in user][0]

async def create_admin_user():
    email = os.getenv("ADMIN_EMAIL", "admin@mail.ru")
    fullname = os.getenv("ADMIN_FULLNAME", "Test Test")
    password = os.getenv("ADMIN_PASSWORD", "123123123aA!")
    if not await exist_user(email):
        hashed_password = hash_password(password)
        await create_user(
            email=email,
            hashed_password=hashed_password,
            full_name=fullname,
            age=18,
            region="RU",
            gender="MALE",
            marital_status="SINGLE",
            role="ADMIN"
        )

async def get_user_by_email(email: str):
    async for conn in get_db():
        user = await conn.fetch("SELECT * FROM users WHERE email = $1", email)
        return [dict(line) for line in user][0]

async def get_user_by_id(user_id: int):
    async for conn in get_db():
        user = await conn.fetch("""SELECT id,
                                           email,
                                           full_name      AS "fullName",
                                           age,
                                           region,
                                           gender,
                                           marital_status AS "maritalStatus",
                                           role,
                                           is_active      AS "isActive",
                                           created_at     AS "createdAt",
                                           updated_at     AS "updatedAt"
                                    FROM users WHERE id = $1""", user_id)
        return [dict(line) for line in user][0]

async def get_all_users(limit: int, offset: int):
    async for conn in get_db():
        users = await conn.fetch("""SELECT id,
                                           email,
                                           full_name      AS "fullName",
                                           age,
                                           region,
                                           gender,
                                           marital_status AS "maritalStatus",
                                           role,
                                           is_active      AS "isActive",
                                           created_at     AS "createdAt",
                                           updated_at     AS "updatedAt"
                                    FROM users
                                    ORDER BY created_at
                                    LIMIT $1 OFFSET $2""", limit, offset)
        total = await conn.fetchval("SELECT COUNT(*) FROM users")
        return users, total


async def deactivate_user(user_id: int):
    async for conn in get_db():
        await conn.execute("""UPDATE users SET is_active = FALSE WHERE id = $1""", user_id)
        await conn.commit()


async def update_user_by_id(user_id: int, data: dict):
    set_parts = []
    values = []
    i = 1
    for key, value in data.items():
        set_parts.append(f'"{key}" = ${i}')
        values.append(value)
        i += 1
    set_parts.append(f'"updatedAt" = NOW()')
    values.append(user_id)
    query = f"""
          UPDATE users
          SET {', '.join(set_parts)}
          WHERE id = ${i}
          RETURNING *
      """
    async for conn in get_db():
        row = await conn.fetchrow(query, *values)
        if row:
            return dict(row)
        return None