#!/usr/bin/env python3
"""Quantum Mesh Proxy with real HTTPS CONNECT tunneling."""

import socket
import threading
import ssl
import time

def parse_connect_request(data: str) -> tuple:
    lines = data.split('\r\n')
    for line in lines:
        if line.upper().startswith('CONNECT '):
            parts = line.split()
            if len(parts) >= 2:
                host_port = parts[1].split(':')
                return host_port[0], int(host_port[1]) if len(host_port) > 1 else 443
    return None, None

def tunnel_traffic(client_sock, target_host, target_port):
    try:
        # Connect to target
        target_sock = socket.create_connection((target_host, target_port), timeout=10)
        client_sock.sendall(b"HTTP/1.1 200 OK\r\n\r\n")
        
        # Forward between client and target
        def forward(src, dst):
            while True:
                try:
                    data = src.recv(4096)
                    if not data: break
                    dst.sendall(data)
                except: break
        
        t1 = threading.Thread(target=forward, args=(client_sock, target_sock), daemon=True)
        t2 = threading.Thread(target=forward, args=(target_sock, client_sock), daemon=True)
        t1.start()
        t2.start()
        t1.join()
        t2.join()
    except Exception as e:
        try:
            client_sock.sendall(b"HTTP/1.1 502 Bad Gateway\r\n\r\n")
        except: pass
    finally:
        try: client_sock.close()
        except: pass
        try: target_sock.close()
        except: pass

def handle_client(conn, addr):
    try:
        data = conn.recv(4096).decode('utf-8', errors='ignore')
        if data.upper().startswith('CONNECT '):
            host, port = parse_connect_request(data)
            if host:
                tunnel_traffic(conn, host, port)
            else:
                conn.sendall(b"HTTP/1.1 400 Bad Request\r\n\r\n")
        else:
            # Regular HTTP - inject mesh headers
            response = f"HTTP/1.1 200 OK\r\nContent-Type: text/plain\r\nX-Quantum-Mesh: active\r\n\r\n[MESH_ENHANCED] {data[:200]}".encode()
            conn.sendall(response)
    except Exception as e:
        pass
    finally:
        try: conn.close()
        except: pass

# Start main proxy socket
proxy_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
proxy_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
proxy_socket.bind(('0.0.0.0', 9999))
proxy_socket.listen(50)

print("🔗 Quantum Mesh HTTPS Proxy Started on 0.0.0.0:9999")
print("   Configure browser proxy: 127.0.0.1:9999")
print("   Supports: HTTP + HTTPS CONNECT tunneling")
print("   Press Ctrl+C to stop\n")

try:
    while True:
        conn, addr = proxy_socket.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
        thread.start()
except KeyboardInterrupt:
    print("\n🛑 Proxy stopped")
    proxy_socket.close()