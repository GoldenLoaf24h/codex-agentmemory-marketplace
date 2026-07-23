#!/usr/bin/env python3
"""Deterministic agentmemory health probe.

Usage:  python probe_agentmemory.py
Run from anywhere. Bypasses `curl` (wrapped by rtk hook on this box) and
reports the exact failure signature so you know whether the backend is
(a) down, (b) up-but-no-routes (the Windows iii-exec bug), or (c) healthy.

Exit code 0 = healthy, 1 = broken.
"""
import json
import socket
import subprocess
import sys
import urllib.request

BASE = "http://127.0.0.1:3111"
WS_PORT = 49134


def port_open(port, host="127.0.0.1", timeout=2):
    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect((host, port))
        return True
    except Exception:
        return False
    finally:
        s.close()


def get(path):
    try:
        r = urllib.request.urlopen(BASE + path, timeout=8)
        return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return "ERR", repr(e)


def call(method, path, body=None):
    data = json.dumps(body).encode() if body is not None else None
    req = urllib.request.Request(
        BASE + path, data=data, method=method,
        headers={"content-type": "application/json"},
    )
    try:
        r = urllib.request.urlopen(req, timeout=8)
        return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        return "ERR", repr(e)


def worker_running():
    """True if a node.exe process has 'index.mjs' in its command line."""
    try:
        out = subprocess.run(
            ['powershell', '-NoProfile', '-Command',
             "Get-CimInstance Win32_Process | Where-Object { $_.Name -eq 'node.exe' "
             "-and $_.CommandLine -like '*index.mjs*' } | Select-Object ProcessId"],
            capture_output=True, text=True, timeout=20,
        ).stdout
        return "ProcessId" in out and "---" not in out.strip().split("ProcessId")[-1]
    except Exception:
        return None  # unknown


def main():
    print("=== agentmemory probe ===")
    http_up = port_open(3111)
    ws_up = port_open(WS_PORT)
    print(f"port 3111 (REST): {'OPEN' if http_up else 'CLOSED'}")
    print(f"port {WS_PORT} (engine WS): {'OPEN' if ws_up else 'CLOSED'}")

    if not http_up:
        print("RESULT: BACKEND DOWN — engine not listening. Start/restart it.")
        return 1

    livez = get("/agentmemory/livez")
    health = get("/agentmemory/health")
    print(f"GET /agentmemory/livez -> {livez[0]}")
    print(f"GET /agentmemory/health -> {health[0]}")

    if livez[0] == 200:
        # route-registering worker is alive — do a write/read round-trip
        remember = call("POST", "/agentmemory/remember",
                        {"content": "PROBE_healthcheck", "type": "fact"})
        ok = remember[0] == 201
        mid = None
        if ok:
            try:
                mid = json.loads(remember[1])["memory"]["id"]
                search = call("POST", "/agentmemory/search",
                              {"query": "PROBE_healthcheck"})
                ok = ok and "PROBE_healthcheck" in search[1]
            finally:
                if mid:
                    call("DELETE", "/agentmemory/governance/memories",
                         {"memoryIds": [mid], "reason": "probe cleanup"})
        wr = worker_running()
        print(f"POST /agentmemory/remember -> {remember[0]} "
              f"({'write/read OK' if ok else 'WRITE FAILED'})")
        print(f"worker process (node ... index.mjs): {wr}")
        if ok:
            print("RESULT: HEALTHY ✅")
            return 0
        print("RESULT: ROUTES UP BUT WRITE FAILED — check engine logs.")
        return 1

    # http up but livez not 200 => classic Windows iii-exec bug
    print("RESULT: UP-BUT-NO-ROUTES (404 on /agentmemory/*) — "
          "iii-exec worker never started. Apply the Windows fix:")
    print("  1) patch iii-config.yaml iii-exec: watch dist/**/*.mjs, "
          "exec <abs node> <abs pkg>/dist/index.mjs")
    print("  2) start worker with III_ENGINE_URL=ws://127.0.0.1:49134")
    return 1


if __name__ == "__main__":
    sys.exit(main())
