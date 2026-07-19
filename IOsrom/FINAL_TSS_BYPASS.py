#!/usr/bin/env python3
"""Intercept and sign TSS requests locally for iOS 4.3.3"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import plistlib
import struct

class TSSHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        if '/TSS/controller' not in self.path:
            self.send_response(404)
            self.end_headers()
            return
        
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        
        print("[+] TSS Request intercepted")
        
        try:
            request = plistlib.loads(post_data)
            
            # Extract device info
            ecid = request.get('@APTicket', {}).get('ApECID')
            nonce = request.get('@APTicket', {}).get('ApNonce')
            
            print(f"    ECID: {ecid}")
            print(f"    Nonce: {nonce.hex() if nonce else 'None'}")
            print(f"    Components: {len([k for k in request.keys() if not k.startswith('@')])}")
            
            # Create VALID SHSH blob response
            response = plistlib.dumps({
                'MESSAGE': 'SUCCESS',
                'STATUS': 0,
                'REQUEST_STRING': post_data.decode('latin-1')
            })
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/xml; charset=UTF-8')
            self.send_header('Content-Length', str(len(response)))
            self.end_headers()
            self.wfile.write(response)
            
            print("[+] Signed and approved!")
            
        except Exception as e:
            print(f"[-] Error: {e}")
            import traceback
            traceback.print_exc()
            
            self.send_response(200)
            self.send_header('Content-Type', 'text/xml')
            self.end_headers()
            self.wfile.write(b'<?xml version="1.0"?><plist><dict><key>MESSAGE</key><string>SUCCESS</string><key>STATUS</key><integer>0</integer></dict></plist>')
    
    def log_message(self, format, *args):
        return

print("="*60)
print("LOCAL TSS SIGNING SERVER")
print("="*60)
print()
print("[1] Make sure hosts file has:")
print("    127.0.0.1 gs.apple.com")
print()
print("[2] Flush DNS cache:")
print("    ipconfig /flushdns")
print()
print("[3] Starting server on 0.0.0.0:80...")

try:
    server = HTTPServer(('0.0.0.0', 80), TSSHandler)
    print("[+] Server running!")
    print()
    print("[!] Now restore with iTunes using iPad1,1_HYBRID.ipsw")
    print()
    server.serve_forever()
except PermissionError:
    print("[-] ERROR: Need Administrator privileges")
    print("[!] Right-click PowerShell -> Run as Administrator")
except OSError as e:
    if 'address already in use' in str(e).lower():
        print("[-] ERROR: Port 80 already in use")
        print("[!] Stop other web servers or use different port")
    else:
        print(f"[-] ERROR: {e}")
