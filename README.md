# NSY Projects Web

This repository holds the public NSY Projects website and the backend project apps that sit behind it.

## Layout

- `web_ui/` - static website files for Cloudflare Pages at `https://nsyprojects.com/`.
- `projects/` - one folder per backend or tool project.
- `projects/dem-claim/` - DEM claim Excel workflow, including its FastAPI app, local runner, deployment notes, ops templates, and test files.

Future projects should be added as `projects/<project-slug>/` so each project keeps its own app code, docs, tests, and deployment notes in one place.

## Important Runtime Boundary

GitHub stores the shared project code. Each computer still keeps its own private runtime setup outside Git:

- Codex app/CLI login and `~/.codex/auth.json`
- installed `dem-claim-excel` Codex skill under `~/.codex/skills/dem-claim-excel`
- Tesseract install
- Python virtual environments
- PM2 secrets, Cloudflare tunnel credentials, logs, uploads, and generated Excel outputs

The DEM app fallback path runs local `codex exec` on the computer that deploys or tests the app. That is intentional. Do not commit Codex credentials or Cloudflare credentials to this repo.

## Working Across Computers

Before editing on either computer:

```bash
git pull
```

After editing:

```bash
git add .
git commit -m "Describe the change"
git push
```

On the deploy computer, pull the latest code and restart the backend process:

```bash
git pull
pm2 restart nsy-dem-app
```

See `projects/dem-claim/README.md` for the DEM app details.
