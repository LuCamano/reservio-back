from services import BaseService
from models import Boleta

class BoletaService(BaseService):
    def __init__(self):
        super().__init__(Boleta)