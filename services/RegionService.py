from services import BaseService
from models import Region

class RegionService(BaseService):
    def __init__(self):
        super().__init__(Region)