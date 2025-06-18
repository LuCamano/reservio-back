from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import JSONResponse
from app.Auth import get_current_user
from app.db import SessionDep
from models import BoletaBase, Boleta
from services.BoletaService import BoletaService
from typing import Annotated, Optional, List
from uuid import UUID

router = APIRouter(prefix="/api/v1/boletas", tags=["Boletas"], dependencies=[Depends(get_current_user)])

## Obtener todas las boletas
@router.get("/", response_model=List[Boleta])
async def get_boletas(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 50,
    order_by: Optional[str] = None,
):
    try:
        boletas = BoletaService.read_all(session, offset=offset, limit=limit, order_by=order_by)
        return boletas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Obtener una boleta por ID
@router.get("/{boleta_id}", response_model=Boleta)
async def get_boleta(boleta_id: UUID, session: SessionDep):
    try:
        boleta = BoletaService.read(session, obj_id=boleta_id)
        if not boleta:
            raise HTTPException(status_code=404, detail="Boleta no encontrada")
        return boleta
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Crear una boleta
@router.post("/", response_model=Boleta)
async def create_boleta(session: SessionDep, obj: BoletaBase):
    try:
        boleta = BoletaService.create(session, obj=obj)
        return boleta
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Actualizar una boleta
@router.put("/{boleta_id}", response_model=Boleta)
async def update_boleta(boleta_id: UUID, session: SessionDep, obj: BoletaBase):
    try:
        boleta = BoletaService.read(session, obj_id=boleta_id)
        if not boleta:
            raise HTTPException(status_code=404, detail="Boleta no encontrada")
        boleta = BoletaService.update(session, obj=obj)
        return boleta
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Eliminar una boleta
@router.delete("/{boleta_id}", response_model=dict)
async def delete_boleta(boleta_id: UUID, session: SessionDep):
    try:
        boleta = BoletaService.read(session, obj_id=boleta_id)
        if not boleta:
            raise HTTPException(status_code=404, detail="Boleta no encontrada")
        BoletaService.delete(session, obj_id=boleta_id)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
