# Sistema de Pagos con MercadoPago

Este documento describe la implementación del sistema de pagos con MercadoPago y comisiones para la plataforma Reservio.

## Características Implementadas

### 1. Sistema de Pagos
- Integración completa con MercadoPago
- Creación de preferencias de pago
- Procesamiento de webhooks
- Seguimiento del estado de pagos

### 2. Sistema de Comisiones
- Cálculo automático del 5% de comisión para la plataforma
- 95% del pago va al propietario de la propiedad
- Gestión de estados de comisiones (pendiente, procesada, completada)
- Panel administrativo para gestionar pagos a propietarios

## Configuración

### 1. Variables de Entorno
Agregar las siguientes variables al archivo `.env`:

```env
# MercadoPago Configuration
MERCADOPAGO_ACCESS_TOKEN="TEST-YOUR_ACCESS_TOKEN_HERE"
MERCADOPAGO_PUBLIC_KEY="TEST-YOUR_PUBLIC_KEY_HERE"
MERCADOPAGO_WEBHOOK_URL="https://your-domain.com/webhook/mercadopago"
```

### 2. Instalación de Dependencias
```bash
pip install mercadopago==2.2.3
```

### 3. Migración de Base de Datos
Ejecutar el script de migración para crear las nuevas tablas:
```bash
python migrate_pagos.py
```

## Nuevos Modelos

### Pago
- Almacena información del pago de MercadoPago
- Calcula automáticamente la comisión del 5%
- Mantiene referencia a la reserva

### Comisión
- Representa el pago pendiente al propietario (95% del total)
- Estados: pendiente, procesada, completada
- Vinculada al pago y al propietario

## API Endpoints

### Para Clientes

#### POST `/pagos/crear-preferencia/{reserva_id}`
Crea una preferencia de pago en MercadoPago para una reserva.

**Respuesta:**
```json
{
  "success": true,
  "data": {
    "pago_id": "uuid",
    "preference_id": "mp_preference_id",
    "init_point": "https://mercadopago.com/checkout/...",
    "sandbox_init_point": "https://sandbox.mercadopago.com/checkout/..."
  },
  "message": "Preferencia de pago creada exitosamente"
}
```

#### GET `/pagos/estado/{pago_id}`
Obtiene el estado actual de un pago.

### Para Propietarios

#### GET `/pagos/comisiones/mis-pagos`
Obtiene las comisiones pendientes del propietario actual.

**Respuesta:**
```json
{
  "success": true,
  "data": [
    {
      "id": "uuid",
      "monto": 95000,
      "estado": "pendiente",
      "fecha_creacion": "2025-06-30T10:00:00",
      "descripcion": "Pago por reserva uuid"
    }
  ],
  "total_pendiente": 95000
}
```

### Para Administradores

#### GET `/pagos/admin/comisiones-a-pagar`
Obtiene todas las comisiones listas para ser pagadas, agrupadas por propietario.

#### PUT `/pagos/admin/procesar-comision/{comision_id}`
Marca una comisión como procesada (lista para pago).

#### PUT `/pagos/admin/completar-comision/{comision_id}`
Marca una comisión como completada (pago realizado).

## Webhook de MercadoPago

### POST `/pagos/webhook`
Endpoint para recibir notificaciones de MercadoPago cuando se completan los pagos.

**Configuración en MercadoPago:**
- URL: `https://tu-dominio.com/pagos/webhook`
- Eventos: `payment`

## Flujo de Pago

1. **Cliente solicita reserva:** Se crea la reserva con estado "pendiente"
2. **Cliente inicia pago:** Se llama a `/pagos/crear-preferencia/{reserva_id}`
3. **Redirección a MercadoPago:** Cliente completa el pago en la plataforma de MP
4. **Webhook de confirmación:** MercadoPago notifica el resultado del pago
5. **Procesamiento automático:** Se actualiza el estado del pago y se crea la comisión
6. **Administrador procesa comisión:** Marca la comisión como procesada cuando transfiere el dinero
7. **Administrador confirma pago:** Marca la comisión como completada

## Estados del Sistema

### Estados de Pago
- `pendiente`: Pago creado pero no procesado
- `aprobado`: Pago aprobado por MercadoPago
- `rechazado`: Pago rechazado
- `cancelado`: Pago cancelado

### Estados de Comisión
- `pendiente`: Comisión creada, esperando procesamiento
- `procesada`: Administrador ha iniciado el proceso de pago
- `completada`: Pago realizado al propietario

## Consideraciones de Seguridad

1. **Validación de Webhooks:** Verificar que los webhooks provienen realmente de MercadoPago
2. **Tokens seguros:** Mantener los tokens de MercadoPago seguros y usar diferentes tokens para producción
3. **Logs de auditoría:** Registrar todas las transacciones para auditoría
4. **Acceso administrativo:** Solo administradores pueden gestionar comisiones

## Testing

Para pruebas, usar las credenciales de sandbox de MercadoPago:
- Access Token: Comienza con "TEST-"
- Public Key: Comienza con "TEST-"

## Próximos Pasos

1. Implementar notificaciones por email cuando se procesen pagos
2. Agregar dashboard con estadísticas de comisiones
3. Implementar exportación de reportes financieros
4. Agregar soporte para múltiples métodos de pago
