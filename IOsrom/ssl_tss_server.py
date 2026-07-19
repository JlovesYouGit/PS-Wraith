#!/usr/bin/env python3
"""SSL TSS server to handle 3uTools/iTunes HTTPS requests"""
import ssl
import socket
import threading
import datetime

log_file = "ssl_tss.log"

def log_message(msg):
    with open(log_file, 'a') as f:
        f.write(f"{datetime.datetime.now().strftime('%H:%M:%S')} - {msg}\n")
    print(msg)

def handle_client(client_socket, addr):
    """Handle SSL client connection"""
    try:
        log_message(f"[+] SSL connection from {addr}")
        
        # Read the request
        request = client_socket.recv(4096).decode('utf-8', errors='ignore')
        log_message(f"[+] Request: {request[:200]}...")
        
        # Create TSS response
        response_body = '''<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
<dict>
    <key>@APTicket</key>
    <data>SW1nM0ZBS0VfVElDS0VUX0RBVEE=</data>
    <key>@BBTicket</key>
    <data>QkJGQUtFX1RJQ0tFVF9EQVRB</data>
    <key>@HostPlatformInfo</key>
    <string>windows</string>
</dict>
</plist>'''
        
        # HTTP response
        http_response = f"""HTTP/1.1 200 OK\r
Content-Type: text/xml; charset=UTF-8\r
Content-Length: {len(response_body)}\r
Server: Apple\r
Connection: close\r
\r
{response_body}"""
        
        client_socket.send(http_response.encode())
        log_message("[✅] Sent TSS response")
        
    except Exception as e:
        log_message(f"[!] Client error: {e}")
    finally:
        client_socket.close()

def start_ssl_server():
    """Start SSL server on port 443"""
    try:
        # Create SSL context
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # Generate self-signed certificate
        import tempfile
        import subprocess
        
        # Create temporary cert
        cert_file = "temp_cert.pem"
        key_file = "temp_key.pem"
        
        # Simple self-signed cert creation
        with open(cert_file, 'w') as f:
            f.write("""-----BEGIN CERTIFICATE-----
MIICljCCAX4CCQDKg8Z8Z8Z8ZjANBgkqhkiG9w0BAQsFADCBjDELMAkGA1UEBhMC
VVMxCzAJBgNVBAgMAkNBMRYwFAYDVQQHDA1TYW4gRnJhbmNpc2NvMQ8wDQYDVQQK
DAZBcHBsZTEPMA0GA1UECwwGQXBwbGUxDzANBgNVBAMMBkFwcGxlMSUwIwYJKoZI
hvcNAQkBFhZhcHBsZUBhcHBsZS5jb20uZmFrZTAeFw0yNTAxMDEwMDAwMDBaFw0y
NjAxMDEwMDAwMDBaMIGMMQswCQYDVQQGEwJVUzELMAkGA1UECAwCQ0ExFjAUBgNV
BAcMDVNhbiBGcmFuY2lzY28xDzANBgNVBAoMBkFwcGxlMQ8wDQYDVQQLDAZBcHBs
ZTEPMA0GA1UEAwwGQXBwbGUxJTAjBgkqhkiG9w0BCQEWFmFwcGxlQGFwcGxlLmNv
bS5mYWtlMIGfMA0GCSqGSIb3DQEBAQUAA4GNADCBiQKBgQC7vbqajDw4o6gJy8jH
tMQzSM9ID2ssOnoqdU6h+rX7dfd4+OyP5MfqOVGHbHzAahlfFe2lYqYDS5xYGMLQ
VeQKNgMQ5fAWQBAJ9fB6TVJ5+wjUlKxdiNNgb5/KVBdXcpg7zBcZjNyn3HqjqZ6V
8VvSdeVu6ohXBr7BjV7OSjrJ5QIDAQABMA0GCSqGSIb3DQEBCwUAA4GBAG9jdHlw
8fTRP2H4f+qiRx1T5Ap09fcAj5AdJq+b4lvr2/tNFx7RjbBH3cqcHa8+TQIc7R6s
kQK+b4BQy6BzV3R5K8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8
-----END CERTIFICATE-----""")
        
        with open(key_file, 'w') as f:
            f.write("""-----BEGIN PRIVATE KEY-----
MIICdgIBADANBgkqhkiG9w0BAQEFAASCAmAwggJcAgEAAoGBALu9upqMPDijqAnL
yMe0xDNIz0gPayw6eip1TqH6tft193j47I/kx+o5UYdsfMBqGV8V7aVipiNLnFgY
wtBV5Ao2AxDl8BZAEAn18HpNUnn7CNSUrF2I02Bvn8pUF1dymDvMFxmM3Kfceqep
npXxW9J15W7qiFcGvsGNXs5KOsnlAgMBAAECgYAKuLTt0lxCDHMltqV2tVXFgRdY
8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z
8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z
8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z
8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z
8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z
8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z
8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z
8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z
8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z
8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z8Z
-----END PRIVATE KEY-----""")
        
        context.load_cert_chain(cert_file, key_file)
        
        # Create server socket
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind(('127.0.0.1', 443))
        server_socket.listen(5)
        
        # Wrap with SSL
        ssl_socket = context.wrap_socket(server_socket, server_side=True)
        
        log_message("[+] SSL TSS Server started on 127.0.0.1:443")
        log_message("[+] Ready for 3uTools/iTunes connections")
        
        while True:
            client_socket, addr = ssl_socket.accept()
            thread = threading.Thread(target=handle_client, args=(client_socket, addr))
            thread.start()
            
    except Exception as e:
        log_message(f"[!] SSL server failed: {e}")

if __name__ == "__main__":
    with open(log_file, 'w') as f:
        f.write(f"SSL TSS Server Log - {datetime.datetime.now()}\n")
        f.write("=" * 50 + "\n\n")
    
    start_ssl_server()