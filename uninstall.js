#!/usr/bin/env node
const fs = require("fs");
const path = require("path");
const os = require("os");

const PULSE_DIR = path.join(os.homedir(), ".pulse");
const CLAUDE_SETTINGS = path.join(os.homedir(), ".claude", "settings.json");

const ANSI = { green: "\x1b[92m", yellow: "\x1b[93m", reset: "\x1b[0m" };
function ok(msg) { console.log(`  ${ANSI.green}✓${ANSI.reset} ${msg}`); }

// Remove Pulse hooks from settings.json
function removeHooks() {
  if (!fs.existsSync(CLAUDE_SETTINGS)) return;
  let settings;
  try { settings = JSON.parse(fs.readFileSync(CLAUDE_SETTINGS, "utf8")); }
  catch { return; }

  if (!settings.hooks) return;

  for (const key of Object.keys(settings.hooks)) {
    settings.hooks[key] = settings.hooks[key].filter(
      (h) => !(h.hooks && h.hooks.some((hh) => hh.command && hh.command.includes("pulse")))
    );
    if (settings.hooks[key].length === 0) delete settings.hooks[key];
  }

  fs.writeFileSync(CLAUDE_SETTINGS, JSON.stringify(settings, null, 2));
  ok("Removed hooks from ~/.claude/settings.json");
}

function removeFiles() {
  if (fs.existsSync(PULSE_DIR)) {
    fs.rmSync(PULSE_DIR, { recursive: true, force: true });
    ok(`Removed ${PULSE_DIR}`);
  }
}

console.log("\n  💓 Pulse uninstaller\n");
removeHooks();
removeFiles();
console.log("\n  Pulse has been removed. Goodbye 👋\n");
