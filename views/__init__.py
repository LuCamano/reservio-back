from typing import Annotated
from fastapi import APIRouter, HTTPException, Query, UploadFile
from sqlmodel import select
from models import Usuario, UsuarioBase
from app.db import SessionDep
from uuid import UUID
router = APIRouter()

@router.get("/users", response_model=list[Usuario])
async def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10
):
    users = session.exec(select(Usuario).offset(offset).limit(limit)).all()
    if not users:
        raise HTTPException(status_code=404, detail="No se encontraron usuarios")
    return users

@router.post("/users", response_model=Usuario)
async def create_user(
    session: SessionDep,
    user: UsuarioBase
):
    db_user = Usuario.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user