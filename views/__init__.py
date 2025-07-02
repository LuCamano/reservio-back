from .UsuarioViews import router as usuarios_router
from .RegionViews import router as region_router
from .ComunaViews import router as comuna_router
from .PropiedadViews import router as propiedad_router
from .ReservaViews import router as reserva_router
from .BoletaViews import router as boleta_router
from .ValoracionViews import router as valoracion_router
from .AuthViews import router as auth_router
from .PagoViews import router as pago_router

routers = [
    auth_router,
    usuarios_router,
    region_router,
    comuna_router,
    propiedad_router,
    reserva_router,
    boleta_router,
    valoracion_router,
    pago_router,
]