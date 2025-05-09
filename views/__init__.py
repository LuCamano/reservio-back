from fastapi import APIRouter
from models import Prueba
from app.db import SessionDep

router = APIRouter()

@router.get("/")
async def read_root():
    return {"message": "Hola papus"}

@router.get("/prueba")
async def prueba(session: SessionDep):
    test = Prueba(nombre="Test")
    session.add(test)
    session.commit()
    session.refresh(test)
    return test