#!/usr/bin/env python3
"""IP-based hijacker for iTunes HTTPS connections"""
import socket
import threading
import sys
import time
import datetime
import ssl
from http.server import HTTPServer, BaseHTTPRequestHandler

# iTunes IP addresses we detected
ITUNES_IPS = [
    "104.26.10.184",
    "23.61.251.200"
]

log_file = "itunes_ip_requests.log"
with open(log_file, 'w') as f:
    f.write(f"iTunes IP Request Log - {datetime.datetime.now()}\n")
    f.write("=" * 50 + "\n\n")

def log_to_file(message):
    """Log message to both console and file"""
    print(message)
    with open(log_file, 'a') as f:
        f.write(f"{datetime.datetime.now().strftime('%H:%M:%S')} - {message}\n")

class HTTPSHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        """Handle iTunes HTTPS POST requests"""
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        log_to_file(f"\n[+] HTTPS POST REQUEST from iTunes")
        log_to_file(f"[+] Path: {self.path}")
        log_to_file(f"[+] Headers: {dict(self.headers)}")
        log_to_file(f"[+] Content Length: {content_length} bytes")
        
        # Save full post data to file
        with open(log_file, 'a') as f:
            f.write(f"FULL POST DATA:\n{post_data.decode('utf-8', errors='ignore')}\n")
            f.write("-" * 30 + "\n")
        
        # Create appropriate response
        if b'photo' in post_data.lower() or 'photo' in self.path.lower():
            log_to_file("[!] DETECTED: Photo sync request - bypassing")
            response = '''<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict><key>PhotoSyncDisabled</key><true/></dict></plist>'''
        elif b'tss' in post_data.lower() or 'tss' in self.path.lower():
            log_to_file("[!] DETECTED: TSS/SHSH request - sending fake blob")
            response = self.create_fake_shsh()
        else:
            log_to_file("[!] DETECTED: Unknown request - sending generic success")
            response = '''<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict><key>Status</key><string>SUCCESS</string></dict></plist>'''
        
        # Send response
        self.send_response(200)
        self.send_header('Content-Type', 'text/xml; charset=UTF-8')
        self.send_header('Content-Length', str(len(response)))
        self.send_header('Server', 'Apple')
        self.end_headers()
        self.wfile.write(response.encode())
        
        log_to_file(f"[✅] Sent {len(response)} byte response to iTunes\n")
    
    def do_GET(self):
        """Handle iTunes HTTPS GET requests"""
        log_to_file(f"\n[+] HTTPS GET REQUEST from iTunes")
        log_to_file(f"[+] Path: {self.path}")
        log_to_file(f"[+] Headers: {dict(self.headers)}")
        
        response = '''<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0"><dict><key>Status</key><string>OK</string></dict></plist>'''
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/xml; charset=UTF-8')
        self.send_header('Content-Length', str(len(response)))
        self.end_headers()
        self.wfile.write(response.encode())
        
        log_to_file(f"[✅] Sent GET response to iTunes\n")
    
    def create_fake_shsh(self):
        """Create fake SHSH blob"""
        return '''<?xml version="1.0" encoding="UTF-8"?>
<plist version="1.0">
<dict>
    <key>@APTicket</key>
    <data>ZmFrZV90aWNrZXRfZGF0YQ==</data>
    <key>@BBTicket</key>
    <data>ZmFrZV9iYXNlYmFuZF90aWNrZXQ=</data>
</dict>
</plist>'''
    
    def log_message(self, format, *args):
        pass

def setup_ip_hijack():
    """Add IP addresses to hosts file"""
    hosts_entries = []
    for ip in ITUNES_IPS:
        hosts_entries.append(f"127.0.0.1 {ip}")
    
    hosts_file = r"C:\Windows\System32\drivers\etc\hosts"
    
    try:
        with open(hosts_file, 'r') as f:
            existing = f.read()
        
        modified = existing
        for entry in hosts_entries:
            if entry not in existing:
                modified += f"\n{entry}"
        
        with open(hosts_file, 'w') as f:
            f.write(modified)
        
        log_to_file("[+] IP hijacking configured")
        log_to_file(f"[+] Redirected IPs: {ITUNES_IPS}")
        return True
        
    except PermissionError:
        log_to_file("[!] Cannot modify hosts file - run as Administrator")
        return False

def start_https_server():
    """Start HTTPS server on port 443"""
    try:
        server = HTTPServer(('127.0.0.1', 443), HTTPSHandler)
        
        # Create self-signed SSL context (iTunes might accept it)
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        
        # Use a simple self-signed cert (iTunes bypass)
        server.socket = context.wrap_socket(server.socket, server_side=True)
        
        log_to_file("[+] HTTPS Hijacker started on 127.0.0.1:443")
        log_to_file("[+] iTunes HTTPS requests will be intercepted")
        log_to_file("[+] Press Ctrl+C to stop")
        server.serve_forever()
        
    except Exception as e:
        log_to_file(f"[!] HTTPS server failed: {e}")
        log_to_file("[!] Try running as Administrator")

def main():
    log_to_file("[+] iTunes IP Hijacker")
    log_to_file("[+] This will intercept iTunes direct IP connections")
    
    if not setup_ip_hijack():
        return
    
    log_to_file("[+] Starting HTTPS server...")
    start_https_server()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        log_to_file("\n[+] IP Hijacker stopped")
        sys.exit(0)