# ConveyX PC-hosted public access

Configured 24 October 2026. The application continues to run on this PC at http://127.0.0.1:8502, using its existing GPU environment and local storage. No Render service was created.

## Current status

- Official project-local cloudflared 2026.10.3 installed at tools/bin/cloudflared.exe; SHA256 matched Cloudflare's published GitHub release checksum.
- A temporary HTTPS Quick Tunnel is connected. Its current address and process/log details are recorded in outputs/tunnel/session.json.
- The tunnel is configured with the single user-approved allowed email address. No unauthenticated tunnel fallback was used.
- External unauthenticated requests to `/`, `/_stcore/health` and `/_stcore/stream` all return HTTP 302 to Cloudflare sign-in, without exposing the application. Raw checks are in outputs/reports/public_tunnel_verification.json.
- Cloudflare's email/PIN page was opened. The correct approved address was verified in the form and the provider confirmed a code request for it. An earlier incorrect duplicated form address was corrected; no application access was granted by that request.
- **Authenticated external application, WebSocket, upload and download testing is pending the user's PIN sign-in.** Local application tests remain separate evidence and do not replace this external test.

## Start and stop

For future foreground sharing, first run launch-gpu.ps1, then share-local.ps1 with the chosen allowed email address. The tunnel client prints a new temporary URL each time.

To stop the currently tracked background tunnel, run:

```powershell
cd D:\Conveyor_dataset
.\stop-sharing.ps1
```

This checks the executable path, origin and start time before stopping the recorded process. ConveyX remains available locally after public sharing stops.

## Limits

The PC must stay awake with working internet, ConveyX and cloudflared. The temporary hostname expires when the tunnel stops and changes on restart. Stable domain hosting, automatic application/tunnel startup and a managed Cloudflare Access deployment are not configured. Details and official references: PC_HOSTING.md.
