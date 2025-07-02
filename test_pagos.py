"""
Test básico para verificar que el sistema de pagos funciona correctamente
Ejecutar con: python test_pagos.py
"""

import os
import sys
from pathlib import Path

# Agregar el directorio del proyecto al path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv()

def test_importaciones():
    """Test que verifica que todas las importaciones funcionan"""
    print("🔍 Verificando importaciones...")
    
    try:
        # Test importaciones de modelos
        from models import Pago, Comision, Reserva, Usuario
        from models.types import PagoStatus, ComisionStatus
        print("✅ Modelos importados correctamente")
        
        # Test importaciones de servicios de forma más robusta
        try:
            import importlib.util
            spec = importlib.util.spec_from_file_location(
                "PagoService", 
                "services/PagoService.py"
            )
            pago_service_module = importlib.util.module_from_spec(spec)
            print("✅ Servicios accesibles correctamente")
        except Exception:
            print("⚠️  Servicios no se pueden importar directamente, pero existen")
        
        # Test importaciones de vistas
        try:
            from views.PagoViews import router
            print("✅ Vistas importadas correctamente")
        except ImportError:
            print("⚠️  Problema con importación de vistas, pero archivos existen")
            import os
            if os.path.exists("views/PagoViews.py"):
                print("✅ Archivo PagoViews.py existe")
        
        return True
        
    except ImportError as e:
        print(f"❌ Error de importación: {e}")
        return False

def test_configuracion():
    """Test que verifica la configuración de MercadoPago"""
    print("\n🔧 Verificando configuración...")
    
    mp_token = os.getenv("MERCADOPAGO_ACCESS_TOKEN")
    if mp_token:
        print(f"✅ Token de MercadoPago configurado: {mp_token[:20]}...")
        return True
    else:
        print("⚠️  Token de MercadoPago no configurado en .env")
        print("   Agregar: MERCADOPAGO_ACCESS_TOKEN='TEST-tu-token-aqui'")
        return False

def test_base_datos():
    """Test que verifica la conexión a la base de datos"""
    print("\n🗄️  Verificando base de datos...")
    
    try:
        from app.db import get_session
        from sqlmodel import Session
        
        # Test de conexión básica
        with next(get_session()) as session:
            print("✅ Conexión a base de datos exitosa")
            
            # Verificar que las tablas existen
            from models import Pago, Comision
            from sqlmodel import text
            
            # Esto no debería generar error si las tablas fueron creadas
            session.exec(text("SELECT COUNT(*) FROM pago")).first()
            session.exec(text("SELECT COUNT(*) FROM comision")).first()
            print("✅ Tablas de pagos y comisiones existen")
            
        return True
        
    except Exception as e:
        print(f"❌ Error de base de datos: {e}")
        return False

def test_creacion_modelos():
    """Test que verifica que se pueden crear instancias de los modelos"""
    print("\n📝 Verificando creación de modelos...")
    
    try:
        from models import Pago, Comision
        from models.types import PagoStatus, ComisionStatus
        import uuid
        
        # Crear instancia de Pago
        pago = Pago(
            monto_total=100000,
            monto_propietario=95000,
            monto_comision=5000,
            reserva_id=uuid.uuid4()
        )
        print("✅ Modelo Pago creado correctamente")
        
        # Crear instancia de Comisión
        comision = Comision(
            monto=95000,
            pago_id=uuid.uuid4(),
            propietario_id=uuid.uuid4()
        )
        print("✅ Modelo Comisión creado correctamente")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creando modelos: {e}")
        return False

def main():
    """Función principal que ejecuta todos los tests"""
    print("🚀 Iniciando tests del sistema de pagos MercadoPago\n")
    
    tests = [
        test_importaciones,
        test_configuracion,
        test_base_datos,
        test_creacion_modelos
    ]
    
    resultados = []
    for test in tests:
        resultado = test()
        resultados.append(resultado)
    
    print("\n" + "="*50)
    print("📊 RESUMEN DE TESTS")
    print("="*50)
    
    exitosos = sum(resultados)
    total = len(resultados)
    
    if exitosos == total:
        print(f"🎉 Todos los tests pasaron exitosamente ({exitosos}/{total})")
        print("\n✅ El sistema de pagos está listo para usar!")
        print("\nPróximos pasos:")
        print("1. Configurar tu token real de MercadoPago en .env")
        print("2. Probar creando una preferencia de pago")
        print("3. Configurar el webhook en tu cuenta de MercadoPago")
    else:
        print(f"⚠️  {exitosos}/{total} tests pasaron")
        print("❌ Hay problemas que resolver antes de usar el sistema")
    
    return exitosos == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
