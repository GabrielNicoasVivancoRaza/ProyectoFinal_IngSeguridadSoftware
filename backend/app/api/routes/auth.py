"""Endpoints de autenticacion: registro, login (JWT) y perfil actual."""
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.security import create_access_token
from app.crud import user as crud
from app.db.session import get_db
from app.models.user import User
from app.schemas.auth import Token
from app.schemas.user import UserCreate, UserRead
from app.services.audit import record

router = APIRouter(prefix="/auth", tags=["autenticacion"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserCreate, request: Request, db: Session = Depends(get_db)
) -> UserRead:
    if crud.get_user_by_username(db, payload.username):
        raise HTTPException(status.HTTP_409_CONFLICT, "El nombre de usuario ya existe")
    if crud.get_user_by_email(db, payload.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "El correo ya esta registrado")
    user = crud.create_user(db, payload)
    record(db, "register", detail=user.username, user_id=user.id, request=request)
    return user


@router.post("/login", response_model=Token)
def login(
    request: Request,
    form: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
) -> Token:
    user = crud.authenticate(db, form.username, form.password)
    if user is None:
        record(db, "login_failed", detail=form.username, request=request)
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario o contrasena incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    record(db, "login", detail=user.username, user_id=user.id, request=request)
    return Token(access_token=create_access_token(user.username))


@router.get("/me", response_model=UserRead)
def me(current_user: User = Depends(get_current_user)) -> UserRead:
    return current_user
