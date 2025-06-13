from services import BaseService
from models.manyToMany import UsuarioPropiedad

class UsuarioPropiedadService(BaseService):
    def __init__(self):
        super().__init__(UsuarioPropiedad)
