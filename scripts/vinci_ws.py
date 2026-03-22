"""
Minimal OBS WebSocket v5 client for VinciFlow vendor requests.
No external dependencies — uses only Python stdlib.
"""

import asyncio
import hashlib
import base64
import json
import uuid
import struct

# ─── Configuration ──────────────────────────────────────────────────
# Auto-detect: if running in WSL, use the Windows host IP; otherwise localhost
import platform
import subprocess

def _detect_host():
    """Detect OBS WebSocket host. WSL needs Windows host IP, native uses localhost."""
    if "microsoft" in platform.release().lower() or "wsl" in platform.release().lower():
        # Try default gateway first (most reliable for WSL2)
        try:
            result = subprocess.run(
                ["ip", "route", "show", "default"],
                capture_output=True, text=True, timeout=2
            )
            for line in result.stdout.splitlines():
                parts = line.split()
                if "via" in parts:
                    return parts[parts.index("via") + 1]
        except Exception:
            pass
        # Fallback to nameserver
        try:
            result = subprocess.run(
                ["cat", "/etc/resolv.conf"],
                capture_output=True, text=True, timeout=2
            )
            for line in result.stdout.splitlines():
                if "nameserver" in line:
                    return line.split()[1]
        except Exception:
            pass
    return "127.0.0.1"

OBS_HOST = _detect_host()
OBS_PORT = 4455
OBS_PASSWORD = ""  # Set if you have WebSocket auth enabled


async def _ws_connect(host, port):
    """Raw WebSocket handshake over TCP (no external libs)."""
    import random
    reader, writer = await asyncio.open_connection(host, port)

    key = base64.b64encode(random.randbytes(16)).decode()
    handshake = (
        f"GET / HTTP/1.1\r\n"
        f"Host: {host}:{port}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
        f"\r\n"
    )
    writer.write(handshake.encode())
    await writer.drain()

    response = b""
    while b"\r\n\r\n" not in response:
        response += await reader.read(4096)

    if b"101" not in response:
        raise ConnectionError(f"WebSocket handshake failed: {response[:200]}")

    return reader, writer


def _ws_encode_frame(data: bytes) -> bytes:
    """Encode a WebSocket text frame with masking."""
    import os
    frame = bytearray()
    frame.append(0x81)  # FIN + text opcode

    length = len(data)
    if length < 126:
        frame.append(0x80 | length)
    elif length < 65536:
        frame.append(0x80 | 126)
        frame.extend(struct.pack(">H", length))
    else:
        frame.append(0x80 | 127)
        frame.extend(struct.pack(">Q", length))

    mask = os.urandom(4)
    frame.extend(mask)
    frame.extend(bytes(b ^ mask[i % 4] for i, b in enumerate(data)))
    return bytes(frame)


async def _ws_read_frame(reader) -> str:
    """Read a single WebSocket text frame."""
    header = await reader.readexactly(2)
    length = header[1] & 0x7F

    if length == 126:
        length = struct.unpack(">H", await reader.readexactly(2))[0]
    elif length == 127:
        length = struct.unpack(">Q", await reader.readexactly(8))[0]

    masked = header[1] & 0x80
    if masked:
        mask = await reader.readexactly(4)
        data = await reader.readexactly(length)
        data = bytes(b ^ mask[i % 4] for i, b in enumerate(data))
    else:
        data = await reader.readexactly(length)

    return data.decode("utf-8")


def _compute_auth(password, salt, challenge):
    """obs-websocket v5 auth: Base64(SHA256(Base64(SHA256(password+salt)) + challenge))"""
    secret = base64.b64encode(
        hashlib.sha256((password + salt).encode()).digest()
    ).decode()
    auth = base64.b64encode(
        hashlib.sha256((secret + challenge).encode()).digest()
    ).decode()
    return auth


async def _send_json(writer, obj):
    data = json.dumps(obj).encode("utf-8")
    writer.write(_ws_encode_frame(data))
    await writer.drain()


async def _recv_json(reader):
    raw = await _ws_read_frame(reader)
    return json.loads(raw)


async def vinci_request(request_type, request_data=None):
    """Send a VinciFlow vendor request and return the response."""
    reader, writer = await _ws_connect(OBS_HOST, OBS_PORT)

    try:
        # 1. Receive Hello (op: 0)
        hello = await _recv_json(reader)
        assert hello["op"] == 0, f"Expected Hello, got op={hello['op']}"

        # 2. Build Identify (op: 1)
        identify = {"op": 1, "d": {"rpcVersion": 1}}

        auth_data = hello["d"].get("authentication")
        if auth_data and OBS_PASSWORD:
            identify["d"]["authentication"] = _compute_auth(
                OBS_PASSWORD, auth_data["salt"], auth_data["challenge"]
            )

        await _send_json(writer, identify)

        # 3. Receive Identified (op: 2)
        identified = await _recv_json(reader)
        if identified["op"] != 2:
            raise ConnectionError(f"Auth failed: {identified}")

        # 4. Send CallVendorRequest (op: 6)
        req_id = str(uuid.uuid4())
        request = {
            "op": 6,
            "d": {
                "requestType": "CallVendorRequest",
                "requestId": req_id,
                "requestData": {
                    "vendorName": "vinci-flow",
                    "requestType": request_type,
                    "requestData": request_data or {},
                },
            },
        }
        await _send_json(writer, request)

        # 5. Read responses until we get ours (skip events)
        for _ in range(20):
            resp = await _recv_json(reader)
            if resp.get("op") == 7 and resp.get("d", {}).get("requestId") == req_id:
                return resp["d"].get("responseData", {}).get("responseData", {})

        return None

    finally:
        writer.close()
        try:
            await writer.wait_closed()
        except Exception:
            pass


def run(request_type, request_data=None):
    """Synchronous wrapper."""
    return asyncio.run(vinci_request(request_type, request_data))
