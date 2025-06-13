from app.db import SessionDep
from sqlmodel import SQLModel, select
from uuid import UUID

class BaseService:
    def __init__(self, model: type[SQLModel]):
        self.model = model

    def create(self, session: SessionDep, obj: SQLModel) -> SQLModel:
        db_obj = self.model.model_validate(obj)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def read(self, session: SessionDep, obj_id: UUID) -> SQLModel | None:
        return session.get(self.model, obj_id)

    def read_all(self, session: SessionDep, offset: int, limit: int, order_by: str | None = None, *args, **kwargs) -> list[SQLModel]:
        query = select(self.model)
        if order_by:
            query = query.order_by(order_by)
        if args or kwargs:
            query = query.where(*args, **kwargs)
        query = query.offset(offset).limit(limit)
        return session.exec(query).all()

    def update(self, session: SessionDep, obj: SQLModel) -> SQLModel:
        db_obj = self.model.model_validate(obj)
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj

    def delete(self, session: SessionDep, obj_id: UUID) -> None:
        obj = session.get(self.model, obj_id)
        if obj:
            session.delete(obj)
            session.commit()