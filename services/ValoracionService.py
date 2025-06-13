from services import BaseService
from models import Valoracion

class ValoracionService(BaseService):
    def __init__(self):
        super().__init__(Valoracion)
