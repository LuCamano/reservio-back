from fastapi import APIRouter, HTTPException, Query, status, Depends
from fastapi.responses import JSONResponse
from app.db import SessionDep
from models import RegionBase, Region
from services.RegionService import RegionService
from typing import Annotated, Optional
from uuid import UUID
from app.Auth import get_current_user

router = APIRouter(prefix="/api/v1/regiones", tags=["Regiones"])

## Obtener todas las regiones
@router.get("/", response_model=list[Region])
async def get_regiones(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 50,
    order_by: Optional[str] = None,
    ):
    try:
        regiones = RegionService.read_all(session, offset=offset, limit=limit, order_by=order_by)
        return regiones
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
## Obtener una región por ID
@router.get("/{region_id}", response_model=Region)
async def get_region(region_id: UUID, session: SessionDep):
    try:
        region = RegionService.read(session, obj_id=region_id)
        if not region:
            raise HTTPException(status_code=404, detail="Región no encontrada")
        return region
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
## Crear una nueva región
@router.post("/", response_model=Region, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
async def create_region(region: RegionBase, session: SessionDep):
    try:
        new_region = RegionService.create(session, obj=region)
        return new_region
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Actualizar una región existente
@router.put("/{region_id}", response_model=Region, dependencies=[Depends(get_current_user)])
async def update_region(region_id: UUID, region_data: RegionBase, session: SessionDep):
    try:
        region = RegionService.read(session, obj_id=region_id)
        if not region:
            raise HTTPException(status_code=404, detail="Región no encontrada")

        # Actualizar los campos de la región
        for key, value in region_data.model_dump(exclude_unset=True).items():
            setattr(region, key, value)

        updated_region = RegionService.update(session, obj=region)
        return updated_region
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
## Eliminar una región
@router.delete("/{region_id}", dependencies=[Depends(get_current_user)])
async def delete_region(region_id: UUID, session: SessionDep):
    try:
        region = RegionService.read(session, obj_id=region_id)
        if not region:
            raise HTTPException(status_code=404, detail="Región no encontrada")
        
        RegionService.delete(session, obj_id=region_id)
        return JSONResponse(status_code=status.HTTP_204_NO_CONTENT, content={"message": "Región eliminada exitosamente"})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))