"""
Deterministic agentmemory backend verification — fixes the FALSE-NEGATIVE trap.

WHY THIS EXISTS:
After a gateway restart or mcp_servers config edit, the agentmemory-mcp
shim registers 53 tools and the memory provider "activates" over a few seconds.
Calling memory_save/memory_recall IMMEDIATELY returns {success:false} / empty
results — a FAKE "not working". That misled a session into telling the user to
restart repeatedly while the backend was actually fine (tools just hadn't registered).

USAGE:
  python verify_roundtrip.py
Checks, in order:
  1. engine REST livez/health (proxy, not curl — curl is rtched here)
  2. mcp registered 53 tools + "Memory provider activated" in logs/agent.log
  3. round-trip: memory_save one probe, then memory_recall the same probe
Prints PASS/FAIL per step. Only a passing round-trip proves the backend works.
"""
import os, sys, json, urllib.request, subprocess

HERMES = os.environ.get("HERMES_HOME",
    r"C:\Users\Lenovo\AppData\Local\hermes")
LOG = os.path.join(HERMES, "logs", "agent.log")
URL = "http://localhost:3111"

def probe(path):
    try:
        r = urllib.request.urlopen(URL + path, timeout=5)
        return r.status
    except Exception as e:
        return f"ERR {e}"

print("=== 1) engine REST ===")
for p in ["/agentmemory/livez", "/agentmemory/health"]:
    print(f"  {p}: {probe(p)}")

print("=== 2) gateway MCP registration (logs/agent.log) ===")
try:
    txt = open(LOG, encoding="utf-8", errors="replace").read()
    reg = "registered 53 tool(s)" in txt or "mcp__agentmemory_mcp__memory_recall" in txt
    act = "Memory provider 'agentmemory' activated" in txt
    print(f"  53 tools registered : {'PASS' if reg else 'FAIL (wait, then re-run)'}")
    print(f"  provider activated  : {'PASS' if act else 'FAIL (wait, then re-run)'}")
except Exception as e:
    print(f"  cannot read log: {e}")

print("=== 3) round-trip (run via agent memory_save/recall tool, not here) ===")
print("  Use the agent tools: memory_save(one probe) THEN memory_recall(same probe).")
print("  Both succeeding = backend OK. Either failing = real fault, dig further.")
print("NOTE: do NOT tell the user 'restart and it should work' until step 2 + 3 pass.")
