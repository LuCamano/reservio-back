from fastapi import APIRouter, HTTPException, Query, status, UploadFile, File, Depends, Form
from datetime import time
from app.db import SessionDep
from models import PropiedadBase, Propiedad, PropiedadRead
from services.PropiedadService import PropiedadService
from services.manyToManyServices import UsuarioPropiedadService
from typing import Annotated, Optional, List
from uuid import UUID
from models.manyToMany import UsuarioPropiedad
from app.Auth import get_current_user

router = APIRouter(prefix="/api/v1/propiedades", tags=["Propiedades"])

## Obtener todas las propiedades
@router.get("/", response_model=List[PropiedadRead])
async def get_propiedades(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 50,
    order_by: Optional[str] = None,
    tipo: Optional[str] = Query(None, description="Filtrar por tipo de propiedad"),
    comuna_id: Optional[UUID] = Query(None, description="Filtrar por comuna"),
    precio_min: Optional[int] = Query(None, description="Precio mínimo por hora"),
    precio_max: Optional[int] = Query(None, description="Precio máximo por hora")
):
    try:
        ## Preparar filtros ######################
        filtros = {}
        if tipo:
            filtros["tipo"] = tipo
        if comuna_id:
            filtros["comuna_id"] = comuna_id
        if precio_min is not None:
            filtros["precio_hora__gte"] = precio_min
        if precio_max is not None:
            filtros["precio_hora__lte"] = precio_max
        ##########################################
        # Leer todas las propiedades con los filtros y ordenamiento
        propiedades = PropiedadService.read_all(session, offset=offset, limit=limit, order_by=order_by, filtros=filtros)
        return propiedades
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

## Obtener una propiedad por ID
@router.get("/{propiedad_id}", response_model=PropiedadRead)
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
    nombre: str | None = Form(None),
    descripcion: str = Form(...),
    direccion: str = Form(...),
    tipo: str = Form(...),
    cod_postal: str = Form(...),
    capacidad: int | None = Form(None),
    precio_hora: int = Form(...),
    comuna_id: UUID = Form(...),
    usuario_id: UUID = Form(...),
    hora_apertura: time | None = Form(None),  # Formato "HH:MM"
    hora_cierre: time | None = Form(None),    # Formato "HH:MM"
    images: List[UploadFile] = File(default_factory=list),
    documento: UploadFile | None = File(None)
):
    try:
        # Convertir strings de hora a objetos time si se proporcionaron
        # hora_apertura_obj = None
        # hora_cierre_obj = None
        
        # if hora_apertura:
        #     try:
        #         hour, minute = map(int, hora_apertura.split(':'))
        #         hora_apertura_obj = time(hour, minute)
        #     except ValueError:
        #         raise HTTPException(status_code=400, detail="Formato de hora_apertura inválido. Use HH:MM")
        
        # if hora_cierre:
        #     try:
        #         hour, minute = map(int, hora_cierre.split(':'))
        #         hora_cierre_obj = time(hour, minute)
        #     except ValueError:
        #         raise HTTPException(status_code=400, detail="Formato de hora_cierre inválido. Use HH:MM")
        
        obj = PropiedadBase(
            nombre=nombre,
            descripcion=descripcion,
            direccion=direccion,
            tipo=tipo,
            cod_postal=cod_postal,
            capacidad=capacidad,
            precio_hora=precio_hora,
            comuna_id=comuna_id,
            hora_apertura=hora_apertura,
            hora_cierre=hora_cierre
        )
        propiedad = PropiedadService.create(session, obj=obj, images=images, documento=documento)
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
    nombre: str | None = Form(None),
    descripcion: str = Form(None),
    direccion: str = Form(None),
    tipo: str = Form(None),
    cod_postal: str = Form(None),
    capacidad: int | None = Form(None),
    precio_hora: int = Form(None),
    comuna_id: UUID = Form(None),
    hora_apertura: time | None = Form(None),  # Formato "HH:MM"
    hora_cierre: time | None = Form(None),    # Formato "HH:MM"
    images: List[UploadFile] = File(default_factory=list),
    documento: UploadFile | None = File(None)
):
    try:
        propiedad: Propiedad = PropiedadService.read(session, obj_id=propiedad_id)
        if not propiedad:
            raise HTTPException(status_code=404, detail="Propiedad no encontrada")
        
        # Actualizar solo los campos que se proporcionaron
        if nombre is not None:
            propiedad.nombre = nombre
        if descripcion is not None:
            propiedad.descripcion = descripcion
        if direccion is not None:
            propiedad.direccion = direccion
        if tipo is not None:
            propiedad.tipo = tipo
        if cod_postal is not None:
            propiedad.cod_postal = cod_postal
        if capacidad is not None:
            propiedad.capacidad = capacidad
        if precio_hora is not None:
            propiedad.precio_hora = precio_hora
        if comuna_id is not None:
            propiedad.comuna_id = comuna_id
        if hora_apertura is not None:
            propiedad.hora_apertura = hora_apertura
        if hora_cierre is not None:
            propiedad.hora_cierre = hora_cierre
        # Manejar las horas si se proporcionaron
        # if hora_apertura is not None:
        #     from datetime import time
        #     try:
        #         hour, minute = map(int, hora_apertura.split(':'))
        #         propiedad.hora_apertura = time(hour, minute)
        #     except ValueError:
        #         raise HTTPException(status_code=400, detail="Formato de hora_apertura inválido. Use HH:MM")
        
        # if hora_cierre is not None:
        #     from datetime import time
        #     try:
        #         hour, minute = map(int, hora_cierre.split(':'))
        #         propiedad.hora_cierre = time(hour, minute)
        #     except ValueError:
        #         raise HTTPException(status_code=400, detail="Formato de hora_cierre inválido. Use HH:MM")
        
        # Primero actualizar los campos básicos
        session.add(propiedad)
        session.commit()
        session.refresh(propiedad)
        
        # Manejar las imágenes si se proporcionaron
        if images and any(img.filename for img in images if img):
            propiedad = PropiedadService.update_with_images(session, propiedad_id=propiedad_id, images=images)
        
        # Manejar el documento si se proporcionó
        if documento and documento.filename:
            propiedad = PropiedadService.update_document(session, propiedad_id=propiedad_id, documento=documento)
        
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

## Validar una propiedad
@router.post("/{propiedad_id}/validar", response_model=dict, dependencies=[Depends(get_current_user)])
async def validate_propiedad(propiedad_id: UUID, session: SessionDep):
    try:
        propiedad: Propiedad = PropiedadService.read(session, obj_id=propiedad_id)
        if not propiedad:
            raise HTTPException(status_code=404, detail="Propiedad no encontrada")
        if propiedad.validada:
            raise HTTPException(status_code=400, detail="La propiedad ya está validada")
        
        result = PropiedadService.validate_property(session, propiedad_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
## Cambiar el estado activo de una propiedad
@router.post("/{propiedad_id}/toggle-active", response_model=dict, dependencies=[Depends(get_current_user)])
async def toggle_active_status(propiedad_id: UUID, session: SessionDep):
    try:
        propiedad: Propiedad = PropiedadService.read(session, obj_id=propiedad_id)
        if not propiedad:
            raise HTTPException(status_code=404, detail="Propiedad no encontrada")
        
        result = PropiedadService.toggle_active_status(session, propiedad_id)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))