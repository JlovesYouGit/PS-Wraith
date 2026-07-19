#!/usr/bin/env python3
"""Check what servers iTunes is actually trying to contact"""
import subprocess
import sys
import time

def monitor_itunes_traffic():
    """Monitor network traffic to see what iTunes is doing"""
    print("[+] Monitoring iTunes network traffic...")
    print("[+] Start iTunes restore now and watch for connections")
    print("[+] Press Ctrl+C to stop monitoring")
    
    try:
        # Use netstat to monitor connections
        while True:
            result = subprocess.run(['netstat', '-an'], capture_output=True, text=True)
            lines = result.stdout.split('\n')
            
            itunes_connections = []
            for line in lines:
                if 'ESTABLISHED' in line and ('80' in line or '443' in line):
                    # Look for connections to Apple servers
                    if any(x in line for x in ['17.', '23.', '104.']):  # Apple IP ranges
                        itunes_connections.append(line.strip())
            
            if itunes_connections:
                print(f"\n[+] iTunes connections detected:")
                for conn in itunes_connections:
                    print(f"  {conn}")
            
            time.sleep(2)
            
    except KeyboardInterrupt:
        print("\n[+] Monitoring stopped")

if __name__ == "__main__":
    monitor_itunes_traffic()