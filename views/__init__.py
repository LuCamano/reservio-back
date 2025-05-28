from typing import Annotated
from fastapi import APIRouter, HTTPException, Query
from sqlmodel import select
from models import Usuario, UsuarioBase
from app.db import SessionDep
from uuid import UUID
router = APIRouter()

@router.get("/users", response_model=list[Usuario])
async def read_users(
    session: SessionDep,
    offset: int = 0,
    limit: Annotated[int, Query(le=100)] = 10
):
    users = session.exec(select(Usuario).offset(offset).limit(limit)).all()
    if not users:
        raise HTTPException(status_code=404, detail="No se encontraron usuarios")
    return users

@router.post("/users", response_model=Usuario)
async def create_user(
    session: SessionDep,
    user: UsuarioBase
):
    db_user = Usuario.model_validate(user)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    return db_user

# from models import (Autor, AutorBase, Libro, LibroBase)

# @router.get("/")
# async def read_root():
#     return {"message": "Hola papus"}

# @router.get("/autores", response_model=list[Autor])
# async def read_autores(
#     session: SessionDep,
#     offset: int = 0,
#     limit: Annotated[int, Query(le=100)] = 10,
# ):
#     autores = session.exec(select(Autor).offset(offset).limit(limit)).all()
#     if not autores:
#         raise HTTPException(status_code=404, detail="No se encontraron autores")
#     return autores

# @router.post("/autores", response_model=Autor)
# async def create_autor(
#     autor: AutorBase,
#     session: SessionDep,
# ):
#     db_autor = Autor.model_validate(autor)
#     session.add(db_autor)
#     session.commit()
#     session.refresh(db_autor)
#     return db_autor

# @router.get("/autores/{autor_id}", response_model=Autor)
# async def read_autor(
#     autor_id: UUID,
#     session: SessionDep,
# ):
#     autor = session.get(Autor, autor_id)
#     if not autor:
#         raise HTTPException(status_code=404, detail="Autor no encontrado")
#     return autor

# @router.post("/libros", response_model=Libro)
# async def create_libro(
#     libro: LibroBase,
#     session: SessionDep
# ):
#     db_libro = Libro.model_validate(libro)
#     session.add(db_libro)
#     session.commit()
#     session.refresh(db_libro)
#     return db_libro

# @router.get("/libros", response_model=list[Libro])
# async def read_libros(
#     session: SessionDep,
#     offset: int = 0,
#     limit: Annotated[int, Query(le=100)] = 10,
# ):
#     libros = session.exec(select(Libro).offset(offset).limit(limit)).all()
#     if not libros:
#         raise HTTPException(status_code=404, detail="No se encontraron libros")
#     return libros

# @router.get("/libros/{libro_id}", response_model=Libro)
# async def read_libro(
#     libro_id: UUID,
#     session: SessionDep,
# ):
#     libro = session.get(Libro, libro_id)
#     if not libro:
#         raise HTTPException(status_code=404, detail="Libro no encontrado")
#     return libro