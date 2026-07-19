#!/usr/bin/env python3
"""Local TSS server that signs everything"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import plistlib

class TSSHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        print("[+] TSS Request received")
        
        # Parse request
        try:
            request = plistlib.loads(post_data)
            print(f"    ECID: {request.get('@APTicket', {}).get('ApECID', 'unknown')}")
            print(f"    Nonce: {request.get('@APTicket', {}).get('ApNonce', 'unknown')}")
        except:
            pass
        
        # Create fake successful response
        response = {
            'MESSAGE': 'SUCCESS',
            'REQUEST_STRING': post_data.decode('utf-8', errors='ignore'),
            'STATUS': 0
        }
        
        response_data = plistlib.dumps(response)
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/xml')
        self.send_header('Content-Length', len(response_data))
        self.end_headers()
        self.wfile.write(response_data)
        
        print("[+] Sent SUCCESS response")
    
    def log_message(self, format, *args):
        pass

print("[+] Starting local TSS server on 127.0.0.1:80")
print("[!] Run as Administrator (needs port 80)")
print("[!] Make sure hosts file has: 127.0.0.1 gs.apple.com")
print()

try:
    server = HTTPServer(('127.0.0.1', 80), TSSHandler)
    print("[+] Server running. Now restore with iTunes/3uTools")
    server.serve_forever()
except PermissionError:
    print("[-] Need Administrator privileges for port 80")
    print("[!] Run PowerShell as Admin")
except Exception as e:
    print(f"[-] Error: {e}")
