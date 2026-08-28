const repoRoot = "/path/to/nsy-projects-web";
const appDir = `${repoRoot}/projects/Stock Strategy Test`;
const opsDir = `${appDir}/ops`;

module.exports = {
  apps: [
    {
      name: "nsy-stock-strategy",
      cwd: appDir,
      script: ".venv/bin/python",
      args: ["app.py", "--host", "127.0.0.1", "--port", "8790"],
      interpreter: "none",
      env: {
        STOCK_STRATEGY_DATA_DIR: `${appDir}/data`,
        STOCK_STRATEGY_PUBLIC_MODE: "1",
        STOCK_STRATEGY_PUBLIC_BACKTESTS_PER_HOUR: "12",
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
