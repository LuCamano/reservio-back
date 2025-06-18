from uuid import UUID
from fastapi import APIRouter, HTTPException, Query, Depends
from fastapi.responses import JSONResponse
from app.db import SessionDep
from models import UsuarioRead, Usuario
from services.UsuarioService import UsuarioService
from typing import Annotated, Optional
from app.Auth import get_current_user

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
        if activo is not None:
            filtros["activo"] = activo
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
async def bloquear_usuario(usuario_id: UUID, session: SessionDep):
    try:
        usuario: Usuario = UsuarioService.read(session, obj_id=usuario_id)
        if not usuario:
            raise HTTPException(status_code=404, detail="Usuario no encontrado")
        if not usuario.activo:
            raise HTTPException(status_code=400, detail="El usuario ya está bloqueado")
        
        usuario.activo = False
        UsuarioService.update(session, obj=usuario)
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
        if usuario.activo:
            raise HTTPException(status_code=400, detail="El usuario ya está activo")
        
        usuario.activo = True
        UsuarioService.update(session, obj=usuario)
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