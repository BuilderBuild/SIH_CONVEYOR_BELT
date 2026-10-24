# Host ConveyX globally from this PC

ConveyX can continue running on this Windows PC with the RTX 5050, local SQLite/history, output files and attached camera. A Cloudflare Tunnel provides an external HTTPS URL and forwards requests to the existing loopback server at http://127.0.0.1:8502. The app is not moved to Render.

## Temporary protected demonstration

1. Install the current official Windows cloudflared client using the [Cloudflare download instructions](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/downloads/). Alternatively, place the official Windows executable at `tools/bin/cloudflared.exe` in this project.
2. Start ConveyX in PowerShell:

   ```powershell
   cd D:\Conveyor_dataset
   .\launch-gpu.ps1
   ```

3. In a second PowerShell terminal, supply the real email address that should be allowed to sign in:

   ```powershell
   cd D:\Conveyor_dataset
   .\share-local.ps1 -AllowedEmail 'you@example.com'
   ```

   Multiple approved viewers:

   ```powershell
   .\share-local.ps1 -AllowedEmail 'you@example.com','colleague@example.com'
   ```

4. Open the temporary HTTPS URL printed by cloudflared. The allowed visitor completes Cloudflare's email/PIN check before entering the shared ConveyX operator dashboard.
5. Keep both terminals running. Ctrl+C in the tunnel terminal ends public access; stopping ConveyX ends the application server.

When the assistant starts a tracked background tunnel, its process and logs are recorded in `outputs/tunnel/session.json`. End that tracked public tunnel with:

```powershell
.\stop-sharing.ps1
```

This verifies the executable, origin and process start time before stopping the recorded process. It does not stop ConveyX or another unrelated process.

The addresses above are placeholders. Cloudflare processes the addresses for access verification. The script checks that the installed client supports `--allowed-mail` and refuses to fall back to an unauthenticated public tunnel.

The app currently has shared inspection history, settings and access to this PC's camera. Only trusted operators should be admitted. The camera is attached to this PC; it is not a remote visitor's webcam. Keep the existing loopback binding and Streamlit request protections; router port forwarding is not required for this tunnel approach.

## Availability and limits

- This PC, ConveyX and the tunnel must stay running, with working internet. Sleep, shutdown or loss of connectivity makes the service unavailable.
- Processing uses this PC's GPU/CPU. Upload/download speed and concurrent workloads depend on the local connection and machine.
- Quick Tunnel addresses change on restart and have no uptime guarantee. Cloudflare documents a 200 in-flight request limit and no SSE support. The actual ConveyX WebSocket/upload/video flow still needs an external test after the tunnel is started.
- Provider upload/request limits may be lower than ConveyX's 200 MB application cap. Check large-video transfers separately.
- A URL has not been created merely by preparing these files. Public deployment is confirmed only after the tunnel starts and an external authenticated browser test succeeds.

## Stable address later

Use a managed Cloudflare Tunnel with an account, a suitable domain and a restrictive Access policy. A Windows service can keep the tunnel running, but it does not keep the PC awake or start ConveyX automatically unless startup is configured separately. No domain purchase, account creation, service installation or public tunnel has been performed by this guide.

References: [Quick Tunnels and email access](https://developers.cloudflare.com/tunnel/get-started/quick-tunnels/), [Cloudflare Tunnel](https://developers.cloudflare.com/cloudflare-one/networks/connectors/cloudflare-tunnel/).
