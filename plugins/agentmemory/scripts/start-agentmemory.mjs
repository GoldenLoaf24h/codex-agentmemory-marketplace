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
 * 3. If not → spawns `npx -y @agentmemory/agentmemory` in background
 * 4. Polls until livez responds or timeout (30s)
 * 
 * Safe on upgrades: uses the official CLI via npx, same as manual start.
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
    console.log('[agentmemory] REST API already running');
    process.exit(0);
  }

  console.log('[agentmemory] Starting REST API (official CLI)...');

  const child = spawn('npx', ['-y', '@agentmemory/agentmemory'], {
    cwd: DATA_DIR,
    detached: true,
    stdio: 'ignore',
    windowsHide: true,
  });
  child.unref();  // Don't keep the event loop alive

  // Wait for it to be ready
  for (let i = 0; i < MAX_WAIT_SEC; i++) {
    await new Promise((r) => setTimeout(r, 1000));
    if (await probeLivez()) {
      console.log(`[agentmemory] Ready after ${i + 1}s`);
      process.exit(0);
    }
  }

  // Timeout — warn but don't block Codex startup
  console.error(`[agentmemory] WARNING: REST API did not start within ${MAX_WAIT_SEC}s`);
  console.error('[agentmemory] Run manually: npx -y @agentmemory/agentmemory');
  process.exit(1);
}

main();
