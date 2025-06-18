from fastapi import APIRouter, HTTPException, Query, status, Depends
from fastapi.responses import JSONResponse
from app.db import SessionDep
from models import ComunaBase, Comuna
from services.ComunaService import ComunaService
from typing import Annotated, Optional
from uuid import UUID
from app.Auth import get_current_user

router = APIRouter(prefix="/api/v1/comunas", tags=["Comunas"])

## Obtener todas las comunas
@router.get("/", response_model=list[Comuna])
async def get_comunas(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 50,
    order_by: Optional[str] = None,
):
    try:
        comunas = ComunaService.read_all(session, offset=offset, limit=limit, order_by=order_by)
        return comunas
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
## Obtener una comuna por ID
@router.get("/{comuna_id}", response_model=Comuna)
async def get_comuna(comuna_id: UUID, session: SessionDep):
    try:
        comuna = ComunaService.read(session, obj_id=comuna_id)
        if not comuna:
            raise HTTPException(status_code=404, detail="Comuna no encontrada")
        return comuna
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
## Crear una nueva comuna
@router.post("/", response_model=Comuna, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
async def create_comuna(comuna: ComunaBase, session: SessionDep):
    try:
        new_comuna = ComunaService.create(session, obj=comuna)
        return new_comuna
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Actualizar una comuna existente
@router.put("/{comuna_id}", response_model=Comuna, dependencies=[Depends(get_current_user)])
async def update_comuna(comuna_id: UUID, comuna_data: ComunaBase, session: SessionDep):
    try:
        comuna = ComunaService.read(session, obj_id=comuna_id)
        if not comuna:
            raise HTTPException(status_code=404, detail="Comuna no encontrada")

        # Actualizar los campos de la comuna
        for key, value in comuna_data.model_dump(exclude_unset=True).items():
            setattr(comuna, key, value)

        updated_comuna = ComunaService.update(session, obj=comuna)
        return updated_comuna
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
## Eliminar una comuna
@router.delete("/{comuna_id}", dependencies=[Depends(get_current_user)])
async def delete_comuna(comuna_id: UUID, session: SessionDep):
    try:
        comuna = ComunaService.read(session, obj_id=comuna_id)
        if not comuna:
            raise HTTPException(status_code=404, detail="Comuna no encontrada")

        ComunaService.delete(session, obj_id=comuna_id)
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={"message": "Comuna eliminada exitosamente"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))