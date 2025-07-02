from fastapi import APIRouter, Depends, HTTPException, Request
from sqlmodel import Session
from typing import Dict, Any
from uuid import UUID
import os

from app.db import get_session
from app.Auth import get_current_user
from models import Usuario
from services.PagoService import MercadoPagoService
from services.ComisionService import ComisionService
from schemas.PagoSchemas import ApiResponse, PreferenciaPagoResponse

router = APIRouter(prefix="/pagos", tags=["Pagos"])

# Configurar MercadoPago (obtener del .env)
MP_ACCESS_TOKEN = os.getenv("MERCADOPAGO_ACCESS_TOKEN", "")

def get_mp_service():
    """Factory function para obtener el servicio de MercadoPago"""
    if not MP_ACCESS_TOKEN:
        raise HTTPException(
            status_code=500, 
            detail="MercadoPago no está configurado. Verificar MERCADOPAGO_ACCESS_TOKEN en .env"
        )
    return MercadoPagoService(MP_ACCESS_TOKEN)


@router.post("/crear-preferencia/{reserva_id}")
async def crear_preferencia_pago(
    reserva_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Crea una preferencia de pago en MercadoPago para una reserva
    """
    try:
        mp_service = get_mp_service()
        resultado = mp_service.crear_preferencia_pago(reserva_id, session)
        return {
            "success": True,
            "data": resultado,
            "message": "Preferencia de pago creada exitosamente"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/webhook")
async def webhook_mercadopago(
    request: Request,
    session: Session = Depends(get_session)
):
    """
    Webhook para recibir notificaciones de MercadoPago
    """
    try:
        # Obtener los datos del webhook
        body = await request.json()
        
        # Verificar que sea una notificación de pago
        if body.get("type") == "payment":
            payment_id = body.get("data", {}).get("id")
            
            if payment_id:
                mp_service = get_mp_service()
                mp_service.procesar_webhook(str(payment_id), session)
                return {"status": "ok"}
        
        return {"status": "ignored"}
        
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/estado/{pago_id}")
async def obtener_estado_pago(
    pago_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Obtiene el estado actual de un pago
    """
    try:
        mp_service = get_mp_service()
        resultado = mp_service.obtener_estado_pago(pago_id, session)
        return {
            "success": True,
            "data": resultado
        }
    except Exception as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/comisiones/mis-pagos")
async def obtener_mis_comisiones(
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Obtiene las comisiones (pagos pendientes) del propietario actual
    """
    try:
        comisiones = ComisionService.obtener_comisiones_propietario(
            current_user.id, session
        )
        
        resultado = []
        for comision in comisiones:
            resultado.append({
                "id": str(comision.id),
                "monto": comision.monto,
                "estado": comision.estado.value,
                "fecha_creacion": comision.fecha_creacion.isoformat(),
                "fecha_procesamiento": comision.fecha_procesamiento.isoformat() if comision.fecha_procesamiento else None,
                "descripcion": comision.descripcion
            })
        
        return {
            "success": True,
            "data": resultado,
            "total_pendiente": sum(c.monto for c in comisiones if c.estado.value == "pendiente")
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/admin/comisiones-a-pagar")
async def obtener_comisiones_a_pagar(
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Obtiene todas las comisiones que están listas para ser pagadas (solo para administradores)
    """
    # Verificar que el usuario sea administrador
    if current_user.tipo.value != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    try:
        comisiones = ComisionService.obtener_comisiones_a_pagar(session)
        return {
            "success": True,
            "data": comisiones
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/admin/procesar-comision/{comision_id}")
async def procesar_comision(
    comision_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Marca una comisión como procesada (solo para administradores)
    """
    # Verificar que el usuario sea administrador
    if current_user.tipo.value != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    try:
        ComisionService.procesar_comision(comision_id, session)
        return {
            "success": True,
            "message": "Comisión procesada exitosamente"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/admin/completar-comision/{comision_id}")
async def completar_comision(
    comision_id: UUID,
    current_user: Usuario = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> Dict[str, Any]:
    """
    Marca una comisión como completada (solo para administradores)
    """
    # Verificar que el usuario sea administrador
    if current_user.tipo.value != "admin":
        raise HTTPException(status_code=403, detail="Acceso denegado")
    
    try:
        ComisionService.completar_comision(comision_id, session)
        return {
            "success": True,
            "message": "Comisión completada exitosamente"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
