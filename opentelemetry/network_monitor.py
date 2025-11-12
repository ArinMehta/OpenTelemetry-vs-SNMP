#!/usr/bin/env python3
"""
Network Monitor with OpenTelemetry Instrumentation
Collects network performance metrics and sends them to OpenTelemetry Collector
"""

import time
import random
import socket
import psutil
import subprocess
from typing import Dict, List
from datetime import datetime

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from prometheus_client import start_http_server, Gauge, Counter, Histogram


class NetworkMonitor:
    """Monitor network performance using OpenTelemetry"""
    
    def __init__(self, otel_endpoint: str = "http://otel-collector:4317"):
        # Setup OpenTelemetry
        self.setup_otel(otel_endpoint)
        
        # Setup Prometheus metrics for direct scraping
        self.setup_prometheus_metrics()
        
        # Network targets to monitor
        self.targets = [
            "8.8.8.8",  # Google DNS
            "1.1.1.1",  # Cloudflare DNS
        ]
        
    def setup_otel(self, endpoint: str):
        """Setup OpenTelemetry metrics and tracing"""
        # Resource attributes
        resource = Resource.create({
            "service.name": "network-monitor",
            "service.version": "1.0.0",
            "deployment.environment": "development"
        })
        
        # Metrics setup
        metric_exporter = OTLPMetricExporter(endpoint=endpoint, insecure=True)
        metric_reader = PeriodicExportingMetricReader(metric_exporter, export_interval_millis=10000)
        meter_provider = MeterProvider(resource=resource, metric_readers=[metric_reader])
        metrics.set_meter_provider(meter_provider)
        
        self.meter = metrics.get_meter(__name__)
        
        # Create metrics
        self.latency_histogram = self.meter.create_histogram(
            name="network.latency",
            description="Network latency in milliseconds",
            unit="ms"
        )
        
        self.packet_loss_counter = self.meter.create_counter(
            name="network.packet_loss",
            description="Number of lost packets",
            unit="1"
        )
        
        self.bandwidth_gauge = self.meter.create_observable_gauge(
            name="network.bandwidth",
            description="Network bandwidth usage",
            unit="bytes",
            callbacks=[self.get_bandwidth]
        )
        
        self.connection_gauge = self.meter.create_observable_gauge(
            name="network.connections",
            description="Number of active network connections",
            unit="1",
            callbacks=[self.get_connections]
        )
        
        # Tracing setup
        trace_exporter = OTLPSpanExporter(endpoint=endpoint, insecure=True)
        trace_provider = TracerProvider(resource=resource)
        trace_provider.add_span_processor(BatchSpanProcessor(trace_exporter))
        trace.set_tracer_provider(trace_provider)
        
        self.tracer = trace.get_tracer(__name__)
        
    def setup_prometheus_metrics(self):
        """Setup Prometheus metrics for direct scraping"""
        self.prom_latency = Histogram(
            'network_latency_ms',
            'Network latency in milliseconds',
            ['target', 'protocol']
        )
        
        self.prom_packet_loss = Counter(
            'network_packet_loss_total',
            'Total number of lost packets',
            ['target']
        )
        
        self.prom_bandwidth_tx = Gauge(
            'network_bandwidth_tx_bytes',
            'Network bandwidth transmitted in bytes',
            ['interface']
        )
        
        self.prom_bandwidth_rx = Gauge(
            'network_bandwidth_rx_bytes',
            'Network bandwidth received in bytes',
            ['interface']
        )
        
        self.prom_connections = Gauge(
            'network_connections_active',
            'Number of active network connections',
            ['state']
        )
        
    def get_bandwidth(self, options):
        """Callback to get bandwidth metrics"""
        net_io = psutil.net_io_counters()
        yield metrics.Observation(net_io.bytes_sent, {"direction": "tx"})
        yield metrics.Observation(net_io.bytes_recv, {"direction": "rx"})
        
    def get_connections(self, options):
        """Callback to get connection count"""
        connections = psutil.net_connections()
        yield metrics.Observation(len(connections))
        
    def measure_latency(self, target: str) -> float:
        """Measure network latency using ping"""
        with self.tracer.start_as_current_span("measure_latency") as span:
            span.set_attribute("target", target)
            
            try:
                # Use ping command
                result = subprocess.run(
                    ['ping', '-c', '1', '-W', '2', target],
                    capture_output=True,
                    text=True,
                    timeout=3
                )
                
                if result.returncode == 0:
                    # Parse ping output for latency
                    output = result.stdout
                    if 'time=' in output:
                        latency_str = output.split('time=')[1].split()[0]
                        latency = float(latency_str)
                        
                        # Record to OpenTelemetry
                        self.latency_histogram.record(latency, {"target": target, "protocol": "icmp"})
                        
                        # Record to Prometheus
                        self.prom_latency.labels(target=target, protocol='icmp').observe(latency)
                        
                        span.set_attribute("latency_ms", latency)
                        return latency
                else:
                    # Packet loss
                    self.packet_loss_counter.add(1, {"target": target})
                    self.prom_packet_loss.labels(target=target).inc()
                    span.set_attribute("packet_loss", True)
                    return -1
                    
            except Exception as e:
                span.record_exception(e)
                print(f"Error measuring latency to {target}: {e}")
                return -1
                
    def collect_network_stats(self):
        """Collect network interface statistics"""
        with self.tracer.start_as_current_span("collect_network_stats"):
            net_io = psutil.net_io_counters(pernic=True)
            
            for interface, stats in net_io.items():
                self.prom_bandwidth_tx.labels(interface=interface).set(stats.bytes_sent)
                self.prom_bandwidth_rx.labels(interface=interface).set(stats.bytes_recv)
                
    def collect_connection_stats(self):
        """Collect connection statistics"""
        with self.tracer.start_as_current_span("collect_connection_stats"):
            connections = psutil.net_connections()
            
            # Count by state
            state_counts = {}
            for conn in connections:
                state = conn.status
                state_counts[state] = state_counts.get(state, 0) + 1
                
            for state, count in state_counts.items():
                self.prom_connections.labels(state=state).set(count)
                
    def run(self):
        """Main monitoring loop"""
        print("Starting Network Monitor with OpenTelemetry...")
        print(f"Monitoring targets: {', '.join(self.targets)}")
        
        # Start Prometheus HTTP server
        start_http_server(8080)
        print("Prometheus metrics available at http://localhost:8080/metrics")
        
        while True:
            try:
                # Measure latency to all targets
                for target in self.targets:
                    latency = self.measure_latency(target)
                    if latency > 0:
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                              f"Latency to {target}: {latency:.2f} ms")
                    else:
                        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] "
                              f"Packet loss to {target}")
                
                # Collect network statistics
                self.collect_network_stats()
                self.collect_connection_stats()
                
                # Wait before next collection
                time.sleep(10)
                
            except KeyboardInterrupt:
                print("\nStopping Network Monitor...")
                break
            except Exception as e:
                print(f"Error in monitoring loop: {e}")
                time.sleep(10)


if __name__ == "__main__":
    import os
    
    # Get OTLP endpoint from environment or use default
    otel_endpoint = os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT", "http://otel-collector:4317")
    
    monitor = NetworkMonitor(otel_endpoint)
    monitor.run()

