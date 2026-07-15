# VPS Access Guide

**Status:** Current authority. Covers SSH, SCP, and graphical desktop access to the Ivy VPS.

## SSH access

The VPS is reachable via the `ih-market-vps` SSH alias defined in `~/.ssh/config`:

```text
Host ih-market-vps
    HostName <VPS_PUBLIC_IP>
    User scraper
    IdentityFile ~/.ssh/ih_market_vps
    Port 22
```

**Read-only inspection:**
```bash
ssh ih-market-vps "<command>"
```

**Interactive session:**
```bash
ssh ih-market-vps
```

Connection details (private runbook): `_internal/vps-inventory-and-runbook.md`

Do not store private keys, passwords, or sensitive SSH configuration in this repository.

## SCP / file transfer

**Send a file from Mac to VPS:**
```bash
scp ./my-file.md ih-market-vps:/home/scraper/Desktop/hermes-bridge/inbox/
```

**Retrieve a file from VPS to Mac:**
```bash
scp ih-market-vps:/home/scraper/Desktop/hermes-bridge/outbox/<response>.md .
```

The bridge at `/home/scraper/Desktop/hermes-bridge/` is the preferred transfer target for operational communication. See `docs/HERMES_OPERATOR_GUIDE.md` for the bridge protocol.

Do not transfer credentials, `.env` files, or private data through SCP into tracked locations.

## Graphical desktop access (Screen Sharing)

The VPS runs an XFCE desktop environment accessible via:

- **XRDP** (port 3389) — use Microsoft Remote Desktop or any RDP client.
- **VNC** (port 5900, loopback) — x11vnc on localhost.

**Current recommended path:** macOS Screen Sharing → VNC or RDP client to `ih-market-vps:3389` (resolved via SSH config's `HostName`).

The desktop is required for:
- Launching Hermes Desktop (requires a graphical X11 session).
- Chrome-based browser workloads (Tampermonkey userscripts, market snapshots).

### Display number caveat

Hermes Desktop is launched with `DISPLAY=:10.0`. This display number is specific to the XRDP session. It may change on reconnection or reboot. Verify the active display before launching:

```bash
echo $DISPLAY
```

### Clipboard limitation

VNC clipboard transfer between the VPS desktop and macOS is **unreliable**. Do not depend on copy-paste for transferring command output, credentials, or file contents. Use the bridge/outbox for durable file transfer:

```bash
# On VPS: write output to bridge outbox
echo "result" > ~/Desktop/hermes-bridge/outbox/report.md

# On Mac: retrieve via SCP
scp ih-market-vps:/home/scraper/Desktop/hermes-bridge/outbox/report.md .
```

## Distinction between access methods

| Method | Purpose | When to use |
|--------|---------|-------------|
| SSH | Command-line inspection, file transfer, automation | Default for all non-graphical work |
| SCP | File transfer to/from bridge | Operational communication, evidence retrieval |
| Screen Sharing / RDP | Graphical desktop | Hermes Desktop, Chrome browser workloads, initial setup |
