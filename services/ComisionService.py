from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from sqlmodel import Session, select

from models import Comision, Pago, Usuario
from models.types import ComisionStatus


class ComisionService:
    
    @staticmethod
    def obtener_comisiones_propietario(
        propietario_id: UUID, 
        session: Session,
        estado: Optional[ComisionStatus] = None
    ) -> List[Comision]:
        """
        Obtiene todas las comisiones de un propietario
        
        Args:
            propietario_id: ID del propietario
            session: Sesión de base de datos
            estado: Estado opcional para filtrar
            
        Returns:
            Lista de comisiones
        """
        query = select(Comision).where(Comision.propietario_id == propietario_id)
        
        if estado:
            query = query.where(Comision.estado == estado)
            
        return session.exec(query).all()
    
    @staticmethod
    def procesar_comision(comision_id: UUID, session: Session) -> bool:
        """
        Marca una comisión como procesada (lista para pago)
        
        Args:
            comision_id: ID de la comisión
            session: Sesión de base de datos
            
        Returns:
            True si se procesó correctamente
        """
        comision = session.get(Comision, comision_id)
        if not comision:
            raise ValueError("Comisión no encontrada")
        
        if comision.estado != ComisionStatus.pendiente:
            raise ValueError("La comisión no está en estado pendiente")
        
        comision.estado = ComisionStatus.procesada
        comision.fecha_procesamiento = datetime.now()
        session.commit()
        
        return True
    
    @staticmethod
    def completar_comision(comision_id: UUID, session: Session) -> bool:
        """
        Marca una comisión como completada (pago realizado)
        
        Args:
            comision_id: ID de la comisión
            session: Sesión de base de datos
            
        Returns:
            True si se completó correctamente
        """
        comision = session.get(Comision, comision_id)
        if not comision:
            raise ValueError("Comisión no encontrada")
        
        if comision.estado != ComisionStatus.procesada:
            raise ValueError("La comisión debe estar procesada primero")
        
        comision.estado = ComisionStatus.completada
        session.commit()
        
        return True
    
    @staticmethod
    def obtener_resumen_comisiones_periodo(
        fecha_inicio: datetime,
        fecha_fin: datetime,
        session: Session
    ) -> Dict[str, Any]:
        """
        Obtiene un resumen de las comisiones en un período
        
        Args:
            fecha_inicio: Fecha de inicio del período
            fecha_fin: Fecha de fin del período
            session: Sesión de base de datos
            
        Returns:
            Diccionario con el resumen
        """
        query = select(Comision).where(
            Comision.fecha_creacion >= fecha_inicio,
            Comision.fecha_creacion <= fecha_fin
        )
        
        comisiones = session.exec(query).all()
        
        total_comisiones = sum(c.monto for c in comisiones)
        comisiones_por_estado = {}
        
        for estado in ComisionStatus:
            comisiones_estado = [c for c in comisiones if c.estado == estado]
            comisiones_por_estado[estado.value] = {
                "cantidad": len(comisiones_estado),
                "monto_total": sum(c.monto for c in comisiones_estado)
            }
        
        return {
            "periodo": {
                "inicio": fecha_inicio.isoformat(),
                "fin": fecha_fin.isoformat()
            },
            "total_comisiones": total_comisiones,
            "cantidad_total": len(comisiones),
            "por_estado": comisiones_por_estado
        }
    
    @staticmethod
    def obtener_comisiones_a_pagar(session: Session) -> List[Dict[str, Any]]:
        """
        Obtiene todas las comisiones que están listas para ser pagadas a los propietarios
        
        Args:
            session: Sesión de base de datos
            
        Returns:
            Lista de comisiones agrupadas por propietario
        """
        query = select(Comision).where(Comision.estado == ComisionStatus.procesada)
        comisiones = session.exec(query).all()
        
        # Agrupar por propietario
        comisiones_por_propietario = {}
        
        for comision in comisiones:
            propietario_id = str(comision.propietario_id)
            
            if propietario_id not in comisiones_por_propietario:
                propietario = session.get(Usuario, comision.propietario_id)
                comisiones_por_propietario[propietario_id] = {
                    "propietario": {
                        "id": propietario_id,
                        "nombre": f"{propietario.nombres} {propietario.appaterno}" if propietario else "N/A",
                        "email": propietario.email if propietario else "N/A"
                    },
                    "comisiones": [],
                    "monto_total": 0
                }
            
            comisiones_por_propietario[propietario_id]["comisiones"].append({
                "id": str(comision.id),
                "monto": comision.monto,
                "fecha_creacion": comision.fecha_creacion.isoformat(),
                "descripcion": comision.descripcion
            })
            
            comisiones_por_propietario[propietario_id]["monto_total"] += comision.monto
        
        return list(comisiones_por_propietario.values())
