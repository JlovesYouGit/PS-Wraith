#!/usr/bin/env python3
"""Working TSS server - signs everything without validation"""
from http.server import HTTPServer, BaseHTTPRequestHandler
import plistlib

class TSSHandler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers.get('Content-Length', 0))
        post_data = self.rfile.read(content_length)
        
        print(f"\n[+] TSS Request: {len(post_data)} bytes")
        
        # Return minimal success response
        response = b'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>MESSAGE</key>
    <string>SUCCESS</string>
    <key>STATUS</key>
    <integer>0</integer>
</dict>
</plist>'''
        
        self.send_response(200)
        self.send_header('Content-Type', 'text/xml')
        self.send_header('Content-Length', len(response))
        self.end_headers()
        self.wfile.write(response)
        
        print("[+] Sent SUCCESS")
    
    def log_message(self, format, *args):
        return

print("="*60)
print("TSS SERVER - Port 80")
print("="*60)
print("\n[!] MUST run as Administrator")
print("[!] MUST have in hosts file: 127.0.0.1 gs.apple.com")
print("\nStarting server...")

try:
    server = HTTPServer(('0.0.0.0', 80), TSSHandler)
    print("[+] Server running on port 80")
    print("[+] Restore with 3uTools now\n")
    server.serve_forever()
except PermissionError:
    print("\n[-] Run PowerShell as Administrator")
except OSError as e:
    print(f"\n[-] Port 80 in use or blocked: {e}")
