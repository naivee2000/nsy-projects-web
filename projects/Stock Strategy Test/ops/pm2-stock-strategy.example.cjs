const repoRoot = "/path/to/nsy-projects-web";
const appDir = `${repoRoot}/projects/Stock Strategy Test`;
const opsDir = `${appDir}/ops`;

module.exports = {
  apps: [
    {
      name: "nsy-stock-strategy",
      cwd: appDir,
      script: `${appDir}/.venv/bin/python`,
      args: ["app.py", "--host", "127.0.0.1", "--port", "8790"],
      interpreter: "none",
      env: {
        MARKETDATA_API_TOKEN: "set-the-personal-token-on-this-machine",
        STOCK_STRATEGY_DATA_DIR: `${appDir}/data`,
        STOCK_STRATEGY_AUTH_USERNAME: "admin",
        STOCK_STRATEGY_SESSION_SECRET: "use-the-same-secret-as-the-NSY-login-service",
        STOCK_STRATEGY_AUTH_COOKIE_NAME: "dem_session",
        STOCK_STRATEGY_LOGIN_URL: "https://dem.nsyprojects.com/login",
        STOCK_STRATEGY_PUBLIC_ORIGIN: "https://strategy.nsyprojects.com",
      },
      out_file: `${opsDir}/logs/nsy-stock-strategy.out.log`,
      error_file: `${opsDir}/logs/nsy-stock-strategy.err.log`,
      merge_logs: true,
      max_restarts: 10,
      restart_delay: 2000,
    },
  ],
};
