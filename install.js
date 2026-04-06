#!/usr/bin/env node
/**
 * Pulse installer — npx pulse-dev install
 * Injects hooks into ~/.claude/settings.json and copies Python files to ~/.pulse/
 */
const fs = require("fs");
const path = require("path");
const { execSync, spawnSync } = require("child_process");
const os = require("os");

const PULSE_DIR = path.join(os.homedir(), ".pulse");
const CLAUDE_SETTINGS = path.join(os.homedir(), ".claude", "settings.json");
const SRC_DIR = path.join(__dirname, "pulse");

const ANSI = {
  green: "\x1b[92m",
  blue: "\x1b[94m",
  yellow: "\x1b[93m",
  reset: "\x1b[0m",
  bold: "\x1b[1m",
};

function ok(msg) { console.log(`  ${ANSI.green}✓${ANSI.reset} ${msg}`); }
function info(msg) { console.log(`  ${ANSI.blue}→${ANSI.reset} ${msg}`); }
function warn(msg) { console.log(`  ${ANSI.yellow}!${ANSI.reset} ${msg}`); }

// Check Python 3
function checkPython() {
  const r = spawnSync("python3", ["--version"], { encoding: "utf8" });
  if (r.status !== 0) {
    console.error("  ✗ python3 not found. Please install Python 3.8+");
    process.exit(1);
  }
  ok(`${r.stdout.trim()} found`);
}

// Copy pulse/ directory to ~/.pulse/
function copyFiles() {
  fs.mkdirSync(PULSE_DIR, { recursive: true });
  fs.mkdirSync(path.join(PULSE_DIR, "hooks"), { recursive: true });

  const files = [
    "db.py", "creature.py", "generate.py", "run.py",
    "hooks/on-stop.sh", "hooks/on-agent-stop.sh",
    "hooks/on-session-start.sh", "hooks/on-prompt.sh",
  ];

  for (const f of files) {
    const src = path.join(SRC_DIR, f);
    const dst = path.join(PULSE_DIR, f);
    fs.copyFileSync(src, dst);
    if (f.endsWith(".sh")) fs.chmodSync(dst, 0o755);
  }
  ok(`Copied files to ${PULSE_DIR}`);
}

// Inject hooks into ~/.claude/settings.json
function injectHooks() {
  let settings = {};
  if (fs.existsSync(CLAUDE_SETTINGS)) {
    try { settings = JSON.parse(fs.readFileSync(CLAUDE_SETTINGS, "utf8")); }
    catch { warn("Could not parse settings.json — creating fresh hooks section"); }
  }

  if (!settings.hooks) settings.hooks = {};

  const hookDef = (script) => ([{
    matcher: "",
    hooks: [{ type: "command", command: `${PULSE_DIR}/hooks/${script}` }],
  }]);

  // Merge — don't overwrite existing hooks, just add Pulse entries
  const merge = (key, script) => {
    if (!settings.hooks[key]) settings.hooks[key] = [];
    const already = settings.hooks[key].some(
      (h) => h.hooks && h.hooks.some((hh) => hh.command && hh.command.includes("pulse"))
    );
    if (!already) settings.hooks[key].push(...hookDef(script));
  };

  merge("Stop", "on-stop.sh");
  merge("SubagentStop", "on-agent-stop.sh");
  merge("SessionStart", "on-session-start.sh");
  merge("UserPromptSubmit", "on-prompt.sh");

  fs.mkdirSync(path.dirname(CLAUDE_SETTINGS), { recursive: true });
  fs.writeFileSync(CLAUDE_SETTINGS, JSON.stringify(settings, null, 2));
  ok("Hooks injected into ~/.claude/settings.json");
}

// Init the DB and print welcome
function initAndWelcome() {
  spawnSync("python3", [path.join(PULSE_DIR, "run.py"), "session-start", "--session-id", "install"], {
    stdio: "inherit",
  });

  console.log("");
  console.log(`  ${ANSI.blue}  (o.o)${ANSI.reset}`);
  console.log(`  ${ANSI.blue} /|   |\\${ANSI.reset}  ${ANSI.bold}Pulse${ANSI.reset} · lv.1 · just hatched`);
  console.log(`  ${ANSI.blue}  d   b${ANSI.reset}`);
  console.log("");
  console.log(`  "Hi. I'm Pulse. I'll be watching. 👀`);
  console.log(`   Start a Claude Code session to wake me up."`);
  console.log("");
  console.log(`  Uninstall anytime: ${ANSI.yellow}npx pulse-dev uninstall${ANSI.reset}`);
  console.log("");
}

console.log("");
console.log(`  ${ANSI.bold}💓 Pulse installer${ANSI.reset}`);
console.log("");

checkPython();
copyFiles();
injectHooks();
initAndWelcome();
