from services import BaseService
from models import Reserva

class ReservaService(BaseService):
    def __init__(self):
        super().__init__(Reserva)
