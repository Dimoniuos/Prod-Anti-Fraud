from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends, HTTPException, APIRouter
from solution.core import check_admin
from solution.models import FraudRule, FraudRuleUpdate, Rule, DSLError, DSLValidateResponse
import asyncpg
from uuid import UUID
from solution.repositories import create_fraud_rule, all_fraud_rules, update_fraud_rule, deactivate_rule, get_fraud_rule_by_id
from solution.service import validate_dsl

router = APIRouter(prefix="/api/v1/fraud-rules")



@router.post("", status_code=201)
async def add_new_rule(data: FraudRule, admin: bool = Depends(check_admin)):
    try:
        rule = await create_fraud_rule(data.name, data.description, data.dslExpression, data.enabled, data.priority)
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=409, detail="Unique Violation Error")
    return rule

@router.get("")
async def get_all_rules(admin: bool = Depends(check_admin)):
    return await all_fraud_rules()

@router.get("/{rule_id}")
async def get_rule_by_id(rule_id: UUID, admin: bool = Depends(check_admin)):
    rule = await get_fraud_rule_by_id(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@router.put("/{rule_id}")
async def update_rule(rule_id: UUID, data: FraudRuleUpdate, admin: bool = Depends(check_admin)):
    try:
        rule = await update_fraud_rule(rule_id, data.name, data.description, data.dslExpression, data.enabled, data.priority)
    except asyncpg.UniqueViolationError:
        raise HTTPException(status_code=409, detail="Rule with this name already exists")

    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@router.delete("/{rule_id}", status_code=204)
async def delete_rule(rule_id: UUID, admin: bool = Depends(check_admin)):
    rule = await deactivate_rule(rule_id)
    if not rule:
        raise HTTPException(status_code=404, detail="Rule not found")
    return rule

@router.post("/validate")
async def validate_rule(rule: Rule, admin: bool = Depends(check_admin)):
    result = validate_dsl(rule.dslExpression)
    if result["isValid"] is True:
        return {
            "isValid": True,
            "normalizedExpression": rule.dslExpression,
            "errors": []
        }
    return {
        "isValid": False,
        "normalizedExpression": None,
        "errors": [
            {
                "code": result["errorCode"],
                "message": result.get("message", "DSL parse error"),
                "position": result.get("position"),
                "near": result.get("near")
            }
        ]
    }