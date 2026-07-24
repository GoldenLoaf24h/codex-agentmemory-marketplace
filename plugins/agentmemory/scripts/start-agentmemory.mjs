#!/usr/bin/env node
/**
 * start-agentmemory.mjs
 *
 * Starts the agentmemory REST API in background if it's not already running.
 * Part of the Codex agentmemory plugin — no core files modified.
 *
 * How it works:
 * 1. Probes localhost:3111/agentmemory/livez
 * 2. If already responding → exit (fast path, ~200ms)
 * 3. If not → spawns `agentmemory` in background via shell (cmd.exe on Windows resolves the .cmd shim)
 * 4. Polls until livez responds or timeout (30s)
 *
 * Why shell: true instead of npx:
 * - npx on Windows is npx.cmd, which child_process.spawn without shell cannot reliably find
 * - npx caches the package separately from npm global install, risking version mismatch
 * - spawn('agentmemory', { shell: true }) works identically to typing in terminal
 */

import { spawn } from 'node:child_process';
import { createConnection } from 'node:net';

const PORT = 3111;
const HOST = '127.0.0.1';
const USER_HOME = process.env.USERPROFILE || process.env.HOME;
const DATA_DIR = `${USER_HOME}/.agentmemory`;
const MAX_WAIT_SEC = 30;

/**
 * Probe the REST API livez endpoint via raw TCP.
 * More reliable than HTTP fetch in pre-session context.
 */
async function probeLivez() {
  return new Promise((resolve) => {
    const socket = createConnection(PORT, HOST, () => {
      socket.write(
        `GET /agentmemory/livez HTTP/1.0\r\nHost: ${HOST}\r\nConnection: close\r\n\r\n`
      );
    });
    let data = '';
    socket.on('data', (chunk) => { data += chunk.toString(); });
    socket.on('close', () => {
      resolve(data.includes('200 OK') && data.includes('"status":"ok"'));
    });
    socket.on('error', () => resolve(false));
    socket.setTimeout(5000, () => { socket.destroy(); resolve(false); });
  });
}

async function main() {
  // Fast check — already running?
  if (await probeLivez()) {
    // backend already running, silent exit
    process.exit(0);
  }

  // starting backend silently

  // spawn with shell: true so cmd.exe resolves agentmemory(.cmd) from PATH,
  // matching what the user types in terminal. No npx, no npm prefix lookup.
  const child = spawn('agentmemory', [], {
    cwd: DATA_DIR,
    shell: true,
    detached: true,
    stdio: 'ignore',
    windowsHide: true,
  });
  child.unref();

  // Wait for it to be ready
  for (let i = 0; i < MAX_WAIT_SEC; i++) {
    await new Promise((r) => setTimeout(r, 1000));
    if (await probeLivez()) {
      // backend ready
      process.exit(0);
    }
  }

  // Timeout — warn but don't block Codex startup
  // WARNING: backend did not start in time
  // Run manually: agentmemory
  process.exit(1);
}

main();
