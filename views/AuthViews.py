from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.db import SessionDep
from models import UsuarioRead
from models.UsuarioModel import Token, UsuarioBase
from app.Auth import create_access_token, verify_password, get_current_user
from datetime import timedelta
from services.UsuarioService import UsuarioService

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UsuarioRead)
async def register(
    session: SessionDep,
    user: UsuarioBase
):
    existing_user = UsuarioService.get_by_email(session, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Email ya registrado")
    return UsuarioService.create(session, user)

@router.post("/login", response_model=Token)
async def login(
    session: SessionDep,
    form_data: OAuth2PasswordRequestForm = Depends()
):
    user = UsuarioService.get_by_email(session, form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")

    access_token = create_access_token(data={"sub": user.email})
    token = Token(access_token=access_token, token_type="bearer")
    return token

@router.get("/me", response_model=UsuarioRead)
async def read_current_user(
    current_user: UsuarioRead = Depends(get_current_user)
):
    return current_user