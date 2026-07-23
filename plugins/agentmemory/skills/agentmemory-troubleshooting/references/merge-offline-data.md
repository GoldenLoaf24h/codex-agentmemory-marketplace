# Merging an orphaned / offline AgentMemory data copy into the live instance

Condensed from the 2026-07-11 session. This is a **deliberate consolidation of two
separate datasets**, NOT a repair — keep it distinct from the "never touch
state_store.db during repair" rule.

## When this applies
You find a SECOND `state_store.db` / `stream_store` (iii `mem:*.bin` files) outside
`~/.agentmemory/data/` — e.g. `D:\workspace\Hermes\data/`. Before anything, confirm
it is NOT a duplicate of the live copy:
- Compare `mtime` + size: orphan was **newer (2026-07-10) and larger (6.8 MB)** vs
  live (2026-06-20, 400 KB) → a SEPARATE live dataset, not a backup.
- Confirm which is live: `iii.exe` is launched with `--config <abs>.yaml` whose
  `iii-state`/`iii-stream` blocks use RELATIVE `./data/state_store.db`; that resolves
  against iii.exe's own dir (`C:\Users\Lenovo\.agentmemory\bin`) → live =
  `C:\Users\Lenovo\.agentmemory\data`. Get live PID via
  `netstat -ano | grep :3111 | grep LISTENING`, then
  `powershell "(Get-CimInstance Win32_Process -Filter 'ProcessId=<pid>').CommandLine"`.

## Recipe (Windows, verified)
```python
import os, shutil, datetime, subprocess

LIVE = r"C:\Users\Lenovo\.agentmemory\data"
ORPHAN = r"D:\workspace\Hermes\data"
BAK = r"C:\Users\Lenovo\agentmemory-backup"   # AGENTMEMORY_EXPORT_ROOT default

# 1) back up BOTH (timestamped)
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
shutil.copytree(LIVE, os.path.join(BAK, f"live-before-merge-{ts}"))
shutil.copytree(ORPHAN, os.path.join(BAK, f"orphan-{ts}"))

# 2) stop live instance (correct Windows syntax — NOT //PID)
#    taskkill /PID <pid> /F   ; then confirm 3111 released

# 3) merge: orphan is superset+newer -> copy ALL .bin over live (overwrite+add)
for sub in ("state_store.db", "stream_store"):
    src = os.path.join(ORPHAN, sub); dst = os.path.join(LIVE, sub)
    for f in os.listdir(src):
        shutil.copy2(os.path.join(src, f), os.path.join(dst, f))

# 4) restart live in BACKGROUND (never & in foreground):
#    npx -y @agentmemory/agentmemory start
#    wait ~30s (SiliconFlow Qwen3-8B cold start; REST empty first 10-20s)
```

## Verify
- `netstat -ano | grep :3111` → LISTENING.
- `curl -s http://localhost:3111/agentmemory/health` → real JSON (not empty).
- `memory_save` one item → `memory_recall` same → hit.
- `memory_recall` a PRE-MERGE historical memory (from the orphan's date range) →
  must return it. This proves the orphan's data is now live.

## Pitfalls
- Use Python `shutil` for copy/rm — MSYS `cp`/`rm -rf` are unreliable on this box
  (empty clones, "already exists and not empty" false errors).
- `taskkill /PID` (single slash) — `//PID` is a POSIX habit Windows rejects.
- After merge, the orphan dir can be deleted ONLY after confirming a successful
  round-trip AND a backup exists (user rule: keep backup until verified).
