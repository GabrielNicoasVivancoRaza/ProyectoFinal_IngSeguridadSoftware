"""Endpoints CRUD de usuarios."""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.crud import user as crud
from app.db.session import get_db
from app.schemas.user import UserCreate, UserRead, UserUpdate

router = APIRouter(prefix="/users", tags=["usuarios"])


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: Session = Depends(get_db)) -> UserRead:
    if crud.get_user_by_username(db, payload.username):
        raise HTTPException(status.HTTP_409_CONFLICT, "El nombre de usuario ya existe")
    if crud.get_user_by_email(db, payload.email):
        raise HTTPException(status.HTTP_409_CONFLICT, "El correo ya esta registrado")
    return crud.create_user(db, payload)


@router.get("", response_model=list[UserRead])
def list_users(
    include_inactive: bool = False, db: Session = Depends(get_db)
) -> list[UserRead]:
    return crud.list_users(db, include_inactive=include_inactive)


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: int, db: Session = Depends(get_db)) -> UserRead:
    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    return user


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int, payload: UserUpdate, db: Session = Depends(get_db)
) -> UserRead:
    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    if payload.email and payload.email != user.email:
        existente = crud.get_user_by_email(db, payload.email)
        if existente and existente.id != user_id:
            raise HTTPException(status.HTTP_409_CONFLICT, "El correo ya esta registrado")
    return crud.update_user(db, user, payload)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: int, db: Session = Depends(get_db)) -> None:
    user = crud.get_user(db, user_id)
    if user is None:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Usuario no encontrado")
    crud.soft_delete_user(db, user)
