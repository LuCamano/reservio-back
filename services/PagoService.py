import mercadopago
from typing import Dict, Any, Optional
from uuid import UUID
from datetime import datetime
from sqlmodel import Session, select
import os
from app.db import get_session
from models import Pago, Comision, Reserva, Usuario
from models.types import PagoStatus, ComisionStatus

NOTIF_URL = os.getenv("MERCADOPAGO_WEBHOOK_URL")

SUCCESS_URL = os.getenv("FRONTEND_SUCCESS_URL")
ERROR_URL = os.getenv("FRONTEND_ERROR_URL")
PENDING_URL = os.getenv("FRONTEND_PENDING_URL")


class MercadoPagoService:
    def __init__(self, access_token: str):
        """
        Inicializa el servicio de MercadoPago
        
        Args:
            access_token: Token de acceso de MercadoPago
        """
        self.sdk = mercadopago.SDK(access_token)
        
    def crear_preferencia_pago(self, reserva_id: UUID, session: Session) -> Dict[str, Any]:
        """
        Crea una preferencia de pago en MercadoPago
        
        Args:
            reserva_id: ID de la reserva
            session: Sesión de base de datos
            
        Returns:
            Diccionario con la información de la preferencia creada
        """
        # Obtener la reserva
        reserva = session.get(Reserva, reserva_id)
        if not reserva:
            raise ValueError("Reserva no encontrada")
            
        # Calcular montos
        monto_total = reserva.costo_total
        monto_comision = int(monto_total * 0.05)  # 5% de comisión
        monto_propietario = monto_total - monto_comision
        
        # Crear el pago en la base de datos
        pago = Pago(
            monto_total=monto_total,
            monto_propietario=monto_propietario,
            monto_comision=monto_comision,
            reserva_id=reserva_id,
            mp_external_reference=str(reserva_id)
        )
        session.add(pago)
        session.commit()
        session.refresh(pago)
        
        # Configurar la preferencia de MercadoPago
        preference_data = {
            "items": [
                {
                    "title": f"Reserva de propiedad",
                    "quantity": 1,
                    "unit_price": monto_total / 100,  # MercadoPago usa valores sin centavos
                    "currency_id": "CLP"
                }
            ],
            "external_reference": str(pago.id),
            "notification_url": NOTIF_URL,
            "back_url": {
                "success": SUCCESS_URL,
                "failure": ERROR_URL,
                "pending": PENDING_URL
            },
            "auto_return": "approved"
        }
        
        # Crear la preferencia en MercadoPago
        preference_response = self.sdk.preference().create(preference_data)
        
        if preference_response["status"] == 201:
            # Actualizar el pago con el ID de la preferencia
            pago.mp_preference_id = preference_response["response"]["id"]
            session.commit()
            
            return {
                "pago_id": str(pago.id),
                "preference_id": preference_response["response"]["id"],
                "init_point": preference_response["response"]["init_point"],
                "sandbox_init_point": preference_response["response"]["sandbox_init_point"]
            }
        else:
            raise Exception(f"Error al crear preferencia: {preference_response}")
    
    def procesar_webhook(self, payment_id: str, session: Session) -> bool:
        """
        Procesa el webhook de MercadoPago cuando se completa un pago
        
        Args:
            payment_id: ID del pago en MercadoPago
            session: Sesión de base de datos
            
        Returns:
            True si el procesamiento fue exitoso
        """
        # Obtener información del pago desde MercadoPago
        payment_info = self.sdk.payment().get(payment_id)
        
        if payment_info["status"] != 200:
            raise Exception(f"Error al obtener información del pago: {payment_info}")
        
        payment_data = payment_info["response"]
        external_reference = payment_data.get("external_reference")
        
        if not external_reference:
            raise ValueError("No se encontró referencia externa en el pago")
        
        # Buscar el pago en la base de datos
        pago = session.exec(
            select(Pago).where(Pago.id == UUID(external_reference))
        ).first()
        
        if not pago:
            raise ValueError("Pago no encontrado en la base de datos")
        
        # Actualizar el estado del pago
        pago.mp_payment_id = payment_id
        pago.mp_status = payment_data["status"]
        pago.fecha_procesamiento = datetime.now()
        
        if payment_data["status"] == "approved":
            pago.estado = PagoStatus.aprobado
            
            # Crear la comisión para el propietario
            reserva = session.get(Reserva, pago.reserva_id)
            if reserva and reserva.propiedad_id:
                # Obtener el propietario de la propiedad
                from models import Propiedad
                propiedad = session.get(Propiedad, reserva.propiedad_id)
                if propiedad and propiedad.propietarios:
                    propietario = propiedad.propietarios[0]  # Asumimos un propietario principal
                    
                    comision = Comision(
                        monto=pago.monto_propietario,
                        pago_id=pago.id,
                        propietario_id=propietario.id,
                        descripcion=f"Pago por reserva {reserva.id}"
                    )
                    session.add(comision)
                    
        elif payment_data["status"] == "rejected":
            pago.estado = PagoStatus.rechazado
        elif payment_data["status"] == "cancelled":
            pago.estado = PagoStatus.cancelado
        
        session.commit()
        return True
    
    def obtener_estado_pago(self, pago_id: UUID, session: Session) -> Dict[str, Any]:
        """
        Obtiene el estado actual de un pago
        
        Args:
            pago_id: ID del pago en la base de datos
            session: Sesión de base de datos
            
        Returns:
            Diccionario con el estado del pago
        """
        pago = session.get(Pago, pago_id)
        if not pago:
            raise ValueError("Pago no encontrado")
        
        resultado = {
            "id": str(pago.id),
            "estado": pago.estado.value,
            "monto_total": pago.monto_total,
            "monto_propietario": pago.monto_propietario,
            "monto_comision": pago.monto_comision,
            "fecha_creacion": pago.fecha_creacion.isoformat(),
            "mp_payment_id": pago.mp_payment_id,
            "mp_status": pago.mp_status
        }
        
        # Si hay un payment_id de MercadoPago, obtener información actualizada
        if pago.mp_payment_id:
            try:
                payment_info = self.sdk.payment().get(pago.mp_payment_id)
                if payment_info["status"] == 200:
                    resultado["mp_info"] = payment_info["response"]
            except Exception:
                pass  # Continuar sin la información de MP si hay error
        
        return resultado
