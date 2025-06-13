from services import BaseService
from models import Usuario

class UsuarioService(BaseService):
    def __init__(self):
        super().__init__(Usuario)
