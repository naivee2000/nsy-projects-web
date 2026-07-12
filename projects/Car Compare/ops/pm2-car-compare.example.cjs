const repoRoot = "/path/to/nsy-projects-web";
const appDir = `${repoRoot}/projects/Car Compare`;
const opsDir = `${appDir}/ops`;

module.exports = {
  apps: [
    {
      name: "nsy-car-compare",
      cwd: appDir,
      script: "/opt/homebrew/bin/python3",
      args: ["app.py", "--host", "127.0.0.1", "--port", "8787"],
      interpreter: "none",
      env: {
        CODEX_BIN: "/Applications/ChatGPT.app/Contents/Resources/codex",
        CAR_COMPARE_AUTH_USERNAME: "admin",
        CAR_COMPARE_SESSION_SECRET: "use-the-same-secret-as-the-NSY-login-service",
        CAR_COMPARE_PUBLIC_ORIGIN: "https://carcompare.nsyprojects.com",
      },
      out_file: `${opsDir}/logs/nsy-car-compare.out.log`,
      error_file: `${opsDir}/logs/nsy-car-compare.err.log`,
      merge_logs: true,
      max_restarts: 10,
    },
  ],
};
