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
        // Put this directory on a persistent disk/volume in production.
        CAR_COMPARE_CACHE_DIR: `${appDir}/data/cache`,
        CAR_COMPARE_CACHE_ENABLED: "1",
        // All verified marketplace and research cache entries are hard-capped at 3 days.
        CAR_COMPARE_RECENT_CACHE_TTL_SECONDS: "259200",
        CAR_COMPARE_OLDER_CACHE_TTL_SECONDS: "259200",
        CAR_COMPARE_GENERATION_CACHE_TTL_SECONDS: "259200",
        CAR_COMPARE_REVIEW_CACHE_TTL_SECONDS: "259200",
        // Deterministic audits finalize collection; generation research still runs automatically.
        CAR_COMPARE_CODEX_COLLECTION_REVIEW: "0",
        // Two browser pages and up to three small indexed-search batches run concurrently.
        CAR_COMPARE_MARKETPLACE_CONCURRENCY: "2",
        CAR_COMPARE_CODEX_SEARCH_WORKERS: "3",
        CAR_COMPARE_CODEX_SEARCH_BATCH_SIZE: "5",
        // Keeps Playwright headless and the macOS regular-Chrome fallback minimized.
        CAR_COMPARE_BACKGROUND_MODE: "1",
        // Runs the event-driven regular-Chrome retry on macOS. Set to 0 only for diagnosis.
        CAR_COMPARE_HOST_CHROME_FALLBACK: "1",
        // Uses native Codex web search for an official source page blocked by the host network.
        CAR_COMPARE_CODEX_SEARCH_FALLBACK: "1",
        // Manual recovery lease when host Chrome cannot produce an audit. Allowed range: 300-3600.
        CAR_COMPARE_FALLBACK_LEASE_SECONDS: "1200",
      },
      out_file: `${opsDir}/logs/nsy-car-compare.out.log`,
      error_file: `${opsDir}/logs/nsy-car-compare.err.log`,
      merge_logs: true,
      max_restarts: 10,
    },
  ],
};
