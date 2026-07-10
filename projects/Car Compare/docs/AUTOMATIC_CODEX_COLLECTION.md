# Automatic Codex Collection

The app can start a local Codex collection job from the `Collect` button.

## How It Works

```text
User enters car query
-> app parses make/model/trim
-> app builds source plan
-> app checks Visor public used and new-car facets first
-> app can continue into a local Codex CLI job for website collection when Codex is available
-> Codex opens/uses source websites when tools are available
-> adapter or Codex returns structured JSON
-> app deduplicates listings and graphs depreciation
```

The bridge is server-side. The website does not talk to a model API directly; it starts a process on the computer running the backend. After deployment, visitors on other computers use that host connection and do not provide their own Codex login.

For sources like Visor, the app can use public market-facet pages directly. These are aggregate observations, not individual VIN/dealer listings. Used-market rows are labeled `visor_public_facets`; new-car age-0 rows are labeled `visor_public_facets_new` with `condition=new`.

If Codex fails after Visor returned usable rows, the job should complete with a partial result and preserve the Visor observations.

## How To Know It Is Running

After you click `Collect`, the Collector panel should move through these states:

- `queued`: the app accepted the job.
- `running: Codex process started (PID ...)`: the local Codex process is alive.
- `running: Codex is still running for ... (PID ...)`: the app is still polling and the child process has not exited.
- `completed`: Codex returned structured JSON and the app will rerun the graph.
- `failed` or `blocked`: Codex exited, timed out, hit a usage limit, or could not access the requested data.

While the job is running, the app checks the Codex process about once per second and the browser polls the app every few seconds. Long website research can still take several minutes, but the elapsed-time/PID line means the app has not frozen.

## Requirements On Another Computer

- Codex installed.
- Codex logged in.
- `codex` available on PATH, or `CODEX_BIN` set to the executable path.
- The app running locally on `127.0.0.1`.

The app checks `CODEX_BIN`, `PATH`, official standalone install locations on macOS/Linux/Windows, and these macOS desktop locations. To override discovery manually, use the path that exists on the host:

```bash
export CODEX_BIN="/Applications/ChatGPT.app/Contents/Resources/codex"
```

The standalone Codex desktop fallback is `/Applications/Codex.app/Contents/Resources/codex`.

After moving into the NSY projects repo, a typical run path is:

```bash
cd "/Users/shaoyangni/Desktop/Python Files/nsy-dem-app-handoff/projects/Car Compare"
python3 app.py --host 127.0.0.1 --port 8787
```

## Safety

The app does not pass arbitrary shell commands from the browser. It only passes the vehicle query into a fixed Codex prompt with a fixed JSON schema.

The app should stay local-only unless auth is added. Automatic collection can consume Codex usage.

## Fallback

If Codex is not installed, not logged in, or cannot operate a website, the app still supports manual capture import and Visor API-style adapters.
