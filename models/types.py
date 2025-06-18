import enum

class UserType(enum.Enum):
    """ Enumerador para el tipo de usuario """
    admin = "admin"
    cliente = "cliente"
    propietario = "propietario"

class ReservaStatus(enum.Enum):
    """ Enumerador para el estado de la reserva """
    pendiente = "pendiente"
    completada = "completada"
    cancelada = "cancelada"
