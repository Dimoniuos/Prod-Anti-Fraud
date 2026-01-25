from fastapi import APIRouter, HTTPException, Depends, Query
from fastapi.security import OAuth2PasswordBearer
from solution.core import hash_password, get_token, verify_password, get_id_from_token
from solution.models import RegisterRequest, LoginRequest, RegisterRequestByAdmin, UserUpdateBase, UserUpdateAdmin
from solution.repositories import exist_user, create_user
from solution.repositories.users_data import get_user_by_email, get_user_by_id, get_all_users, deactivate_user, update_user_by_id

router = APIRouter(prefix="/api/v1")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")



@router.post("/auth/register", status_code=201)
async def register_user(data: RegisterRequest):
    if await exist_user(data.email):
        raise HTTPException(
            status_code=409, detail="User with this email already exists."
        )
    hashed_password = hash_password(data.password)
    user = await create_user(data.email, hashed_password, data.fullName, data.age, data.region, str(data.gender) if data.gender else None, str(data.maritalStatus) if data.maritalStatus else None, "USER")
    token = get_token(user["id"], user["role"])
    return {
        "accessToken": token,
        "expiresIn": 3600,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "fullName": user["full_name"],
            "age": user["age"],
            "region": user["region"],
            "gender": user["gender"],
            "maritalStatus": user["marital_status"],
            "role": user["role"],
            "isActive": user["is_active"],
            "createdAt": user["created_at"],
            "updatedAt": user["updated_at"],
        },
    }

@router.post("/auth/login")
async def login_user(data: LoginRequest):
    if not await exist_user(data.email):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    user = await get_user_by_email(data.email)
    if not verify_password(data.password, user["hashed_password"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    if not user["is_active"]:
        raise HTTPException(status_code=423, detail="User is not active")
    token = get_token(user["id"], user["role"])
    return {
        "accessToken": token,
        "expiresIn": 3600,
        "user": {
            "id": user["id"],
            "email": user["email"],
            "fullName": user["full_name"],
            "age": user["age"],
            "region": user["region"],
            "gender": user["gender"],
            "maritalStatus": user["marital_status"],
            "role": user["role"],
            "isActive": user["is_active"],
            "createdAt": user["created_at"],
            "updatedAt": user["updated_at"],
        },
    }


async def get_some_user(token: str = Depends(oauth2_scheme)):
    if not token:
        raise HTTPException(status_code=401)
    user_id = get_id_from_token(token)
    user = await get_user_by_id(user_id)
    if not user or not user["isActive"]:
        raise HTTPException(status_code=401)
    return user


@router.get("/users/me")
async def user_get_me(user = Depends(get_some_user)):
    return user

@router.get("/users/{user_id}")
async def get_by_user_id(user_id: int, user = Depends(get_some_user)):
    if user["role"] != "ADMIN":
        if user["id"] != user_id:
            raise HTTPException(status_code=403, detail="Forbidden")
        return user
    return user

@router.get("/users")
async def get_all_users_by_admin(page: int = Query(0, ge=0), size:int = Query(20, ge=1, le=100), user = Depends(get_some_user)):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Forbidden")
    users, total = await get_all_users(size, page*size)
    return {
        "items": [dict(user) for user in users],
        "total": total,
        "page": page,
        "size": size
    }

@router.delete("/users/{user_id}", status_code=204)
async def delete_user(user_id: int, user = Depends(get_some_user)):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Forbidden")
    await deactivate_user(user_id)

@router.post("/users")
async def admin_create_new_user(new_user: RegisterRequestByAdmin, user = Depends(get_some_user)):
    if user["role"] != "ADMIN":
        raise HTTPException(status_code=403, detail="Forbidden")
    if await exist_user(new_user.email):
        raise HTTPException(
            status_code=409, detail="User with this email already exists."
        )
    hashed_password = hash_password(new_user.password)
    created_user = await create_user(new_user.email, hashed_password, new_user.fullName, new_user.age, new_user.region, str(new_user.gender) if new_user.gender else None, str(new_user.maritalStatus) if new_user.maritalStatus else None, str(new_user.role))
    return created_user

@router.put("/api/v1/users/me")
async def update_my_profile(data: UserUpdateBase, user = Depends(get_some_user)):
    updated_user = await update_user_by_id(user["id"], data.dict(exclude_unset=False))
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.put("/api/v1/users/{user_id}")
async def update_user(
    user_id: str,
    payload: dict,
    user = Depends(get_some_user)
):
    if user["role"] == "ADMIN":
        schema = UserUpdateAdmin
    else:
        schema = UserUpdateBase
    try:
        data = schema(**payload).dict(exclude_unset=False)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    if user["role"] != "ADMIN" and str(user["id"]) != str(user_id):
        raise HTTPException(status_code=403, detail="Forbidden")
    if user["role"] != "ADMIN" and ("role" in data or "isActive" in data):
        raise HTTPException(status_code=403, detail="Cannot change role or isActive")
    updated_user = await update_user_by_id(user_id, data)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user