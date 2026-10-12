const repoRoot = "/path/to/nsy-projects-web";
const appDir = `${repoRoot}/projects/Python Study App`;
const opsDir = `${appDir}/ops`;
const persistentDataDir = "/path/to/persistent/code-practice-data";

module.exports = {
  apps: [
    {
      name: "nsy-python-study",
      cwd: appDir,
      script: ".venv/bin/python",
      args: ["-m", "uvicorn", "code_practice.app:app", "--host", "127.0.0.1", "--port", "8791"],
      interpreter: "none",
      env: {
        CODE_PRACTICE_DATA_DIR: persistentDataDir,
        CODE_PRACTICE_SEED_DB: `${appDir}/seed_data/initial_progress.db`,
        CODE_PRACTICE_AUTH_USERNAME: "admin",
        CODE_PRACTICE_SESSION_SECRET: "use-the-same-secret-as-the-NSY-login-service",
        CODE_PRACTICE_AUTH_COOKIE_NAME: "dem_session",
        CODE_PRACTICE_LOGIN_URL: "https://dem.nsyprojects.com/login",
        CODE_PRACTICE_PUBLIC_ORIGIN: "https://replace-with-study-hostname.nsyprojects.com",
        CODEX_BIN: "/Applications/ChatGPT.app/Contents/Resources/codex-cli/bin/codex",
      },
      out_file: `${opsDir}/logs/nsy-python-study.out.log`,
      error_file: `${opsDir}/logs/nsy-python-study.err.log`,
      merge_logs: true,
      max_restarts: 10,
      restart_delay: 2000,
    },
  ],
};
