import { spawnSync } from "node:child_process";
import { existsSync, mkdirSync, rmSync } from "node:fs";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));
const adminRoot = resolve(__dirname, "..");
const cacheRoot = resolve(adminRoot, ".accounting-ui");
const repoDir = resolve(cacheRoot, "cz-accounting-module");
const packageDir = resolve(repoDir, "packages", "accounting-ui");
const repository = "https://github.com/Lakyn80/cz-accounting-module.git";
const tag = "v0.1.0";
const expectedCommit = "dddfe59ad4a0f08f6f8cb0f2217d8e0342f527f6";

function run(command, args, options = {}) {
  const result = spawnSync(command, args, {
    cwd: options.cwd ?? adminRoot,
    stdio: options.stdio ?? "inherit",
    encoding: "utf8",
  });
  if (result.status !== 0) {
    throw new Error(`${command} ${args.join(" ")} failed with exit code ${result.status}`);
  }
  return result.stdout?.trim() ?? "";
}

function currentCommit() {
  if (!existsSync(resolve(repoDir, ".git"))) {
    return "";
  }
  const result = spawnSync("git", ["rev-parse", "HEAD"], {
    cwd: repoDir,
    encoding: "utf8",
  });
  return result.status === 0 ? result.stdout.trim() : "";
}

function removeCachedRepo() {
  const resolvedRepo = resolve(repoDir);
  if (!resolvedRepo.startsWith(cacheRoot)) {
    throw new Error(`Refusing to remove path outside accounting UI cache: ${resolvedRepo}`);
  }
  rmSync(resolvedRepo, { recursive: true, force: true });
}

mkdirSync(cacheRoot, { recursive: true });

if (currentCommit() !== expectedCommit) {
  if (existsSync(repoDir)) {
    removeCachedRepo();
  }
  run("git", ["clone", "--depth", "1", "--branch", tag, repository, repoDir]);
}

if (!existsSync(resolve(packageDir, "src", "index.ts"))) {
  throw new Error(`@cz-accounting/accounting-ui was not found at ${packageDir}`);
}

console.log(`@cz-accounting/accounting-ui ready from ${tag} (${expectedCommit.slice(0, 7)})`);
