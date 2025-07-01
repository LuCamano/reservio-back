# Ejemplos de uso de la API de Pagos

Este archivo contiene ejemplos de cómo usar los endpoints de la API de pagos con MercadoPago.

## Configuración inicial

1. Asegúrate de tener configurado tu token de MercadoPago en el archivo `.env`:
```env
MERCADOPAGO_ACCESS_TOKEN="TEST-1234567890-123456-abcdef123456789"
```

2. Obtén un token de autenticación haciendo login:
```bash
curl -X POST "http://localhost:8000/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@example.com",
    "password": "password123"
  }'
```

## 1. Crear una preferencia de pago

```bash
curl -X POST "http://localhost:8000/pagos/crear-preferencia/{reserva_id}" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json"
```

**Respuesta esperada:**
```json
{
  "success": true,
  "data": {
    "pago_id": "123e4567-e89b-12d3-a456-426614174000",
    "preference_id": "1234567890-abcd-1234-5678-123456789012",
    "init_point": "https://www.mercadopago.com.co/checkout/v1/redirect?pref_id=1234567890-abcd-1234-5678-123456789012",
    "sandbox_init_point": "https://sandbox.mercadopago.com.co/checkout/v1/redirect?pref_id=1234567890-abcd-1234-5678-123456789012"
  },
  "message": "Preferencia de pago creada exitosamente"
}
```

## 2. Verificar estado de un pago

```bash
curl -X GET "http://localhost:8000/pagos/estado/{pago_id}" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Respuesta esperada:**
```json
{
  "success": true,
  "data": {
    "id": "123e4567-e89b-12d3-a456-426614174000",
    "estado": "pendiente",
    "monto_total": 100000,
    "monto_propietario": 95000,
    "monto_comision": 5000,
    "fecha_creacion": "2025-06-30T10:00:00",
    "mp_payment_id": null,
    "mp_status": null
  }
}
```

## 3. Obtener comisiones del propietario

```bash
curl -X GET "http://localhost:8000/pagos/comisiones/mis-pagos" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

**Respuesta esperada:**
```json
{
  "success": true,
  "data": [
    {
      "id": "456e7890-e89b-12d3-a456-426614174000",
      "monto": 95000,
      "estado": "pendiente",
      "fecha_creacion": "2025-06-30T10:00:00",
      "fecha_procesamiento": null,
      "descripcion": "Pago por reserva 789e0123-e89b-12d3-a456-426614174000"
    }
  ],
  "total_pendiente": 95000
}
```

## 4. Endpoints de administración

### Obtener todas las comisiones a pagar (solo administradores)

```bash
curl -X GET "http://localhost:8000/pagos/admin/comisiones-a-pagar" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"
```

### Procesar una comisión (solo administradores)

```bash
curl -X PUT "http://localhost:8000/pagos/admin/procesar-comision/{comision_id}" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"
```

### Completar una comisión (solo administradores)

```bash
curl -X PUT "http://localhost:8000/pagos/admin/completar-comision/{comision_id}" \
  -H "Authorization: Bearer ADMIN_JWT_TOKEN"
```

## 5. Webhook de MercadoPago

El webhook se configura automáticamente y no requiere autenticación:

```bash
curl -X POST "http://localhost:8000/pagos/webhook" \
  -H "Content-Type: application/json" \
  -d '{
    "type": "payment",
    "data": {
      "id": "123456789"
    }
  }'
```

## Flujo completo de ejemplo

1. **Cliente crea una reserva** (usando otro endpoint)
2. **Cliente solicita pago:**
   ```bash
   curl -X POST "http://localhost:8000/pagos/crear-preferencia/reserva-id"
   ```
3. **Cliente es redirigido a MercadoPago** usando el `init_point`
4. **Cliente completa el pago en MercadoPago**
5. **MercadoPago envía webhook** automáticamente
6. **Sistema procesa el pago** y crea la comisión
7. **Propietario puede ver sus comisiones:**
   ```bash
   curl -X GET "http://localhost:8000/pagos/comisiones/mis-pagos"
   ```
8. **Administrador procesa el pago al propietario:**
   ```bash
   curl -X PUT "http://localhost:8000/pagos/admin/procesar-comision/comision-id"
   ```

## Códigos de estado

- `200`: Operación exitosa
- `400`: Error en la solicitud (datos inválidos, configuración incorrecta)
- `401`: No autenticado
- `403`: Sin permisos (para endpoints de admin)
- `404`: Recurso no encontrado
- `500`: Error interno del servidor

## Notas importantes

1. **Ambiente de pruebas**: Usar tokens que comiencen con "TEST-" para sandbox
2. **Webhook URL**: Configurar la URL real en producción
3. **Seguridad**: Los tokens JWT expiran, renovar según sea necesario
4. **Montos**: Todos los montos están en centavos (100 = $1.00)
5. **Estados de pago**: pendiente → aprobado/rechazado/cancelado
6. **Estados de comisión**: pendiente → procesada → completada
