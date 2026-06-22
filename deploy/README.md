# Deployment

KidQuest runs 24/7 on a Proxmox LXC (**CT 110** on `zeratul`) and serves only
**pre-generated content** — no GPU, no inference. The daily content batch runs
separately on the GPU box and writes to the NAS content store, mounted read-only
here.

## Components
- **api** (`Dockerfile.api`): FastAPI + uvicorn. Serves `/health`, `/profile/{id}`,
  `/content/today/{id}` and static media. CPU-only.
- **web** (`Dockerfile.web` + `nginx.conf`): nginx serving the built Phaser client
  and reverse-proxying API paths to `api`.

## Local / CT run
```bash
KIDQUEST_CONTENT_DIR=/path/to/content-store docker compose up -d --build
# game:   http://localhost:8080
# health: curl http://localhost:8080/health  -> {"ok":true,"schema_version":"1"}
```

`KIDQUEST_CONTENT_DIR` is bind-mounted read-only to `/content-store` in the api
container. On the CT it points at the NAS path (see `lxc/ct110.md`).

## Provisioning CT 110
Full runbook in [`lxc/ct110.md`](lxc/ct110.md): create the unprivileged LXC
(`nesting=1`), bind-mount the NAS content store, install Docker, clone, and
`docker compose up`. This is a production change — run it deliberately.
