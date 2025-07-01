from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from app.db import SessionDep
from models import UsuarioRead
from models.UsuarioModel import Token, UsuarioBase, RefreshTokenRequest
from app.Auth import create_access_token, create_refresh_token, verify_password, get_current_user, decode_refresh_token
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
    
    # Validar que el usuario no esté bloqueado
    if not UsuarioService.isActive(session, user.id):
        raise HTTPException(
            status_code=403, 
            detail="Usuario bloqueado. Contacte al administrador para más información."
        )

    access_token = create_access_token(data={"sub": user.email})
    refresh_token = create_refresh_token(data={"sub": user.email})
    token = Token(access_token=access_token, refresh_token=refresh_token, token_type="bearer")
    return token

@router.get("/me", response_model=UsuarioRead)
async def read_current_user(
    current_user: UsuarioRead = Depends(get_current_user)
):
    return current_user

@router.post("/refresh", response_model=Token)
async def refresh_token(
    session: SessionDep,
    refresh_request: RefreshTokenRequest
):
    """
    Endpoint para refrescar el access token usando un refresh token válido
    """
    payload = decode_refresh_token(refresh_request.refresh_token)
    email: str = payload.get("sub")
    
    if not email:
        raise HTTPException(
            status_code=401,
            detail="Refresh token inválido"
        )
    
    # Verificar que el usuario aún existe
    user = UsuarioService.get_by_email(session, email)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Usuario no encontrado"
        )
    
    # Validar que el usuario no esté bloqueado
    if not UsuarioService.isActive(session, user.id):
        raise HTTPException(
            status_code=403,
            detail="Usuario bloqueado. Contacte al administrador para más información."
        )
    
    # Crear nuevos tokens
    new_access_token = create_access_token(data={"sub": user.email})
    new_refresh_token = create_refresh_token(data={"sub": user.email})
    
    return Token(
        access_token=new_access_token, 
        refresh_token=new_refresh_token, 
        token_type="bearer"
    )

@router.post("/logout")
async def logout():
    """
    Endpoint para logout (en el frontend se debe eliminar los tokens del almacenamiento)
    """
    return {"message": "Logout exitoso"}

@router.get("/status")
async def get_user_status(
    session: SessionDep,
    current_user: UsuarioRead = Depends(get_current_user)
):
    """
    Endpoint para obtener el estado de bloqueo del usuario actual.
    Solo accessible si el usuario está activo (no bloqueado).
    """
    is_active = UsuarioService.isActive(session, current_user.id)
    active_block = UsuarioService.get_active_block(session, current_user.id)
    
    response = {
        "user_id": current_user.id,
        "is_active": is_active,
        "blocked": not is_active
    }
    
    if active_block:
        response.update({
            "block_details": {
                "motivo": active_block.motivo,
                "fecha_bloqueo": active_block.fecha_bloqueo,
                "fecha_desbloqueo": active_block.fecha_desbloqueo,
                "administrador_id": active_block.administrador_id
            }
        })
    
    return response