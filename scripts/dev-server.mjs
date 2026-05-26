import { mkdirSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import { spawn } from "node:child_process";

const rootDir = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const tempDir = resolve(rootDir, ".tmp");
const tsxCli = resolve(rootDir, "node_modules", "tsx", "dist", "cli.mjs");

mkdirSync(tempDir, { recursive: true });

const child = spawn(process.execPath, [tsxCli, "watch", "index.ts"], {
  cwd: resolve(rootDir, "server"),
  env: {
    ...process.env,
    TMP: tempDir,
    TEMP: tempDir,
    TMPDIR: tempDir
  },
  stdio: "inherit",
  windowsHide: true
});

child.on("exit", (code, signal) => {
  if (signal) {
    process.kill(process.pid, signal);
    return;
  }

  process.exit(code ?? 0);
});
