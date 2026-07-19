import subprocess
from pathlib import Path

ipwnder = Path("N:/ROMLOADDER/ipwndfu-win32/ipwnder.exe")
result = subprocess.run([str(ipwnder), "-p"], capture_output=True, text=True, cwd=str(ipwnder.parent))
print(result.stdout)
print(result.stderr)
print(f"Return code: {result.returncode}")
