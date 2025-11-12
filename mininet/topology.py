#!/usr/bin/env python3
"""
Mininet Network Topology for Monitoring Project
Creates a simple network topology with hosts and switches
"""

from mininet.net import Mininet
# from mininet.node import Controller, OVSSwitch  <-- Removed Controller
from mininet.node import OVSSwitch # <-- Kept OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import time


def create_topology():
    info('*** Creating network\n')
    net = Mininet(
        switch=OVSSwitch,
        link=TCLink,
        autoSetMacs=True,
        autoStaticArp=True
    )
    
    info('*** Adding switches (in standalone mode)\n')
    s1 = net.addSwitch('s1', failMode='standalone')
    s2 = net.addSwitch('s2', failMode='standalone')
    
    info('*** Adding hosts\n')
    h1 = net.addHost('h1', ip='10.0.0.1/24')
    h2 = net.addHost('h2', ip='10.0.0.2/24')
    h3 = net.addHost('h3', ip='10.0.0.3/24')
    h4 = net.addHost('h4', ip='10.0.0.4/24')
    h5 = net.addHost('h5', ip='10.0.0.5/24')
    h6 = net.addHost('h6', ip='10.0.0.6/24')
    
    info('*** Creating links\n')
    net.addLink(h1, s1, bw=100, delay='5ms', loss=0)
    net.addLink(h2, s1, bw=100, delay='5ms', loss=0)
    net.addLink(h3, s1, bw=50, delay='10ms', loss=1)
    net.addLink(h3, s2, bw=50, delay='10ms', loss=1)
    net.addLink(h4, s2, bw=100, delay='5ms', loss=0)
    net.addLink(h5, s2, bw=10, delay='20ms', loss=2)
    net.addLink(h6, s2, bw=100, delay='5ms', loss=0)
    net.addLink(s1, s2, bw=1000, delay='2ms', loss=0)
    
    info('*** Starting network\n')
    net.start()

    return net


def setup_snmp_agents(net):
    """Setup SNMP agents on hosts, as per the troubleshooting guide"""
    info('*** Setting up SNMP agents on all hosts...\n')
    
    for host in net.hosts:
        info(f'Configuring SNMP on {host.name} ({host.IP()})...\n')
        host.cmd('apt-get update -qq > /dev/null 2>&1')

        # Install snmpd AND the tools needed by the traffic generator
        info(f'Installing tools (snmpd, curl, iperf) on {host.name}...\n')
        host.cmd('apt-get install -y -qq snmpd curl iperf > /dev/null 2>&1')
        
        # Configure snmpd.conf to listen on all interfaces (0.0.0.0)
        conf = """
agentAddress udp:161
rocommunity public
sysLocation "Mininet Lab"
sysContact "admin@project.local"
        """
        # Use 'echo' to write the file, ensuring correct permissions
        host.cmd(f"echo '{conf}' > /etc/snmp/snmpd.conf")
        
        # Restart the service to apply changes
        host.cmd('service snmpd restart')
                
        info(f'SNMP agent started on {host.name}\n')


def run_tests(net):
    """Run basic connectivity tests"""
    info('*** Running connectivity tests\n')
    
    # Ping test
    info('*** Ping test: h1 -> h2\n')
    h1 = net.get('h1')
    h2 = net.get('h2')
    result = h1.cmd(f'ping -c 3 {h2.IP()}')
    info(result)
    
    info('*** Ping test: h1 -> h6\n')
    h6 = net.get('h6')
    result = h1.cmd(f'ping -c 3 {h6.IP()}')
    info(result)
    
    # Bandwidth test using iperf
    info('*** Bandwidth test: h1 -> h2\n')
    h2.cmd('iperf -s &')
    time.sleep(1)
    result = h1.cmd(f'iperf -c {h2.IP()} -t 5')
    info(result)
    h2.cmd('kill %iperf')


def start_monitoring(net):
    """Start monitoring services on hosts"""
    info('*** Starting monitoring services\n')
    
    # Start simple HTTP servers for testing
    for i, host in enumerate(net.hosts, 1):
        port = 8000 + i
        host.cmd(f'python3 -m http.server {port} &')
        info(f'HTTP server started on {host.name}:{port}\n')


def main():
    """Main function"""
    setLogLevel('info')
    
    net = create_topology()

    info('*** Automating SNMP setup as per troubleshooting plan...\n')
    setup_snmp_agents(net)
    
    # Run connectivity tests
    run_tests(net)
    
    # Start monitoring services
    start_monitoring(net)
    
    info('*** Network is ready!\n')
    info('*** You can now:\n')
    info('    1. Run traffic generator: python mininet/traffic_generator.py\n')
    info('    2. Access Grafana: http://localhost:3000\n')
    info('    3. Access Prometheus: http://localhost:9090\n')
    info('*** Starting CLI (type "exit" to quit)\n')
    
    # Start CLI
    CLI(net)
    
    # Cleanup
    info('*** Stopping network\n')
    net.stop()


if __name__ == '__main__':
    main()