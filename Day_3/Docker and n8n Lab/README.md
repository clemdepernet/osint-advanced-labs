# Docker & n8n Lab (Day 3)

Containers for OSINT + an automated OSINT→STIX pipeline in n8n.

| Path | What |
|---|---|
| `DockerN8N_Lab.md` / `.pdf` | the guided lab (Docker basics → disposable OSINT containers → n8n → agentic pipeline) |
| `docker-compose.yml` | brings up n8n (`:5678`) and a throwaway web server (`:8088`) |
| `workflows/osint_stix_pipeline.json` | import into n8n: parallel agents → STIX writer → OpenCTI/TAXII + alert |
| `site/` | demo content for the throwaway web server |

```bash
docker compose up -d n8n        # http://localhost:5678
docker compose down -v          # tear everything down
```
