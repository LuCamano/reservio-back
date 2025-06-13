from services import BaseService
from models import Propiedad

class PropiedadService(BaseService):
    def __init__(self):
        super().__init__(Propiedad)
