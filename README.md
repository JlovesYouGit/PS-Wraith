Here’s how the PS4 deployment flow works and what you need to do to get it operational.

**System overview**
- The Mac acts as the host. It runs an endpoint server that serves the GoldHEN payload and kernel patch data.
- The PS4 reaches that server over the local network and downloads `goldhen.bin`.
- After download, the PS4 needs an active listener/exploit context to actually execute the payload; otherwise it remains a downloaded file only.
- SeedGate/Vemex provide device discovery and MAC/IP routing metadata, but the actual execution still depends on what’s running on the PS4
