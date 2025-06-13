from services import BaseService
from models import Comuna

class ComunaService(BaseService):
    def __init__(self):
        super().__init__(Comuna)