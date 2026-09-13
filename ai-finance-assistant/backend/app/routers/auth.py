import datetime as dt

from fastapi import APIRouter, Depends, HTTPException, status

from app import schemas
from app.security import hash_password, verify_password, create_access_token
from app.storage import json_db, next_id
from app.deps import get_current_user

router = APIRouter(tags=["Authentication"])


@router.post("/register", response_model=schemas.UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: schemas.UserRegister):
    with json_db() as db:
        existing = next((u for u in db["users"] if u["email"] == payload.email), None)
        if existing:
            raise HTTPException(status_code=400, detail="An account with this email already exists.")

        user = {
            "user_id": next_id(db, "users"),
            "name": payload.name,
            "email": payload.email,
            "password_hash": hash_password(payload.password),
            "created_at": dt.datetime.utcnow().isoformat(),
        }
        db["users"].append(user)

    return user


@router.post("/login", response_model=schemas.Token)
def login(payload: schemas.UserLogin):
    with json_db() as db:
        user = next((u for u in db["users"] if u["email"] == payload.email), None)

    if not user or not verify_password(payload.password, user["password_hash"]):
        raise HTTPException(status_code=401, detail="Incorrect email or password.")

    token = create_access_token(subject=user["email"])
    return schemas.Token(access_token=token, user=user)


@router.get("/me", response_model=schemas.UserOut)
def read_me(current_user: dict = Depends(get_current_user)):
    return current_user
