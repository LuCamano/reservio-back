from app.db import SessionDep
from services import BaseService
from models import Usuario, UsuarioBase
from app.Auth import get_password_hash
from sqlmodel import select

class UsuarioService(BaseService):
    model = Usuario

    @classmethod
    def create(cls, session, obj: UsuarioBase) -> Usuario:
        new_user = obj
        new_user.password = get_password_hash(obj.password)
        return super().create(session, new_user)
    
    @classmethod
    def get_by_email(cls, session: SessionDep, email: str):
        return session.exec(select(Usuario).where(Usuario.email == email)).first()