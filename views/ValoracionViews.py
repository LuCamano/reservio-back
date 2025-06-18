from fastapi import APIRouter, HTTPException, Query, status, Depends
from fastapi.responses import JSONResponse
from app.db import SessionDep
from models import ValoracionBase, Valoracion
from services.ValoracionService import ValoracionService
from typing import Annotated, Optional, List
from uuid import UUID
from app.Auth import get_current_user

router = APIRouter(prefix="/api/v1/valoraciones", tags=["Valoraciones"])

## Obtener todas las valoraciones
@router.get("/", response_model=List[Valoracion])
async def get_valoraciones(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 50,
    order_by: Optional[str] = None,
):
    try:
        valoraciones = ValoracionService.read_all(session, offset=offset, limit=limit, order_by=order_by)
        return valoraciones
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Obtener una valoracion por ID
@router.get("/{valoracion_id}", response_model=Valoracion)
async def get_valoracion(valoracion_id: UUID, session: SessionDep):
    try:
        valoracion = ValoracionService.read(session, obj_id=valoracion_id)
        if not valoracion:
            raise HTTPException(status_code=404, detail="Valoración no encontrada")
        return valoracion
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Crear una valoracion
@router.post("/", response_model=Valoracion, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
async def create_valoracion(session: SessionDep, obj: ValoracionBase):
    try:
        valoracion = ValoracionService.create(session, obj=obj)
        return valoracion
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Actualizar una valoracion
@router.put("/{valoracion_id}", response_model=Valoracion, dependencies=[Depends(get_current_user)])
async def update_valoracion(valoracion_id: UUID, session: SessionDep, obj: ValoracionBase):
    try:
        valoracion = ValoracionService.read(session, obj_id=valoracion_id)
        if not valoracion:
            raise HTTPException(status_code=404, detail="Valoración no encontrada")
        valoracion = ValoracionService.update(session, obj=obj)
        return valoracion
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Eliminar una valoracion
@router.delete("/{valoracion_id}", response_model=dict, dependencies=[Depends(get_current_user)])
async def delete_valoracion(valoracion_id: UUID, session: SessionDep):
    try:
        valoracion = ValoracionService.read(session, obj_id=valoracion_id)
        if not valoracion:
            raise HTTPException(status_code=404, detail="Valoración no encontrada")
        ValoracionService.delete(session, obj_id=valoracion_id)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
