#!/usr/bin/env python3
"""
SNMP Data Collector
Collects network metrics using SNMP and exposes them for Prometheus
"""

import time
import os
from datetime import datetime
from pysnmp.hlapi import *
from prometheus_client import start_http_server, Gauge, Counter, Info
from typing import Dict, List, Tuple

print("DEBUG: collect_snmp starting")

class SNMPCollector:
    """Collect network metrics using SNMP"""
    
    # Common SNMP OIDs
    OIDS = {
        # System Information
        'sysDescr': '1.3.6.1.2.1.1.1.0',
        'sysUpTime': '1.3.6.1.2.1.1.3.0',
        'sysName': '1.3.6.1.2.1.1.5.0',
        
        # Interface Statistics (IF-MIB)
        'ifNumber': '1.3.6.1.2.1.2.1.0',
        'ifDescr': '1.3.6.1.2.1.2.2.1.2',
        'ifType': '1.3.6.1.2.1.2.2.1.3',
        'ifSpeed': '1.3.6.1.2.1.2.2.1.5',
        'ifPhysAddress': '1.3.6.1.2.1.2.2.1.6',
        'ifAdminStatus': '1.3.6.1.2.1.2.2.1.7',
        'ifOperStatus': '1.3.6.1.2.1.2.2.1.8',
        'ifInOctets': '1.3.6.1.2.1.2.2.1.10',
        'ifInUcastPkts': '1.3.6.1.2.1.2.2.1.11',
        'ifInErrors': '1.3.6.1.2.1.2.2.1.14',
        'ifOutOctets': '1.3.6.1.2.1.2.2.1.16',
        'ifOutUcastPkts': '1.3.6.1.2.1.2.2.1.17',
        'ifOutErrors': '1.3.6.1.2.1.2.2.1.20',
        
        # IP Statistics
        'ipInReceives': '1.3.6.1.2.1.4.3.0',
        'ipInDelivers': '1.3.6.1.2.1.4.9.0',
        'ipOutRequests': '1.3.6.1.2.1.4.10.0',
        
        # TCP Statistics
        'tcpActiveOpens': '1.3.6.1.2.1.6.5.0',
        'tcpPassiveOpens': '1.3.6.1.2.1.6.6.0',
        'tcpCurrEstab': '1.3.6.1.2.1.6.9.0',
        'tcpInSegs': '1.3.6.1.2.1.6.10.0',
        'tcpOutSegs': '1.3.6.1.2.1.6.11.0',
        
        # UDP Statistics
        'udpInDatagrams': '1.3.6.1.2.1.7.1.0',
        'udpOutDatagrams': '1.3.6.1.2.1.7.4.0',
    }
    
    def __init__(self, target: str, community: str = 'public', version: str = '2c'):
        self.target = target
        self.community = community
        self.version = version
        
        # Setup Prometheus metrics
        self.setup_prometheus_metrics()
        
        # Store previous values for rate calculation
        self.previous_values = {}
        self.previous_time = time.time()
        
    def setup_prometheus_metrics(self):
        """Setup Prometheus metrics"""
        # System info
        self.system_info = Info('snmp_system', 'SNMP system information')
        self.system_uptime = Gauge('snmp_system_uptime_seconds', 'System uptime in seconds')
        
        # Interface metrics
        self.if_in_octets = Gauge('snmp_if_in_octets_total', 'Incoming octets', ['interface'])
        self.if_out_octets = Gauge('snmp_if_out_octets_total', 'Outgoing octets', ['interface'])
        self.if_in_packets = Gauge('snmp_if_in_packets_total', 'Incoming packets', ['interface'])
        self.if_out_packets = Gauge('snmp_if_out_packets_total', 'Outgoing packets', ['interface'])
        self.if_in_errors = Gauge('snmp_if_in_errors_total', 'Incoming errors', ['interface'])
        self.if_out_errors = Gauge('snmp_if_out_errors_total', 'Outgoing errors', ['interface'])
        self.if_speed = Gauge('snmp_if_speed_bps', 'Interface speed in bits per second', ['interface'])
        self.if_status = Gauge('snmp_if_status', 'Interface operational status (1=up, 2=down)', ['interface'])
        
        # Bandwidth utilization (calculated)
        self.if_bandwidth_utilization = Gauge('snmp_if_bandwidth_utilization_percent', 
                                               'Interface bandwidth utilization percentage', 
                                               ['interface', 'direction'])
        
        # IP metrics
        self.ip_in_receives = Counter('snmp_ip_in_receives_total', 'IP packets received')
        self.ip_in_delivers = Counter('snmp_ip_in_delivers_total', 'IP packets delivered')
        self.ip_out_requests = Counter('snmp_ip_out_requests_total', 'IP packets sent')
        
        # TCP metrics
        self.tcp_active_opens = Counter('snmp_tcp_active_opens_total', 'TCP active opens')
        self.tcp_passive_opens = Counter('snmp_tcp_passive_opens_total', 'TCP passive opens')
        self.tcp_curr_estab = Gauge('snmp_tcp_curr_estab', 'Current established TCP connections')
        self.tcp_in_segs = Counter('snmp_tcp_in_segs_total', 'TCP segments received')
        self.tcp_out_segs = Counter('snmp_tcp_out_segs_total', 'TCP segments sent')
        
        # UDP metrics
        self.udp_in_datagrams = Counter('snmp_udp_in_datagrams_total', 'UDP datagrams received')
        self.udp_out_datagrams = Counter('snmp_udp_out_datagrams_total', 'UDP datagrams sent')
        
    def snmp_get(self, oid: str) -> Tuple[bool, any]:
        """
        Perform SNMP GET operation
        
        Args:
            oid: SNMP OID to query
            
        Returns:
            Tuple of (success, value)
        """
        try:
            iterator = getCmd(
                SnmpEngine(),
                CommunityData(self.community),
                UdpTransportTarget((self.target, 161)),
                ContextData(),
                ObjectType(ObjectIdentity(oid))
            )
            
            errorIndication, errorStatus, errorIndex, varBinds = next(iterator)
            
            if errorIndication:
                print(f"SNMP Error: {errorIndication}")
                return False, None
            elif errorStatus:
                print(f"SNMP Error: {errorStatus.prettyPrint()}")
                return False, None
            else:
                for varBind in varBinds:
                    return True, varBind[1]
                    
        except Exception as e:
            print(f"Exception during SNMP GET: {e}")
            return False, None
            
    def snmp_walk(self, oid: str) -> List[Tuple[str, any]]:
        """
        Perform SNMP WALK operation
        
        Args:
            oid: SNMP OID to walk
            
        Returns:
            List of (oid, value) tuples
        """
        results = []
        try:
            for (errorIndication, errorStatus, errorIndex, varBinds) in nextCmd(
                SnmpEngine(),
                CommunityData(self.community),
                UdpTransportTarget((self.target, 161)),
                ContextData(),
                ObjectType(ObjectIdentity(oid)),
                lexicographicMode=False
            ):
                if errorIndication:
                    print(f"SNMP Error: {errorIndication}")
                    break
                elif errorStatus:
                    print(f"SNMP Error: {errorStatus.prettyPrint()}")
                    break
                else:
                    for varBind in varBinds:
                        results.append((str(varBind[0]), varBind[1]))
                        
        except Exception as e:
            print(f"Exception during SNMP WALK: {e}")
            
        return results
        
    def collect_system_info(self):
        """Collect system information"""
        success, sys_descr = self.snmp_get(self.OIDS['sysDescr'])
        if success:
            self.system_info.info({'description': str(sys_descr)})
            
        success, sys_uptime = self.snmp_get(self.OIDS['sysUpTime'])
        if success:
            # Convert from TimeTicks (hundredths of seconds) to seconds
            uptime_seconds = int(sys_uptime) / 100
            self.system_uptime.set(uptime_seconds)
            
    def collect_interface_stats(self):
        """Collect interface statistics"""
        # Get number of interfaces
        success, if_number = self.snmp_get(self.OIDS['ifNumber'])
        if not success:
            return
            
        num_interfaces = int(if_number)
        current_time = time.time()
        time_delta = current_time - self.previous_time
        
        for i in range(1, num_interfaces + 1):
            # Get interface description
            success, if_descr = self.snmp_get(f"{self.OIDS['ifDescr']}.{i}")
            if not success:
                continue
            interface_name = str(if_descr)
            
            # Get interface statistics
            success, in_octets = self.snmp_get(f"{self.OIDS['ifInOctets']}.{i}")
            if success:
                in_octets_val = int(in_octets)
                self.if_in_octets.labels(interface=interface_name).set(in_octets_val)
                
                # Calculate bandwidth utilization
                if f"in_octets_{i}" in self.previous_values and time_delta > 0:
                    prev_in_octets = self.previous_values[f"in_octets_{i}"]
                    bytes_per_sec = (in_octets_val - prev_in_octets) / time_delta
                    
                    # Get interface speed
                    success, if_speed = self.snmp_get(f"{self.OIDS['ifSpeed']}.{i}")
                    if success and int(if_speed) > 0:
                        bits_per_sec = bytes_per_sec * 8
                        utilization = (bits_per_sec / int(if_speed)) * 100
                        self.if_bandwidth_utilization.labels(
                            interface=interface_name, 
                            direction='in'
                        ).set(utilization)
                        
                self.previous_values[f"in_octets_{i}"] = in_octets_val
                
            success, out_octets = self.snmp_get(f"{self.OIDS['ifOutOctets']}.{i}")
            if success:
                out_octets_val = int(out_octets)
                self.if_out_octets.labels(interface=interface_name).set(out_octets_val)
                
                # Calculate bandwidth utilization
                if f"out_octets_{i}" in self.previous_values and time_delta > 0:
                    prev_out_octets = self.previous_values[f"out_octets_{i}"]
                    bytes_per_sec = (out_octets_val - prev_out_octets) / time_delta
                    
                    success, if_speed = self.snmp_get(f"{self.OIDS['ifSpeed']}.{i}")
                    if success and int(if_speed) > 0:
                        bits_per_sec = bytes_per_sec * 8
                        utilization = (bits_per_sec / int(if_speed)) * 100
                        self.if_bandwidth_utilization.labels(
                            interface=interface_name,
                            direction='out'
                        ).set(utilization)
                        
                self.previous_values[f"out_octets_{i}"] = out_octets_val
                
            # Other interface metrics
            success, in_packets = self.snmp_get(f"{self.OIDS['ifInUcastPkts']}.{i}")
            if success:
                self.if_in_packets.labels(interface=interface_name).set(int(in_packets))
                
            success, out_packets = self.snmp_get(f"{self.OIDS['ifOutUcastPkts']}.{i}")
            if success:
                self.if_out_packets.labels(interface=interface_name).set(int(out_packets))
                
            success, in_errors = self.snmp_get(f"{self.OIDS['ifInErrors']}.{i}")
            if success:
                self.if_in_errors.labels(interface=interface_name).set(int(in_errors))
                
            success, out_errors = self.snmp_get(f"{self.OIDS['ifOutErrors']}.{i}")
            if success:
                self.if_out_errors.labels(interface=interface_name).set(int(out_errors))
                
            success, if_speed = self.snmp_get(f"{self.OIDS['ifSpeed']}.{i}")
            if success:
                self.if_speed.labels(interface=interface_name).set(int(if_speed))
                
            success, oper_status = self.snmp_get(f"{self.OIDS['ifOperStatus']}.{i}")
            if success:
                self.if_status.labels(interface=interface_name).set(int(oper_status))
                
        self.previous_time = current_time

    def collect_ip_stats(self):
        """Collect IP statistics"""
        success, ip_in_receives = self.snmp_get(self.OIDS['ipInReceives'])
        if success:
            # Note: Prometheus Counter doesn't have a set method, we track the value
            pass

        success, ip_in_delivers = self.snmp_get(self.OIDS['ipInDelivers'])
        if success:
            pass

        success, ip_out_requests = self.snmp_get(self.OIDS['ipOutRequests'])
        if success:
            pass

    def collect_tcp_stats(self):
        """Collect TCP statistics"""
        success, tcp_curr_estab = self.snmp_get(self.OIDS['tcpCurrEstab'])
        if success:
            self.tcp_curr_estab.set(int(tcp_curr_estab))

    def collect_udp_stats(self):
        """Collect UDP statistics"""
        pass  # Similar to TCP stats

    def collect_all(self):
        """Collect all metrics"""
        print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Collecting SNMP metrics from {self.target}...")

        try:
            self.collect_system_info()
            self.collect_interface_stats()
            self.collect_ip_stats()
            self.collect_tcp_stats()
            self.collect_udp_stats()
            print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Collection complete")
        except Exception as e:
            print(f"Error collecting metrics: {e}")

    def run(self, interval: int = 15):
        """
        Run the collector continuously

        Args:
            interval: Collection interval in seconds
        """
        print(f"Starting SNMP Collector for {self.target}")
        print(f"Community: {self.community}, Version: {self.version}")
        print(f"Collection interval: {interval} seconds")

        # Start Prometheus HTTP server
        start_http_server(8000)
        print("Prometheus metrics available at http://localhost:8000/metrics")

        while True:
            try:
                self.collect_all()
                time.sleep(interval)
            except KeyboardInterrupt:
                print("\nStopping SNMP Collector...")
                break
            except Exception as e:
                print(f"Error in collection loop: {e}")
                time.sleep(interval)


if __name__ == "__main__":
    # Get configuration from environment variables
    target = os.getenv("SNMP_TARGET", "snmp-simulator")
    community = os.getenv("SNMP_COMMUNITY", "public")
    version = os.getenv("SNMP_VERSION", "2c")
    interval = int(os.getenv("SNMP_INTERVAL", "15"))

    collector = SNMPCollector(target, community, version)
    collector.run(interval)

