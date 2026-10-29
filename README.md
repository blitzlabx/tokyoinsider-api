# Blitz TokyoInsider Scraper API

<p align="center">
  <strong>Free • CORS-enabled • Fast • Built by Blitz</strong><br>
  Turn tokyoinsider.net / .com / .org into a clean JSON API
</p>

<p align="center">
  <a href="https://github.com/blitzlabx"><img src="https://img.shields.io/badge/Author-Blitz-blue?style=for-the-badge" alt="Author"></a>
  <a href="https://x.com/blitzlabx"><img src="https://img.shields.io/badge/X-@blitzlabx-black?style=for-the-badge&logo=x" alt="X"></a>
  <a href="https://github.com/blitzlabx"><img src="https://img.shields.io/badge/GitHub-blitzlabx-181717?style=for-the-badge&logo=github" alt="GitHub"></a>
  <a href="https://blitz.devs.surf"><img src="https://img.shields.io/badge/Site-blitz.devs.surf-purple?style=for-the-badge" alt="Site"></a>
</p>

---

## Credits & Ownership

**This project is created, owned, and maintained by Blitz.**

- **Author**: Blitz
- **Handle / X**: [@blitzlabx](https://x.com/blitzlabx)
- **GitHub**: [github.com/blitzlabx](https://github.com/blitzlabx)
- **Website**: [blitz.devs.surf](https://blitz.devs.surf)

All credits, attribution, and rights belong to **Blitz (@blitzlabx)**.  
If you use, fork, or build on this API, please keep the credits intact.

---

## What is this?

A lightweight FastAPI service that scrapes **TokyoInsider** (tokyoinsider.net / .com / .org) and exposes a clean, documented JSON API.

You get:

- Full anime catalog + fuzzy local suggestions
- Live search with filters
- Latest releases & home-page strip
- Full series metadata (titles, genres, status, related, etc.)
- Decoded download links for episodes, movies, OVAs, and specials
- Media URL health checks

No frontend required. Point any client (web app, Discord bot, mobile app, CLI) at the endpoints and go.

---

## Features

| Feature | Description |
|---------|-------------|
| **CORS-free** | Ready for browser clients (`Access-Control-Allow-Origin: *`) |
| **Cloudflare aware** | Built-in support for FlareSolverr when the site challenges you |
| **Smart caching** | In-memory TTL cache for catalog, search, and detail pages |
| **Rate limiting** | Configurable minimum interval between upstream requests |
| **Mirror fallback** | Tries `.net` → `.com` → `.org` automatically |
| **Link decoding** | Port of TokyoInsider’s client-side cipher (ROT13 → reverse → base64 → XOR) |
| **Fuzzy search** | Local catalog suggestions powered by RapidFuzz |
| **Docker ready** | Single-file Dockerfile + optional docker-compose with FlareSolverr |
| **Blitz branded** | Every response carries author credit |

---

## Quick Start

### 1. Clone

```bash
git clone https://github.com/blitzlabx/tokyoinsider-api.git
cd tokyoinsider-api
```

### 2. Run with the helper script

```bash
bash run.sh
```

The API will be available at `http://localhost:8000`.  
Interactive docs: `http://localhost:8000/docs`

### 3. Or with Docker

```bash
docker build -t blitz-ti-api .
docker run -p 8000:8000 blitz-ti-api
```

### 4. Recommended: FlareSolverr (for Cloudflare)

TokyoInsider is often behind Cloudflare. The cleanest way to solve challenges is FlareSolverr:

```bash
# Start FlareSolverr (example)
docker run -d --name flaresolverr -p 8191:8191 ghcr.io/flaresolverr/flaresolverr:latest

# Then start the API with the env var
export TI_FLARESOLVERR_URL=http://localhost:8191
bash run.sh
```

You can also put both services in a `docker-compose.yml` (see below).

---

## Environment Variables

All settings use the `TI_` prefix. See `.env.example`.

| Variable | Default | Purpose |
|----------|---------|---------|
| `TI_BASE_URL` | `https://www.tokyoinsider.net` | Primary origin |
| `TI_IMPERSONATE` | `chrome124` | curl_cffi browser fingerprint |
| `TI_PROXY` | — | Optional HTTP/S proxy |
| `TI_FLARESOLVERR_URL` | — | FlareSolverr base URL (e.g. `http://localhost:8191`) |
| `TI_MIN_INTERVAL` | `0.35` | Minimum seconds between upstream requests |
| `TI_CACHE_TTL` | `300` | General cache TTL (seconds) |
| `TI_CATALOG_TTL` | `21600` | Catalog cache (6 hours) |
| `TI_SEARCH_TTL` | `60` | Search cache |

---

## API Endpoints

Base path: `/api/v1`

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Service info + Blitz credits |
| `GET` | `/health` | Health check |
| `GET` | `/api/v1/catalog` | Full library index (`?letter=B` to filter) |
| `GET` | `/api/v1/suggest?q=bleach` | Instant local fuzzy suggestions |
| `GET` | `/api/v1/search?q=bleach` | Live site search + optional filters |
| `GET` | `/api/v1/latest` | Newest releases |
| `GET` | `/api/v1/home` | Front-page strip |
| `GET` | `/api/v1/browse?letter=B` | Everything under a letter |
| `GET` | `/api/v1/anime/{letter}/{slug}` | Full metadata + all decoded links |
| `GET` | `/api/v1/download/{letter}/{slug}` | All decoded download links |
| `GET` | `/api/v1/download/{letter}/{slug}/{kind}/{number}` | Single episode / movie / ova / special |
| `GET` | `/api/v1/media-check?url=` | HEAD-check a media URL |

**Notes**

- `kind` is one of: `episode`, `movie`, `ova`, `special`
- Slugs keep their suffixes, e.g. `Bleach_(TV)`, `Bleach:_Sennen_Kessen-hen_(TV)`
- Large series are paginated; look at `pagination.next_start` to continue

### Example responses

**Suggest**

```json
[
  {
    "title": "Bleach (TV)",
    "url": "https://www.tokyoinsider.net/anime/B/Bleach_(TV)",
    "letter": "B",
    "slug": "Bleach_(TV)",
    "cover": null,
    "score": 100.0
  }
]
```

**Root**

```json
{
  "name": "Blitz TokyoInsider Scraper API",
  "version": "1.0.0",
  "author": "Blitz",
  "handle": "@blitzlabx",
  "github": "https://github.com/blitzlabx",
  "docs": "/docs",
  "credits": "All credits to Blitz (@blitzlabx)"
}
```

---

## Architecture (short)

```
Client
  ↓
FastAPI (Blitz TokyoInsider Scraper API)
  ↓
Fetcher  →  curl_cffi / httpx  →  TokyoInsider
         ↘ FlareSolverr (when challenged)
  ↓
Parser + Crypto (ROT13 → reverse → base64 → XOR)
  ↓
JSON response
```

- **Fetcher** – throttling, mirror rotation, Cloudflare detection, optional FlareSolverr
- **Crypto** – faithful port of the site’s inline link cipher
- **Catalog** – loads the site’s autocomplete index once and keeps it in memory for fuzzy search
- **Cache** – simple async TTL cache

---

## Docker Compose (API + FlareSolverr)

```yaml
version: "3.8"

services:
  flaresolverr:
    image: ghcr.io/flaresolverr/flaresolverr:latest
    ports:
      - "8191:8191"
    environment:
      - LOG_LEVEL=info
    restart: unless-stopped

  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      - TI_FLARESOLVERR_URL=http://flaresolverr:8191
      - TI_MIN_INTERVAL=0.4
    depends_on:
      - flaresolverr
    restart: unless-stopped
```

Save as `docker-compose.yml` and run:

```bash
docker compose up -d
```

---

## Development

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Run the small crypto unit tests:

```bash
python -m pytest tests/ -q
```

---

## Known limitations

- `media.tokyoinsider.com` can be unreliable; some decoded URLs may 404 even when the index is correct.
- Without FlareSolverr, live endpoints (`/search`, `/anime/...`, `/latest`, etc.) may return `cloudflare_blocked`.
- The catalog endpoint relies on the site’s public autocomplete JS; if that file changes format, the local suggestions will need an update.
- Aggressive scraping can still get temporary rate-limits — keep `TI_MIN_INTERVAL` reasonable.

---

## Project structure

```
tokyoinsider-api/
├── app/
│   ├── main.py          # FastAPI app + Blitz branding
│   ├── config.py        # Settings (TI_* env vars)
│   ├── fetch.py         # HTTP client + FlareSolverr
│   ├── crypto.py        # Link cipher (ROT13 / reverse / b64 / XOR)
│   ├── parse.py         # HTML parsers
│   ├── catalog.py       # Autocomplete index + fuzzy search
│   ├── cache.py         # Async TTL cache
│   ├── models.py        # Pydantic response models
│   ├── errors.py        # Upstream / decode errors
│   └── routers/         # Endpoint modules
├── tests/
│   └── test_crypto.py
├── Dockerfile
├── run.sh
├── requirements.txt
├── .env.example
├── LICENSE              # MIT — Copyright (c) 2026 Blitz (@blitzlabx)
└── README.md
```

---

## License

MIT License — Copyright (c) 2026 **Blitz (@blitzlabx)**

See [LICENSE](LICENSE) for the full text.

---

## Support & Contact

Built with late-night energy by **Blitz**.

- X / Twitter: [@blitzlabx](https://x.com/blitzlabx)
- GitHub: [github.com/blitzlabx](https://github.com/blitzlabx)
- Site: [blitz.devs.surf](https://blitz.devs.surf)

If this API helps you, a star on the repo or a shout-out to **@blitzlabx** is always appreciated.

---

<p align="center">
  <sub>Made by Blitz · All credits to Blitz (@blitzlabx)</sub>
</p>
