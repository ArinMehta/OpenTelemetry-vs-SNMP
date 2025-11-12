#!/usr/bin/env python3
"""
OpenTelemetry Instrumentation Helper
Provides utilities for instrumenting network applications
"""

from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
import os


def setup_opentelemetry(service_name: str = "network-service"):
    """
    Setup OpenTelemetry with OTLP exporters
    
    Args:
        service_name: Name of the service being instrumented
    """
    # Get OTLP endpoint from environment
    otlp_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4317")
    
    # Create resource with service information
    resource = Resource.create({
        "service.name": service_name,
        "service.version": os.getenv("OTEL_SERVICE_VERSION", "1.0.0"),
        "deployment.environment": os.getenv("OTEL_DEPLOYMENT_ENV", "development"),
    })
    
    # Setup Tracing
    trace_exporter = OTLPSpanExporter(endpoint=otlp_endpoint, insecure=True)
    trace_provider = TracerProvider(resource=resource)
    trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
    trace.set_tracer_provider(trace_provider)
    
    # Setup Metrics
    metric_exporter = OTLPMetricExporter(endpoint=otlp_endpoint, insecure=True)
    metric_reader = PeriodicExportingMetricReader(
        metric_exporter,
        export_interval_millis=10000  # Export every 10 seconds
    )
    meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
    metrics.set_meter_provider(meter_provider)
    
    print(f"OpenTelemetry initialized for service: {service_name}")
    print(f"OTLP Endpoint: {otlp_endpoint}")
    
    return trace.get_tracer(__name__), metrics.get_meter(__name__)


def create_network_metrics(meter):
    """
    Create standard network monitoring metrics
    
    Args:
        meter: OpenTelemetry Meter instance
        
    Returns:
        Dictionary of metric instruments
    """
    return {
        "latency": meter.create_histogram(
            name="network.latency",
            description="Network latency in milliseconds",
            unit="ms"
        ),
        "throughput": meter.create_histogram(
            name="network.throughput",
            description="Network throughput in bytes per second",
            unit="bytes/s"
        ),
        "packet_loss": meter.create_counter(
            name="network.packet_loss",
            description="Number of lost packets",
            unit="1"
        ),
        "errors": meter.create_counter(
            name="network.errors",
            description="Number of network errors",
            unit="1"
        ),
        "connections": meter.create_up_down_counter(
            name="network.connections",
            description="Number of active connections",
            unit="1"
        ),
    }


if __name__ == "__main__":
    # Example usage
    tracer, meter = setup_opentelemetry("example-service")
    
    # Create metrics
    network_metrics = create_network_metrics(meter)
    
    # Example: Record a latency measurement
    with tracer.start_as_current_span("example_operation") as span:
        span.set_attribute("operation.type", "ping")
        network_metrics["latency"].record(25.5, {"target": "8.8.8.8"})
        print("Recorded latency measurement")

