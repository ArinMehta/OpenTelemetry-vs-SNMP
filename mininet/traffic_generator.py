#!/usr/bin/env python3
"""
Network Traffic Generator
Generates various types of network traffic for testing monitoring systems
"""

import time
import random
import subprocess
import threading
from datetime import datetime
from typing import List


class TrafficGenerator:
    """Generate network traffic for monitoring"""
    
    def __init__(self, targets: List[str] = None):
        if targets is None:
            self.targets = [
                '10.0.0.1',
                '10.0.0.2',
                '10.0.0.3',
                '10.0.0.4',
                '10.0.0.5',
                '10.0.0.6',
            ]
        else:
            self.targets = targets
            
        self.running = False
        
    def generate_ping_traffic(self, target: str, count: int = 10):
        """Generate ICMP ping traffic"""
        try:
            result = subprocess.run(
                ['ping', '-c', str(count), target],
                capture_output=True,
                text=True,
                timeout=count + 5
            )
            
            if result.returncode == 0:
                # Parse statistics
                output = result.stdout
                if 'min/avg/max' in output:
                    stats_line = output.split('min/avg/max')[1].split('\n')[0]
                    print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                          f"Ping to {target}: {stats_line}")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"Ping to {target}: FAILED")
                      
        except Exception as e:
            print(f"Error generating ping traffic to {target}: {e}")
            
    def generate_http_traffic(self, target: str, port: int = 80):
        """Generate HTTP traffic"""
        try:
            result = subprocess.run(
                ['curl', '-s', '-o', '/dev/null', '-w', '%{time_total}',
                 f'http://{target}:{port}'],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                response_time = float(result.stdout) * 1000  # Convert to ms
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"HTTP to {target}:{port}: {response_time:.2f} ms")
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"HTTP to {target}:{port}: FAILED")
                      
        except Exception as e:
            print(f"Error generating HTTP traffic to {target}:{port}: {e}")
            
    def generate_udp_traffic(self, target: str, port: int = 5000, size: int = 1024):
        """Generate UDP traffic"""
        try:
            # Use netcat or similar tool
            data = 'X' * size
            result = subprocess.run(
                ['echo', data, '|', 'nc', '-u', '-w', '1', target, str(port)],
                shell=True,
                capture_output=True,
                timeout=5
            )
            
            print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                  f"UDP to {target}:{port}: {size} bytes sent")
                  
        except Exception as e:
            print(f"Error generating UDP traffic to {target}:{port}: {e}")
            
    def generate_tcp_traffic(self, target: str, port: int = 5001, duration: int = 5):
        """Generate TCP traffic using iperf"""
        try:
            result = subprocess.run(
                ['iperf', '-c', target, '-p', str(port), '-t', str(duration)],
                capture_output=True,
                text=True,
                timeout=duration + 10
            )
            
            if result.returncode == 0:
                # Parse bandwidth from output
                output = result.stdout
                if 'Mbits/sec' in output:
                    lines = output.split('\n')
                    for line in lines:
                        if 'Mbits/sec' in line:
                            print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                                  f"TCP to {target}:{port}: {line.strip()}")
                            break
            else:
                print(f"[{datetime.now().strftime('%H:%M:%S')}] "
                      f"TCP to {target}:{port}: FAILED")
                      
        except Exception as e:
            print(f"Error generating TCP traffic to {target}:{port}: {e}")
            
    def generate_mixed_traffic(self):
        """Generate mixed traffic patterns"""
        print(f"\n{'='*60}")
        print(f"Starting mixed traffic generation at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*60}\n")
        
        while self.running:
            # Randomly select traffic type and target
            target = random.choice(self.targets)
            traffic_type = random.choice(['ping', 'http', 'udp'])
            
            if traffic_type == 'ping':
                self.generate_ping_traffic(target, count=5)
            elif traffic_type == 'http':
                port = random.randint(8001, 8006)
                self.generate_http_traffic(target, port)
            elif traffic_type == 'udp':
                port = random.randint(5000, 5010)
                size = random.randint(512, 2048)
                self.generate_udp_traffic(target, port, size)
                
            # Random delay between traffic bursts
            delay = random.uniform(1, 5)
            time.sleep(delay)
            
    def generate_burst_traffic(self, duration: int = 30):
        """Generate burst traffic for stress testing"""
        print(f"\n{'='*60}")
        print(f"Starting burst traffic for {duration} seconds")
        print(f"{'='*60}\n")
        
        start_time = time.time()
        threads = []
        
        while time.time() - start_time < duration:
            # Create multiple threads for concurrent traffic
            for target in self.targets[:3]:  # Use first 3 targets
                t = threading.Thread(target=self.generate_ping_traffic, args=(target, 10))
                t.start()
                threads.append(t)
                
            # Wait for threads to complete
            for t in threads:
                t.join()
                
            threads.clear()
            time.sleep(2)
            
        print(f"\nBurst traffic completed")
        
    def generate_latency_test(self):
        """Generate traffic to measure latency variations"""
        print(f"\n{'='*60}")
        print(f"Starting latency test")
        print(f"{'='*60}\n")
        
        for i in range(10):
            for target in self.targets:
                self.generate_ping_traffic(target, count=1)
            time.sleep(5)
            
        print(f"\nLatency test completed")
        
    def start(self, mode: str = 'mixed'):
        """
        Start traffic generation
        
        Args:
            mode: Traffic generation mode ('mixed', 'burst', 'latency')
        """
        self.running = True
        
        try:
            if mode == 'mixed':
                self.generate_mixed_traffic()
            elif mode == 'burst':
                self.generate_burst_traffic()
            elif mode == 'latency':
                self.generate_latency_test()
            else:
                print(f"Unknown mode: {mode}")
                
        except KeyboardInterrupt:
            print("\n\nStopping traffic generation...")
            self.running = False
            
    def stop(self):
        """Stop traffic generation"""
        self.running = False


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description='Network Traffic Generator')
    parser.add_argument('--mode', choices=['mixed', 'burst', 'latency'],
                        default='mixed', help='Traffic generation mode')
    parser.add_argument('--targets', nargs='+', help='Target IP addresses')
    parser.add_argument('--duration', type=int, default=300,
                        help='Duration in seconds (for burst mode)')
    
    args = parser.parse_args()
    
    # Create traffic generator
    generator = TrafficGenerator(targets=args.targets)
    
    print("="*60)
    print("Network Traffic Generator")
    print("="*60)
    print(f"Mode: {args.mode}")
    print(f"Targets: {', '.join(generator.targets)}")
    print("="*60)
    print("\nPress Ctrl+C to stop\n")
    
    # Start generation
    if args.mode == 'burst':
        generator.generate_burst_traffic(duration=args.duration)
    else:
        generator.start(mode=args.mode)


if __name__ == '__main__':
    main()

