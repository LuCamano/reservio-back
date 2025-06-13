from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from app.db import SessionDep
from models import UsuarioBase
from services.UsuarioService import UsuarioService
from typing import Annotated

router = APIRouter(tags=["Usuarios"])

@router.get("/registrar", response_model=JSONResponse)
async def registrar(session: SessionDep, user: UsuarioBase):
    try:
        UsuarioService.create(session, user)
        return JSONResponse(status_code=201, content={"message": "Usuario registrado exitosamente"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/usuarios", response_model=list[UsuarioBase])
async def obtener_usuarios(session: SessionDep, offset: int = 0, limit: Annotated[int, Query(le=100)] = 100, order_by: str | None = None):
    try:
        usuarios = UsuarioService.read_all(session=session, offset=offset, limit=limit, order_by=order_by)
        if not usuarios:
            raise HTTPException(status_code=404, detail="No se encontraron usuarios")
        return usuarios
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
