# Changelog

Todos los cambios notables en este proyecto serán documentados en este archivo.

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