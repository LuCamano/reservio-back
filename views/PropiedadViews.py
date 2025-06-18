from fastapi import APIRouter, HTTPException, Query, status, UploadFile, File, Depends, Form
from fastapi.responses import JSONResponse
from app.db import SessionDep
from models import PropiedadBase, Propiedad
from services.PropiedadService import PropiedadService
from services.manyToManyServices import UsuarioPropiedadService
from typing import Annotated, Optional, List
from uuid import UUID
from models.manyToMany import UsuarioPropiedad
from app.Auth import get_current_user

router = APIRouter(prefix="/api/v1/propiedades", tags=["Propiedades"])

## Obtener todas las propiedades
@router.get("/", response_model=List[Propiedad])
async def get_propiedades(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 50,
    order_by: Optional[str] = None,
):
    try:
        propiedades = PropiedadService.read_all(session, offset=offset, limit=limit, order_by=order_by)
        return propiedades
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Obtener una propiedad por ID
@router.get("/{propiedad_id}", response_model=Propiedad)
async def get_propiedad(propiedad_id: UUID, session: SessionDep):
    try:
        propiedad = PropiedadService.read(session, obj_id=propiedad_id)
        if not propiedad:
            raise HTTPException(status_code=404, detail="Propiedad no encontrada")
        return propiedad
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Crear una propiedad con imágenes
@router.post("/", response_model=Propiedad, status_code=status.HTTP_201_CREATED, dependencies=[Depends(get_current_user)])
async def create_propiedad(
    session: SessionDep,
    nombre: str = Form(...),
    descripcion: str = Form(...),
    direccion: str = Form(...),
    tipo: str = Form(...),
    cod_postal: str = Form(...),
    capacidad: int = Form(...),
    precio_hora: int = Form(...),
    comuna_id: UUID = Form(...),
    usuario_id: UUID = Form(...),
    images: List[UploadFile] = File(default_factory=list)
):
    try:
        obj = PropiedadBase(
            nombre=nombre,
            descripcion=descripcion,
            direccion=direccion,
            tipo=tipo,
            cod_postal=cod_postal,
            capacidad=capacidad,
            precio_hora=precio_hora,
            comuna_id=comuna_id
        )
        propiedad = PropiedadService.create(session, obj=obj, images=images)
        # Crear relación usuario-propiedad correctamente
        usuario_propiedad = UsuarioPropiedad(usuario_id=usuario_id, propiedad_id=propiedad.id)
        UsuarioPropiedadService.create(session, obj=usuario_propiedad)
        return propiedad
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Actualizar una propiedad
@router.put("/{propiedad_id}", response_model=Propiedad, dependencies=[Depends(get_current_user)])
async def update_propiedad(
    propiedad_id: UUID,
    session: SessionDep,
    obj: PropiedadBase,
    images: List[UploadFile] = File(default_factory=list)
):
    try:
        propiedad = PropiedadService.read(session, obj_id=propiedad_id)
        if not propiedad:
            raise HTTPException(status_code=404, detail="Propiedad no encontrada")
        propiedad = PropiedadService.update(session, obj=obj)
        if images:
            propiedad = PropiedadService.create(session, obj=obj, images=images)
        return propiedad
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Eliminar una propiedad
@router.delete("/{propiedad_id}", response_model=dict, dependencies=[Depends(get_current_user)])
async def delete_propiedad(propiedad_id: UUID, session: SessionDep):
    try:
        propiedad = PropiedadService.read(session, obj_id=propiedad_id)
        if not propiedad:
            raise HTTPException(status_code=404, detail="Propiedad no encontrada")
        PropiedadService.delete(session, obj_id=propiedad_id)
        return {"ok": True}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
