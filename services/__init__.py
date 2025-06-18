from app.db import SessionDep
from sqlmodel import SQLModel, select
from uuid import UUID

class BaseService:
    model: type[SQLModel]

    @classmethod
    def create(cls, session: SessionDep, obj: SQLModel) -> SQLModel:
        db_obj = cls.model.model_validate(obj)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    @classmethod
    def read(cls, session: SessionDep, obj_id: UUID) -> SQLModel | None:
        return session.get(cls.model, obj_id)

    @classmethod
    def read_all(cls, session: SessionDep, offset: int, limit: int, order_by: str | None = None, filtros: dict = None) -> list[SQLModel]:
        query = select(cls.model)
        if order_by:
            query = query.order_by(order_by)
        if filtros:
            condiciones = []
            for campo, valor in filtros.items():
                if hasattr(cls.model, campo):
                    condiciones.append(getattr(cls.model, campo) == valor)
            query = query.where(*condiciones)
        query = query.offset(offset).limit(limit)
        return session.exec(query).all()

    @classmethod
    def update(cls, session: SessionDep, obj: SQLModel) -> SQLModel:
        # Obtener el objeto existente
        db_obj = session.get(cls.model, obj.id)
        if not db_obj:
            raise ValueError(f"No existe un objeto con id {obj.id}")
        # Actualizar solo los campos presentes en obj
        for key, value in obj.model_dump(exclude_unset=True).items():
            setattr(db_obj, key, value)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    @classmethod
    def delete(cls, session: SessionDep, obj_id: UUID) -> None:
        obj = session.get(cls.model, obj_id)
        if obj:
            session.delete(obj)
            session.commit()