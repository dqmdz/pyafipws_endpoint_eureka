# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

## [2025.06.14] - 2025-06-14

### Nuevas características
- **Integración completa con OpenTelemetry** para observabilidad
- **Instrumentación automática** de Flask, requests y logging
- **Soporte para trazas distribuidas** con Jaeger + Elasticsearch
- **Nuevo archivo `app/otel_setup.py`** para configuración de observabilidad

### Mejoras
- Actualizada documentación del README con información de observabilidad
- Mejorado el logging con contexto de trazas
- Agregadas dependencias OpenTelemetry:
  - opentelemetry-api==1.21.0
  - opentelemetry-sdk==1.21.0
  - opentelemetry-instrumentation-flask==0.42b0
  - opentelemetry-instrumentation-requests==0.42b0
  - opentelemetry-instrumentation-logging==0.42b0
  - opentelemetry-exporter-otlp-proto-http==1.21.0

### Cambios técnicos
- Modificado `app/service.py` para integrar OpenTelemetry
- Actualizado `app/routes.py` para incluir trazas en endpoints
- Agregada configuración opcional via variable de entorno `OTEL_EXPORTER_OTLP_ENDPOINT`

## [2025.05.18] - 2025-05-18

### Mejoras
- Actualizado Python a 3.11
- Actualizada versión de pyafipws a v2025.05.05
- Mejorada la documentación del proyecto

### Cambios
- Agregado campo requerido `id_condicion_iva` para facturación
- Mejorado el formato de logging de JSON en el endpoint de facturación

## [2025.01.03] - 2025-01-03

### Mejoras
- Mejorado el logging de la integración con AFIP
- Deshabilitado el cache para la integración con AFIP

## [2025.01.01] - 2025-01-01

### Mejoras
- Restaurada la verificación de estado de servidores AFIP
- Mejorado el manejo de autenticación

### Correcciones
- Removido logging de debug hardcodeado
- Corregido el nivel de debug para conexiones HTTP

## Notas
- Todos los cambios están basados en commits reales del repositorio verificados en el historial de git
- Las fechas están en formato YYYY-MM-DD y corresponden a las fechas reales de los commits
- Los cambios están organizados cronológicamente de más reciente a más antiguo
- Información no verificable del historial anterior ha sido removida para mantener precisión

### Información no verificable removida
- Cambios fechados en 2024.07.25, 2024.09.14, 2024.11.07, 2024.12.02, 2025.01.14 no pudieron ser confirmados en el historial de git actual
- Se recomienda verificar estos cambios con el historial completo del repositorio 