from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from app.db import SessionDep
from models import UsuarioRead, Usuario
from services.UsuarioService import UsuarioService
from typing import Annotated, Optional
from app.Auth import get_current_user
from datetime import datetime

router = APIRouter(prefix="/api/v1/usuarios", tags=["Usuarios"], dependencies=[Depends(get_current_user)])

## Obtener todos los usuarios y filtrar por activo/inactivo
@router.get("/", response_model=list[UsuarioRead])
async def get_usuarios(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 50,
    order_by: str | None = None,
    activo: Optional[bool] = Query(None, description="Filtrar por usuarios activos (True) o inactivos (False)")
):
    try:
        ## Preparar filtros ######################
        filtros = {}
        ##########################################
        usuarios = UsuarioService.read_all(session=session, offset=offset, limit=limit, order_by=order_by, filtros=filtros)
        if not usuarios:
            raise HTTPException(status_code=404, detail="No se encontraron usuarios")
        return usuarios
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Obtener un usuario por ID
@router.get("/{usuario_id}", response_model=UsuarioRead)
async def get_usuario(usuario_id: UUID, session: SessionDep):
    try:
        usuario = UsuarioService.read(session, obj_id=usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        return usuario
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Bloquear a un usuario
@router.post("/{usuario_id}/bloquear")
async def bloquear_usuario(usuario_id: UUID, administrador_id: UUID, motivo: str, session: SessionDep, fecha_desbloqueo: Optional[datetime] = Query(None, description="Fecha de desbloqueo (opcional)")):
    try:
        usuario: Usuario = UsuarioService.read(session, obj_id=usuario_id)
        isActive = UsuarioService.isActive(session, usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        if not isActive:
            raise HTTPException(status_code=400, detail="El usuario ya está bloqueado")
        
        UsuarioService.block_user(session=session, user_id=usuario_id, motivo=motivo, fecha_desbloqueo=fecha_desbloqueo, administrador_id=administrador_id)
        return JSONResponse(status_code=200, content={"message": "Usuario bloqueado exitosamente"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
## Desbloquear a un usuario
@router.post("/{usuario_id}/desbloquear")
async def desbloquear_usuario(usuario_id: UUID, session: SessionDep):
    try:
        usuario: Usuario = UsuarioService.read(session, obj_id=usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        if UsuarioService.isActive(session, usuario_id):
            raise HTTPException(status_code=400, detail="El usuario ya está activo")

        UsuarioService.unblock_user(session, usuario_id)
        return JSONResponse(status_code=200, content={"message": "Usuario desbloqueado exitosamente"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Modificar datos de un usuario
@router.put("/{usuario_id}", response_model=UsuarioRead)
async def update_usuario(usuario_id: UUID, usuario_data: UsuarioRead, session: SessionDep):
    try:
        usuario = UsuarioService.read(session, obj_id=usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        
        # Actualizar los campos del usuario
        for key, value in usuario_data.model_dump(exclude_unset=True).items():
            setattr(usuario, key, value)
        
        updated_usuario = UsuarioService.update(session, obj=usuario)
        return updated_usuario
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))