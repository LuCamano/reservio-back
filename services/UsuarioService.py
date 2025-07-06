from app.db import SessionDep
from services import BaseService
from models import Usuario, UsuarioBase, BloqueoUsuario
from app.Auth import get_password_hash
from sqlmodel import select
from uuid import UUID
from datetime import datetime

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
    
    @classmethod
    def isActive(cls, session: SessionDep, user_id: UUID) -> bool:
        """
        Verifica si un usuario está activo (no bloqueado).
        Un usuario está bloqueado si:
        - Tiene un bloqueo sin fecha de desbloqueo (bloqueo permanente)
        - Tiene un bloqueo con fecha de desbloqueo en el futuro
        """
        now = datetime.now()
        
        # Buscar bloqueos activos para el usuario
        bloqueo_activo = session.exec(
            select(BloqueoUsuario).where(
                BloqueoUsuario.usuario_id == user_id,
                # El bloqueo está activo si:
                # 1. No tiene fecha de desbloqueo (bloqueo permanente) O
                # 2. La fecha de desbloqueo es en el futuro
                (BloqueoUsuario.fecha_desbloqueo.is_(None)) | 
                (BloqueoUsuario.fecha_desbloqueo > now)
            )
        ).first()
        
        # El usuario está activo si NO hay bloqueos activos
        return bloqueo_activo is None
    
    @classmethod
    def get_active_block(cls, session: SessionDep, user_id: UUID) -> BloqueoUsuario | None:
        """
        Obtiene el bloqueo activo de un usuario, si existe.
        Útil para obtener detalles del bloqueo como motivo y fechas.
        """
        now = datetime.now()
        
        return session.exec(
            select(BloqueoUsuario).where(
                BloqueoUsuario.usuario_id == user_id,
                # El bloqueo está activo si:
                # 1. No tiene fecha de desbloqueo (bloqueo permanente) O
                # 2. La fecha de desbloqueo es en el futuro
                (BloqueoUsuario.fecha_desbloqueo.is_(None)) | 
                (BloqueoUsuario.fecha_desbloqueo > now)
            ).order_by(BloqueoUsuario.fecha_bloqueo.desc())  # El más reciente primero
        ).first()
        
    @classmethod
    def block_user(cls, session: SessionDep, user_id: UUID, administrador_id: UUID, motivo: str, fecha_desbloqueo: datetime | None = None) -> BloqueoUsuario:
        bloqueo = BloqueoUsuario(usuario_id=user_id, motivo=motivo, 
                                administrador_id=administrador_id,
                                fecha_desbloqueo=fecha_desbloqueo
                                )
        session.add(bloqueo)
        session.commit()
        session.refresh(bloqueo)
        return bloqueo
    
    @classmethod
    def unblock_user(cls, session: SessionDep, user_id: UUID):
        # Buscar el bloqueo activo más reciente
        bloqueo_activo = cls.get_active_block(session, user_id)
        if not bloqueo_activo:
            raise ValueError("El usuario no tiene bloqueos activos")
        
        # Actualizar la fecha de desbloqueo
        bloqueo_activo.fecha_desbloqueo = datetime.now()
        session.add(bloqueo_activo)
        session.commit()
        session.refresh(bloqueo_activo)
        return bloqueo_activo