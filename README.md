# pyafipws_endpoint_eureka

[![Build and Push Docker Image](https://github.com/dqmdz/pyafipws_endpoint_eureka/actions/workflows/deploy.yml/badge.svg)](https://github.com/dqmdz/pyafipws_endpoint_eureka/actions/workflows/deploy.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![Flask](https://img.shields.io/badge/flask-3.0.1-green.svg)](https://flask.palletsprojects.com/)
[![MySQL](https://img.shields.io/badge/mysql-5.7-orange.svg)](https://www.mysql.com/)
[![Docker](https://img.shields.io/badge/docker-latest-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/license-GPL%203.0-yellow.svg)](https://www.gnu.org/licenses/gpl-3.0)

Servicio REST basado en [pyafipws](https://github.com/reingart/pyafipws) para la emisión de comprobantes electrónicos AFIP (Argentina) con integración a Eureka Service Discovery.

## Características

- Emisión de comprobantes electrónicos AFIP (Facturas, Notas de Crédito/Débito)
- Integración con Eureka Service Discovery
- API REST con Flask
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
   - `INSTANCE_PORT`: Puerto del servicio (default: 5000)
   - `CERT_DATE`: Fecha del certificado (default: 2019-01-01)

## Uso

### Desarrollo local

```bash
docker-compose -f docker-compose.yml.example up
```

### Producción

```bash
docker-compose up -d
```

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

### GET /api/afipws/test

Endpoint de prueba para verificar el estado del servicio.

## Licencia

GPL 3.0
