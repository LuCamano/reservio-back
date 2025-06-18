from services import BaseService
from models import Propiedad, PropiedadBase
from controllers.Media import upload_image
from fastapi import UploadFile, File
from app.db import SessionDep

class PropiedadService(BaseService):
    model = Propiedad

    @classmethod
    def create(cls, session: SessionDep, obj: PropiedadBase, images: list[UploadFile] = [File(None)]):
        # Upload images and get their paths
        image_paths = []
        db_obj: Propiedad = super().create(session, obj=obj)
        for image in images:
            if image:
                image_path = upload_image(str(db_obj.id), file=image)
                image_paths.append(f"media/{image_path['folder']}/{image_path['filename']}")
        db_obj.imagenes = image_paths
        db_obj = cls.update(session, obj=db_obj)
        return db_obj