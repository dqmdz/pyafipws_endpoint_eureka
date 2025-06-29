"""
Configuración de OpenTelemetry para observabilidad.
Se integra con el sistema Jaeger + Elasticsearch existente.
"""
import os
import logging
from typing import Optional

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.logger_setup import logger

def setup_otel() -> Optional[trace.Tracer]:
    """
    Configura OpenTelemetry para el servicio.
    
    Returns:
        Optional[trace.Tracer]: El tracer configurado o None si no se puede configurar
    """
    try:
        otel_endpoint = os.getenv('OTEL_EXPORTER_OTLP_ENDPOINT')
        if not otel_endpoint:
            logger.info("OpenTelemetry no configurado - OTEL_EXPORTER_OTLP_ENDPOINT no definido")
            return None

        # Forzar el endpoint correcto para el exporter HTTP
        otlp_exporter = OTLPSpanExporter(
            endpoint=f"{otel_endpoint}/v1/traces"
        )
        
        # Configurar el recurso con información del servicio
        resource = Resource.create({
            "service.name": "pyafipws-service",
            "service.version": "1.0.0",
            "deployment.environment": "production" if os.getenv('PRODUCTION', 'FALSE').upper() == 'TRUE' else "development"
        })
        
        # Configurar el proveedor de trazas
        trace_provider = TracerProvider(resource=resource)
        
        # Configurar el procesador de spans
        span_processor = BatchSpanProcessor(otlp_exporter)
        trace_provider.add_span_processor(span_processor)
        
        # Establecer el proveedor de trazas global
        trace.set_tracer_provider(trace_provider)
        
        # Obtener el tracer
        tracer = trace.get_tracer(__name__)
        
        logger.info(f"OpenTelemetry configurado exitosamente con endpoint: {otel_endpoint}/v1/traces")
        return tracer
        
    except Exception as e:
        logger.error(f"Error configurando OpenTelemetry: {e}")
        return None

def instrument_app(app):
    """
    Instrumenta la aplicación Flask con OpenTelemetry.
    
    Args:
        app: La aplicación Flask a instrumentar
    """
    try:
        # Instrumentar Flask
        FlaskInstrumentor().instrument_app(app)
        logger.info("Flask instrumentado con OpenTelemetry")
        
        # Instrumentar requests
        RequestsInstrumentor().instrument()
        logger.info("Requests instrumentado con OpenTelemetry")
        
        # Instrumentar logging
        LoggingInstrumentor().instrument(
            set_logging_format=True,
            log_level=logging.INFO
        )
        logger.info("Logging instrumentado con OpenTelemetry")
        
    except Exception as e:
        logger.error(f"Error instrumentando la aplicación: {e}")

def get_tracer() -> Optional[trace.Tracer]:
    """
    Obtiene el tracer de OpenTelemetry configurado.
    
    Returns:
        Optional[trace.Tracer]: El tracer configurado o None
    """
    try:
        return trace.get_tracer(__name__)
    except Exception:
        return None 