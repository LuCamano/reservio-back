from services import BaseService
from models import Propiedad, PropiedadBase
from controllers.Media import upload_image
from fastapi import UploadFile, File
from app.db import SessionDep
from uuid import UUID

class PropiedadService(BaseService):
    model = Propiedad

    @classmethod
    def create(cls, session: SessionDep, obj: PropiedadBase, images: list[UploadFile] = [File(None)], documento: UploadFile | None = None):
        # Upload images and get their paths
        image_paths = []
        db_obj: Propiedad = super().create(session, obj=obj)
        for image in images:
            if image and image.filename:
                image_path = upload_image(str(db_obj.id), file=image)
                image_paths.append(f"media/{image_path['folder']}/{image_path['filename']}")
        db_obj.imagenes = image_paths

        # Upload document if provided
        if documento:
            doc_path = upload_image(f'{db_obj.id}/docs', file=documento)
            db_obj.documento = f"media/{doc_path['folder']}/{doc_path['filename']}"
        # Actualizar directamente en la base de datos
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    
    @classmethod
    def update_with_images(cls, session: SessionDep, propiedad_id: UUID, images: list[UploadFile]):
        """Actualiza las imágenes de una propiedad existente"""
        db_obj: Propiedad = session.get(cls.model, propiedad_id)
        if not db_obj:
            raise ValueError(f"No existe una propiedad con id {propiedad_id}")
        
        # Upload new images and get their paths
        image_paths = []
        for image in images:
            if image and image.filename:
                image_path = upload_image(str(db_obj.id), file=image)
                image_paths.append(f"media/{image_path['folder']}/{image_path['filename']}")

        # Update images (replace existing ones)
        db_obj.imagenes = image_paths
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj
    
    @classmethod
    def update_document(cls, session: SessionDep, propiedad_id: UUID, documento: UploadFile):
        """Actualiza el documento de una propiedad existente"""
        db_obj: Propiedad = session.get(cls.model, propiedad_id)
        if not db_obj:
            raise ValueError(f"No existe una propiedad con id {propiedad_id}")
        
        # Upload document
        doc_path = upload_image(f'{db_obj.id}/docs', file=documento)
        db_obj.documento = f"media/{doc_path['folder']}/{doc_path['filename']}"
        
        session.add(db_obj)
        session.commit()
        session.refresh(db_obj)
        return db_obj