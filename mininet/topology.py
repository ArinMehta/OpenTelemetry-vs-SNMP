#!/usr/bin/env python3
"""
Mininet Network Topology for Monitoring Project
Creates a routed network topology with two subnets and one router.
"""

from mininet.net import Mininet
from mininet.node import OVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink
import time
import os

def create_topology():
    """
    Create network topology:
    
    Subnet 1 (10.0.1.0/24)              Subnet 2 (10.0.2.0/24)
    h1 (101) --- s1 --- r1 (1) --- s2 --- h4 (104)
    h2 (102) ---/       |          |       \--- h5 (105)
    h3 (103) ---/       |          |       \--- h6 (106)
                        |          |
                   (10.0.1.1)    (10.0.2.1)
    """
    
    info('*** Creating network\n')
    net = Mininet(
        switch=OVSSwitch,
        link=TCLink,
        autoSetMacs=True
    )
    
    info('*** Adding switches (in standalone mode)\n')
    s1 = net.addSwitch('s1', failMode='standalone')
    s2 = net.addSwitch('s2', failMode='standalone')
    
    info('*** Adding router (r1)\n')
    # Add r1 as a host, we will configure it to act as a router
    r1 = net.addHost('r1')

    info('*** Adding hosts\n')
    # Subnet 1: 10.0.1.0/24
    h1 = net.addHost('h1', ip='10.0.1.101/24', defaultRoute='via 10.0.1.1')
    h2 = net.addHost('h2', ip='10.0.1.102/24', defaultRoute='via 10.0.1.1')
    h3 = net.addHost('h3', ip='10.0.1.103/24', defaultRoute='via 10.0.1.1')
    
    # Subnet 2: 10.0.2.0/24
    h4 = net.addHost('h4', ip='10.0.2.104/24', defaultRoute='via 10.0.2.1')
    h5 = net.addHost('h5', ip='10.0.2.105/24', defaultRoute='via 10.0.2.1')
    h6 = net.addHost('h6', ip='10.0.2.106/24', defaultRoute='via 10.0.2.1')
    
    info('*** Creating links\n')
    # Links for Subnet 1
    net.addLink(h1, s1, bw=100, delay='5ms', loss=0)
    net.addLink(h2, s1, bw=100, delay='5ms', loss=0)
    net.addLink(h3, s1, bw=50, delay='10ms', loss=1)
    
    # Links for Subnet 2
    net.addLink(h4, s2, bw=100, delay='5ms', loss=0)
    net.addLink(h5, s2, bw=10, delay='20ms', loss=2)
    net.addLink(h6, s2, bw=100, delay='5ms', loss=0)

    # Link Router to Switches
    # r1-eth0 will be on Subnet 1
    net.addLink(r1, s1, bw=1000, delay='2ms', loss=0) 
    # r1-eth1 will be on Subnet 2
    net.addLink(r1, s2, bw=1000, delay='2ms', loss=0)
    
    info('*** Starting network\n')
    net.start()

    # --- Configure Router (r1) ---
    info('*** Configuring router r1\n')
    
    # Manually configure interface IPs for the router
    r1.cmd('ifconfig r1-eth0 10.0.1.1/24 up')
    r1.cmd('ifconfig r1-eth1 10.0.2.1/24 up')
    
    # Enable IP forwarding on r1
    r1.cmd('sysctl -w net.ipv4.ip_forward=1')

    # Add NAT for internet connectivity
    nat = add_nat(net, inet_intf='eth0')  # change to 'ens33' if your VM uses that
    
    info('*** Network topology:\n')
    info('h1-h3 (10.0.1.x/24) --- s1 --- r1 --- s2 --- h4-h6 (10.0.2.x/24)\n')
    
    return net


def setup_snmp_agents(net):
    """Setup SNMP agents on hosts AND the router"""
    info('*** Setting up SNMP agents on all nodes (hosts + router)...\n')
    
    # The 'net.hosts' list now includes h1-h6 AND r1
    for host in net.hosts:
        info(f'Configuring SNMP and tools on {host.name}...\n')
        
        # Install snmpd, curl, and iperf (quietly)
        host.cmd('apt-get update -qq > /dev/null 2>&1')
        host.cmd('apt-get install -y -qq snmpd curl iperf > /dev/null 2>&1')
        
        # Configure snmpd.conf to listen on all interfaces
        conf = """
agentAddress udp:161
rocommunity public
sysLocation "Mininet_{host.name}"
sysContact "admin@localhost"
        """
        # Use 'echo' to write the file, ensuring correct permissions
        host.cmd(f"echo '{conf}' > /etc/snmp/snmpd.conf")
        
        # Restart the service to apply changes
        host.cmd('service snmpd restart')
                
        info(f'SNMP agent started on {host.name}\n')


def run_tests(net):
    """Run basic connectivity tests"""
    info('*** Running connectivity tests\n')
    
    h1, h2, h6 = net.get('h1', 'h2', 'h6')
    
    # Ping test (same subnet)
    info('*** Ping test: h1 -> h2 (same subnet)\n')
    result = h1.cmd(f'ping -c 3 {h2.IP()}')
    info(result)
    
    # Ping test (different subnet, should work via router)
    info('*** Ping test: h1 -> h6 (across router)\n')
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
    # net.hosts includes r1, so it will get a server too
    for i, host in enumerate(net.hosts, 1):
        port = 8000 + i
        host.cmd(f'python3 -m http.server {port} &')
        info(f'HTTP server started on {host.name}:{port}\n')

from mininet.node import Node

def add_nat(net, connect_to='r1-eth2', inet_intf='eth0'):
    """
    Add a NAT node that provides internet access to Mininet hosts.
    """
    info('*** Adding NAT node\n')
    nat = net.addHost('nat', inNamespace=False)  # not in Mininet namespace
    
    # Link NAT to router
    net.addLink(nat, net.get('r1'))
    
    info('*** Configuring NAT\n')
    nat.cmd('sysctl -w net.ipv4.ip_forward=1')
    
    # Identify external interface (host side, usually eth0 or ens33)
    info(f'*** Using external interface {inet_intf} for internet access\n')
    
    # Flush old rules
    nat.cmd('iptables -F')
    nat.cmd('iptables -t nat -F')
    
    # Masquerade traffic from Mininet (10.0.0.0/8 is broad enough to cover both subnets)
    nat.cmd(f'iptables -t nat -A POSTROUTING -s 10.0.0.0/8 -o {inet_intf} -j MASQUERADE')
    nat.cmd('iptables -A FORWARD -i %s -o %s -m state --state RELATED,ESTABLISHED -j ACCEPT' % (inet_intf, connect_to))
    nat.cmd('iptables -A FORWARD -o %s -i %s -j ACCEPT' % (inet_intf, connect_to))

    info('*** NAT configured. Mininet hosts should now reach the Internet.\n')
    return nat


def main():
    """Main function"""
    setLogLevel('info')
    
    if os.getuid() != 0:
        info('*** Warning: Mininet must be run as root.\n')
        info('*** Please run: sudo python3 mininet/topology.py\n')
        return

    # Create topology
    net = create_topology()
    
    # Setup SNMP agents on all nodes (h1-h6 and r1)
    setup_snmp_agents(net)
    
    # Run connectivity tests
    run_tests(net)
    
    # Start monitoring services
    start_monitoring(net)
    
    info('*** Network is ready!\n')
    info('*** You can now:\n')
    info('    1. (From h1) Run traffic generator: python3 mininet/traffic_generator.py\n')
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