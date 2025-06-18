from fastapi import APIRouter, HTTPException, Query, status, Depends
from fastapi.responses import JSONResponse
from app.db import SessionDep
from models import ReservaBase, Reserva
from services.ReservaService import ReservaService
from typing import Annotated, Optional, List
from uuid import UUID
from app.Auth import get_current_user

router = APIRouter(prefix="/api/v1/reservas", tags=["Reservas"], dependencies=[Depends(get_current_user)])

## Obtener todas las reservas
@router.get("/", response_model=List[Reserva])
async def get_reservas(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 50,
    order_by: Optional[str] = None,
):
    try:
        reservas = ReservaService.read_all(session, offset=offset, limit=limit, order_by=order_by)
        return reservas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Obtener una reserva por ID
@router.get("/{reserva_id}", response_model=Reserva)
async def get_reserva(reserva_id: UUID, session: SessionDep):
    try:
        reserva = ReservaService.read(session, obj_id=reserva_id)
        if not reserva:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        return reserva
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Crear una reserva
@router.post("/", response_model=Reserva)
async def create_reserva(session: SessionDep, obj: ReservaBase):
    try:
        reserva = ReservaService.create(session, obj=obj)
        return reserva
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Actualizar una reserva
@router.put("/{reserva_id}", response_model=Reserva)
async def update_reserva(reserva_id: UUID, session: SessionDep, obj: ReservaBase):
    try:
        reserva = ReservaService.read(session, obj_id=reserva_id)
        if not reserva:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        reserva = ReservaService.update(session, obj=obj)
        return reserva
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Eliminar una reserva
@router.delete("/{reserva_id}", response_model=dict)
async def delete_reserva(reserva_id: UUID, session: SessionDep):
    try:
        reserva = ReservaService.read(session, obj_id=reserva_id)
        if not reserva:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        ReservaService.delete(session, obj_id=reserva_id)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
