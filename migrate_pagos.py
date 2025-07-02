"""
Script de migración para agregar las tablas de pagos y comisiones
Ejecutar este script después de actualizar los modelos
"""

from sqlmodel import SQLModel, create_engine
from dotenv import load_dotenv
import os

# Cargar variables de entorno
load_dotenv()

# Importar todos los modelos para que SQLModel los reconozca
from models import (
    Usuario, Region, Comuna, Propiedad, Reserva, 
    Boleta, Valoracion, Pago, Comision, BloqueoUsuario
)

def migrate_database():
    """
    Crea las nuevas tablas en la base de datos
    """
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise ValueError("DATABASE_URL no encontrada en las variables de entorno")
    
    engine = create_engine(database_url)
    
    print("Creando nuevas tablas...")
    
    # Esto creará solo las tablas que no existen
    SQLModel.metadata.create_all(engine)
    
    print("Migración completada exitosamente!")
    print("Nuevas tablas creadas:")
    print("- pago")
    print("- comision")

if __name__ == "__main__":
    migrate_database()
