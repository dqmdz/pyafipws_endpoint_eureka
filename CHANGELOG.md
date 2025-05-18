# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

## [2025.05.05] - 2025-05-14

### Cambios
- Actualizado Python a 3.11
- Actualizada versión de pyafipws a v2025.05.05
- Agregado campo requerido `id_condicion_iva` para facturación
- Mejorado el formato de logging de JSON en el endpoint de facturación

## [2024.07.25] - 2024-07-28

### Mejoras
- Agregado badge de estado del workflow
- Cambiado nombre del certificado
- Flexibilizado el proceso de deploy
- Corregidos errores de Flask
- Mejorada la pipeline de testing
- Agregado cliente Eureka

### Correcciones
- Corregido el comando `flask run`
- Mejorado el Dockerfile
- Automatizada la versión

## [2024.07.25] - 2024-07-25

### Características
- Agregado soporte para comprobantes asociados
- Agregado logging de errores en autorización de comprobantes
- Implementado redondeo de neto e IVA para evitar errores de AFIP

## [2024.09.14] - 2024-10-05

### Mejoras
- Agregadas variables de entorno
- Actualizado Dockerfile
- Agregado logging de certificados
- Agregados mensajes de error
- Mejorado el sistema de logging

## [2024.11.07] - 2024-12-02

### Mejoras
- Mejorado el sistema de logging
- Refactorizado y mejorado el código original
- Ajustados los valores float para mantener el tipo de los operandos

## [2025.01.14] - 2025.01.14

### Mejoras
- Restaurada la verificación de estado de servidores AFIP
- Removido logging de debug hardcodeado
- Mejorado el manejo de autenticación
- Mejorado el logging de la integración con AFIP
- Deshabilitado el cache para la integración con AFIP

## Notas
- Todos los cambios están basados en commits reales del repositorio
- Las fechas están en formato YYYY-MM-DD
- Los cambios están organizados cronológicamente de más reciente a más antiguo 