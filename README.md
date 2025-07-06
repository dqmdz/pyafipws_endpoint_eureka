# pyafipws_endpoint_eureka (ETEREA Fork)

This repository is a fork of the original [pyafipws_endpoint_eureka by dqmdz](https://github.com/dqmdz/pyafipws_endpoint_eureka). It is maintained by ETEREA with specific modifications.

[![Build and Push Docker Image](https://github.com/ETEREA-services/ETEREA.pyafipws-tsa-service/actions/workflows/deploy.yml/badge.svg)](https://github.com/ETEREA-services/ETEREA.pyafipws-tsa-service/actions/workflows/deploy.yml)

---

*The following is the documentation from the original repository for reference.*

# pyafipws_endpoint_eureka

[![Build and Push Docker Image](https://github.com/dqmdz/pyafipws_endpoint_eureka/actions/workflows/deploy.yml/badge.svg)](https://github.com/dqmdz/pyafipws_endpoint_eureka/actions/workflows/deploy.yml)
[![Python 3.13](https://img.shields.io/badge/python-3.13-blue.svg)](https://www.python.org/downloads/release/python-3130/)
[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/release/python-3120/)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Flask 3.0.1](https://img.shields.io/badge/flask-3.0.1-green.svg)](https://flask.palletsprojects.com/)
[![pyafipws v2025.05.05](https://img.shields.io/badge/pyafipws-v2025.05.05-orange.svg)](https://github.com/dqmdz/pyafipws)
[![Docker](https://img.shields.io/badge/docker-latest-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-GPL%203.0-yellow.svg)](https://www.gnu.org/licenses/gpl-3.0)

Servicio REST basado en [pyafipws v2025.05.05](https://github.com/dqmdz/pyafipws) para la emisión de comprobantes electrónicos AFIP (Argentina) con integración a Eureka Service Discovery.

## Características

- Emisión de comprobantes electrónicos AFIP (Facturas, Notas de Crédito/Débito)
- Integración con Eureka Service Discovery
- API REST con Flask 3.0.1
- **Documentación automática con Swagger/OpenAPI**
- **Observabilidad con OpenTelemetry** (trazas, métricas y logs)
- **Integración con Jaeger + Elasticsearch** para monitoreo distribuido
- Contenedorización con Docker
- Soporte para ambiente de homologación y producción
- Logging mejorado y manejo de errores
- Validación de datos de entrada
- Soporte para comprobantes asociados

## Requisitos

- Python 3.11
- Docker y Docker Compose
- Certificados AFIP válidos (`.crt` y `.key`)
- CUIT válido para facturación
- **Opcional**: Endpoint OpenTelemetry para observabilidad

## Configuración

1. Clonar el repositorio
2. Copiar los certificados AFIP a la raíz del proyecto:
   - `user.crt`
   - `user.key`
3. Configurar variables de entorno (opcional):
   - `CUIT`: CUIT para facturación
   - `CERT`: Ruta al certificado (default: user.crt)
   - `PRIVATEKEY`: Ruta a la clave privada (default: user.key)
   - `PRODUCTION`: TRUE/FALSE para ambiente de producción
   - `EUREKA_PORT`: Puerto de Eureka (default: 8761)
   - `INSTANCE_PORT`: Puerto del servicio (default: 5086)
   - `CERT_DATE`: Fecha del certificado (default: 2019-01-01)
   - **`OTEL_EXPORTER_OTLP_ENDPOINT`**: Endpoint OpenTelemetry para observabilidad (opcional)

## Uso

### Desarrollo local

```bash
docker-compose -f docker-compose.yml.example up
```

### Producción

```bash
docker-compose up -d
```

## Observabilidad

El servicio incluye integración completa con OpenTelemetry para observabilidad:

### Trazas Distribuidas
- Instrumentación automática de Flask, requests y logging
- Trazas de todas las operaciones de facturación
- Integración con Jaeger para visualización de trazas

### Métricas y Logs
- Logging estructurado con contexto de trazas
- Métricas de rendimiento y errores
- Exportación a Elasticsearch para análisis

### Configuración
Para habilitar la observabilidad, configurar la variable de entorno:
```bash
OTEL_EXPORTER_OTLP_ENDPOINT=http://jaeger:4318
```

## Documentación de la API

### Swagger UI

Una vez que el servicio esté ejecutándose, puedes acceder a la documentación interactiva de la API en:

```
http://localhost:5086/swagger/
```

La documentación Swagger incluye:
- Descripción completa de todos los endpoints
- Modelos de datos con ejemplos
- Interfaz interactiva para probar los endpoints
- Códigos de respuesta y manejo de errores

📖 **Guía completa de Swagger**: [docs/SWAGGER_GUIDE.md](docs/SWAGGER_GUIDE.md)

## API Endpoints

### POST /api/afipws/facturador

Emite un comprobante electrónico.

**Campos requeridos:**
- `tipo_afip`: Tipo de comprobante AFIP
- `punto_venta`: Punto de venta
- `tipo_documento`: Tipo de documento del receptor
- `documento`: Número de documento del receptor
- `total`: Importe total
- `id_condicion_iva`: ID de condición IVA del receptor

**Campos opcionales:**
- `neto`: Importe neto gravado
- `iva`: Importe IVA 21%
- `neto105`: Importe neto gravado 10.5%
- `iva105`: Importe IVA 10.5%
- `asociado_tipo_afip`: Tipo de comprobante asociado
- `asociado_punto_venta`: Punto de venta del comprobante asociado
- `asociado_numero_comprobante`: Número de comprobante asociado
- `asociado_fecha_comprobante`: Fecha del comprobante asociado

### GET /api/afipws/consulta_comprobante

Consulta un comprobante electrónico ya emitido.

**Query Parameters:**
- `tipo_cbte` (integer, required): Tipo de comprobante AFIP (ej. 6 para Factura B).
- `punto_vta` (integer, required): Punto de venta (ej. 34).
- `cbte_nro` (integer, required): Número del comprobante a consultar (ej. 100).

**Respuesta Exitosa (200 OK):**
```json
{
  "mensaje": "Comprobante encontrado.",
  "factura": {
    "concepto": 1,
    "tipo_doc": 96,
    "nro_doc": 28757428,
    "tipo_cbte": 6,
    "punto_vta": 34,
    "cbt_desde": 100,
    "cbt_hasta": 100,
    "fecha_cbte": "20240126",
    "imp_total": 20000.04,
    "cae": "74049145150923",
    "resultado": "A",
    "fch_venc_cae": "20240205",
    "...": "..."
  }
}
```

**Respuesta Comprobante No Encontrado (200 OK):**
```json
{
  "mensaje": "602: No existen datos en nuestros registros para los parametros ingresados.",
  "factura": null
}
```

### GET /api/afipws/test

Endpoint de prueba para verificar el estado del servicio.

## Ejemplo de uso con curl

```bash
# Probar el endpoint de test
curl -X GET "http://localhost:5086/api/afipws/test"

# Consultar un comprobante existente
curl -X GET "http://localhost:5086/api/afipws/consulta_comprobante?tipo_cbte=6&punto_vta=34&cbte_nro=100"

# Emitir una factura
curl -X POST "http://localhost:5086/api/afipws/facturador" \
  -H "Content-Type: application/json" \
  -d '{
    "tipo_afip": 1,
    "punto_venta": 1,
    "tipo_documento": 80,
    "documento": "20123456789",
    "total": 1210.0,
    "id_condicion_iva": 1,
    "neto": 1000.0,
    "iva": 210.0
  }'
```

## Ejemplos y Documentación

- 📚 [Guía de Swagger](docs/SWAGGER_GUIDE.md) - Documentación completa de la API
- 🚀 [Ejemplo de uso](examples/api_usage.py) - Script de ejemplo para probar la API

## Licencia

GPL 3.0