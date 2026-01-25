from .postgre_settings import get_db
import uuid
import asyncpg


async def create_fraud_rule(name, description, dsl_expression, enabled, priority):
    rule_id = uuid.uuid4()
    try:
        async for conn in get_db():
            return await conn.fetchrow(
            """
            INSERT INTO fraud_rules
            (id, name, description, dsl_expression, enabled, priority)
            VALUES ($1, $2, $3, $4, $5, $6)
            RETURNING
                id,
                name,
                description,
                dsl_expression AS "dslExpression",
                enabled,
                priority,
                created_at AS "createdAt",
                updated_at AS "updatedAt"
            """,
            rule_id,
            name,
            description,
            dsl_expression,
            enabled,
            priority,
        )
    except asyncpg.UniqueViolationError:
        raise


async def all_fraud_rules():
    async for conn in get_db():
        return await conn.fetch(
        """
        SELECT
            id,
            name,
            description,
            dsl_expression AS "dslExpression",
            enabled,
            priority,
            created_at AS "createdAt",
            updated_at AS "updatedAt"
        FROM fraud_rules
        ORDER BY priority ASC
        """
    )


async def get_fraud_rule_by_id(rule_id):
    async for conn in get_db():
        return await conn.fetchrow(
        """
        SELECT
            id,
            name,
            description,
            dsl_expression AS "dslExpression",
            enabled,
            priority,
            created_at AS "createdAt",
            updated_at AS "updatedAt"
        FROM fraud_rules
        WHERE id = $1
        """,
        rule_id
    )


async def update_fraud_rule(rule_id, name, description, dsl_expression, enabled, priority):
    try:
        async for conn in get_db():
            return await conn.fetchrow(
            """
            UPDATE fraud_rules
            SET
                name=$1,
                description=$2,
                dsl_expression=$3,
                enabled=$4,
                priority=$5,
                updated_at=now()
            WHERE id=$6
            RETURNING
                id,
                name,
                description,
                dsl_expression AS "dslExpression",
                enabled,
                priority,
                created_at AS "createdAt",
                updated_at AS "updatedAt"
            """,
            name,
            description,
            dsl_expression,
            enabled,
            priority,
            rule_id
        )
    except asyncpg.UniqueViolationError:
        raise


async def deactivate_rule(rule_id):
    async for conn in get_db():
        return await conn.fetchrow(
        """
        UPDATE fraud_rules
        SET enabled=false, updated_at=now()
        WHERE id=$1
        RETURNING
            id,
            name,
            description,
            dsl_expression AS "dslExpression",
            enabled,
            priority,
            created_at AS "createdAt",
            updated_at AS "updatedAt"
        """,
        rule_id
    )
