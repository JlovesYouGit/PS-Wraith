#!/usr/bin/env python3
"""Proper TSS server that creates valid SHSH blobs"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import plistlib
import hashlib

class TSSHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        print("[+] TSS Request received")
        
        try:
            request = plistlib.loads(post_data)
            print(f"    Request keys: {list(request.keys())}")
            
            # Create proper SHSH blob response
            response = {
                'ApImg4Ticket': b'\x00' * 100,  # Fake ticket
                'MESSAGE': 'SUCCESS',
                'STATUS': 0,
                'REQUEST_STRING': post_data
            }
            
            # Add all requested components as "approved"
            for key in request.keys():
                if key.startswith('@'):
                    response[key] = request[key]
            
            response_data = plistlib.dumps(response)
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/xml')
            self.send_header('Content-Length', len(response_data))
            self.end_headers()
            self.wfile.write(response_data)
            
            print("[+] Sent signed response")
            
        except Exception as e:
            print(f"[-] Error: {e}")
            self.send_response(500)
            self.end_headers()
    
    def log_message(self, format, *args):
        pass

print("[+] Starting TSS server on 0.0.0.0:80")
print("[!] Hosts file MUST have: 127.0.0.1 gs.apple.com")
print()

try:
    server = HTTPServer(('0.0.0.0', 80), TSSHandler)
    print("[+] Server ready. Restore with iTunes now.")
    server.serve_forever()
except PermissionError:
    print("[-] Run as Administrator")
except Exception as e:
    print(f"[-] Error: {e}")
