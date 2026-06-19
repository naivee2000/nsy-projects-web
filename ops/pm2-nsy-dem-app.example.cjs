const root = "/path/to/nsy-dem-app-handoff";
const appDir = `${root}/projects/dem-claim/app`;
const opsDir = `${root}/ops`;

module.exports = {
  apps: [
    {
      name: "nsy-dem-app",
      cwd: appDir,
      script: "./.venv/bin/python",
      args: ["-m", "uvicorn", "app_zh_secure:app", "--host", "127.0.0.1", "--port", "8000"],
      interpreter: "none",
      env: {
        DEM_SKILL_ROOT: "/Users/YOUR_USER/.codex/skills/dem-claim-excel",
        DEM_JOB_ROOT: `${appDir}/web_outputs`,
        DEM_JOB_RETENTION_HOURS: "24",
        DEM_JOB_CLEANUP_INTERVAL_SECONDS: "3600",
        CODEX_BIN: "/Applications/Codex.app/Contents/Resources/codex",
        DEM_AUTH_USERNAME: "admin",
        DEM_AUTH_PASSWORD_HASH: "pbkdf2_sha256$...",
        DEM_SESSION_SECRET: "replace-with-a-long-random-secret",
      },
      out_file: `${opsDir}/logs/nsy-dem-app.out.log`,
      error_file: `${opsDir}/logs/nsy-dem-app.err.log`,
      merge_logs: true,
      max_restarts: 10,
    },
    {
      name: "nsy-dem-tunnel",
      cwd: root,
      script: "/opt/homebrew/bin/cloudflared",
      args: ["tunnel", "--config", `${opsDir}/cloudflared-nsy-dem-app.yml`, "run", "nsy-dem-app"],
      interpreter: "none",
      out_file: `${opsDir}/logs/nsy-dem-tunnel.out.log`,
      error_file: `${opsDir}/logs/nsy-dem-tunnel.err.log`,
      merge_logs: true,
      max_restarts: 10,
    },
  ],
};
