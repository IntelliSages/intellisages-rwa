# RWAs Intelligence

**Analytic Sages' market-data and research intelligence platform for tokenized real-world assets (RWAs).**

RWAs Intelligence connects asset discovery, issuer products, blockchain deployments, spot and perpetual markets, funding, DeFi opportunities, trader intelligence and relevant market/onchain/macro events. It helps users move from a market-wide question to the exact instrument, issuer, network, venue and observation behind an answer.

> **Product principle:** a number is useful only when its meaning, identity, scope, time and coverage are clear. Partial or missing observations must remain visible; a successful API response is not proof of complete market coverage.

## Governing MVP plan

**[MVP_IMPLEMENTATION_BLUEPRINT.md](MVP_IMPLEMENTATION_BLUEPRINT.md) is the governing implementation baseline.** It defines the 16-page MVP, launch qualifications, shared behaviours, provider tiers, metric readiness, implementation work packages, inherited QA defects, acceptance gates and post-launch phases. Changes to approved scope or gates require product-owner approval.

## Documentation map

| Document | Purpose |
|---|---|
| [MVP_IMPLEMENTATION_BLUEPRINT.md](MVP_IMPLEMENTATION_BLUEPRINT.md) | Governing MVP scope, delivery sequence, launch gates and operating plan |
| [RULES.md](RULES.md) | Binding identity, metric, evidence, aggregation, safety and implementation rules |
| [PRD.md](PRD.md) | Product vision, users, MVP scope, journeys and functional requirements |
| [ROADMAP.md](ROADMAP.md) | Delivery phases, dependencies, milestones and release gates |
| [ARCHITECTURE.md](ARCHITECTURE.md) | Proposed system architecture, domain model, ingestion and serving design |
| [TASKS.md](TASKS.md) | Engineering work breakdown and acceptance tasks |
| [PROGRESS.md](PROGRESS.md) | Verified implementation status and decision log |
| [docs/BASELINE_AUDIT.md](docs/BASELINE_AUDIT.md) | Repository and supplied prototype baseline; known gaps |
| [docs/FRONTEND_SPEC.md](docs/FRONTEND_SPEC.md) | Screen inventory, interaction rules and UI states |
| [docs/DATA_DICTIONARY.md](docs/DATA_DICTIONARY.md) | Shared metric meanings, units, formulas and availability rules |
| [docs/SCREEN_METRIC_INVENTORY.md](docs/SCREEN_METRIC_INVENTORY.md) | Screen-by-screen field inventory and removed/deferred reconciliation |
| [docs/DATA_IDENTITY_AND_AGGREGATION.md](docs/DATA_IDENTITY_AND_AGGREGATION.md) | Canonical identity, classification, supply, volume and deduplication |
| [docs/PROVIDER_ENDPOINT_REGISTRY.md](docs/PROVIDER_ENDPOINT_REGISTRY.md) | Provider routes, retained evidence, access and remaining validation |
| [docs/API_CONTRACTS.md](docs/API_CONTRACTS.md) | Proposed internal read APIs and typed response contracts |
| [docs/VALIDATION_MATRIX.md](docs/VALIDATION_MATRIX.md) | Metric readiness, source coverage, blockers and QA criteria |
| [docs/RESEARCH_AND_OPEN_DECISIONS.md](docs/RESEARCH_AND_OPEN_DECISIONS.md) | External context, research implications and unresolved product decisions |

## Product scope

The approved MVP includes 16 pages: Home, Crypto Screener, Tokenized RWA Screener, Correlation, HIP-3, Ondo, bStocks, xStocks, Backpack, Robinhood Tokenized Assets, PreStocks, Paimon, Funding Rates, DeFi, Trader Intelligence and Intelligence Event Feed.

A page may remain visible with specific metrics unavailable or restricted. See the governing blueprint and PRD for page-level launch qualifications and explicit exclusions.

## Current status

PR #6 has delivered the first frontend shell and page-layout pass. The Tokenized RWA Screener and read-only catalogue API are the current implementation increment. No live market observations, provider-complete universe, production provider entitlements or shared deployment are asserted. See PROGRESS.md and VALIDATION_MATRIX.md.

## Engineering approach

1. Follow MVP_IMPLEMENTATION_BLUEPRINT.md as the implementation sequence and scope baseline.
2. Preserve approved product decisions and source evidence.
3. Audit the actual repository and prototype before selecting or replacing technology.
4. Build canonical identity and data-quality foundations before market-wide aggregation.
5. Implement provider adapters independently from domain calculations and UI.
6. Serve typed, provenance-aware read models; never let the UI infer missing data as zero.
7. Deliver incrementally, with reproducible fixtures, regression tests and release gates.

## Working agreement

Classify every new statement as **approved product decision**, **retained source evidence**, **proposal**, **unverified assumption**, **deferred scope** or **implementation result**. Update related documents together and keep the progress log honest.

## Run the frontend locally

The Next.js frontend can run independently of the API. From the repository root:

```bash
npm install
npm run dev
```

Open http://localhost:3000. Without an API connection, the Tokenized RWA Screener displays an explicit API-not-configured state; it does not load sample market data.

To run the local catalogue API, open a second terminal:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements-dev.txt
cd backend
export DATABASE_URL='sqlite:///./local.db'
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```

In the frontend terminal, set the server-only API URL before starting Next.js:

```bash
RWA_API_BASE_URL=http://127.0.0.1:8000 npm run dev
```

The same variable can be placed in `.env.local` (copy `.env.example`). The browser calls a same-origin Next.js proxy; the backend URL is not exposed as a public client-side environment variable. The API currently serves registered identity/classification records only. It does not ingest market observations or prove provider-universe completeness.


## Deploy the API to Render with PostgreSQL

The repository includes a Render Blueprint at `render.yaml`. It provisions a persistent PostgreSQL 16 database and a Python web service in Frankfurt, connects them over Render's private network, runs Alembic migrations as a pre-deploy step, and checks database readiness at `/healthz`.

### Provisioning

1. In Render, choose **New → Blueprint** and connect `IntelliSages/intellisages-rwa`.
2. Select the `feat/render-postgres-deployment` branch while reviewing this change, or `main` after it is merged.
3. Review the Blueprint resources and the current Render pricing before applying. The configuration uses a Starter web service and Basic PostgreSQL database so the API does not sleep and the database is persistent. These are paid Render resources.
4. Apply the Blueprint. Render creates `intellisages-rwa-db` and `intellisages-rwa-api`. The database connection string is injected internally; it is never committed to Git.
5. Wait for the pre-deploy migration and health check to pass. The service is ready only when `/healthz` returns HTTP 200 and reports `database: connected`.

### Required backend secrets

The Blueprint intentionally does not create a registry admin token or CoinGecko API key. Add secrets in the Render service's Environment page only when needed:

- `REGISTRY_ADMIN_TOKEN`: a long, randomly generated secret for the protected import/review API. Keep it server-side; never add it to Vercel or browser code.
- `COINGECKO_API_KEY`: optional, only for running the provider snapshot client from a trusted operator environment.

Import administration remains disabled (HTTP 503) until `REGISTRY_ADMIN_TOKEN` is configured. Do not expose import/review routes through the public frontend.

### Connect Vercel

After Render reports the API service as Live, copy its HTTPS service URL (for example, `https://intellisages-rwa-api.onrender.com`). In the Vercel project `intellisages-rwa`, add the server-only environment variable:

```text
RWA_API_BASE_URL=https://<your-render-service>.onrender.com
```

Apply it to Preview and Production, then redeploy the frontend. The existing Next.js route handler proxies catalogue requests server-side; browser requests remain same-origin and no CORS wildcard is required. Do not prefix this variable with `NEXT_PUBLIC_`.

### Database and release safety

- Render's managed PostgreSQL is the persistent source of truth; the local SQLite database is not copied or used in production.
- Alembic runs before each new web-service deployment. A failed migration prevents the new version from being promoted to serving traffic.
- The health check verifies both process and database connectivity.
- PostgreSQL URLs supplied as `postgres://` or `postgresql://` are normalized to the installed psycopg v3 driver.
- Backups, point-in-time recovery and retention depend on the selected Render database plan; confirm the current plan's backup policy before importing production review data.
- The initial Render database is empty. Existing local staged CoinGecko review batches are not automatically copied; migrate/export/import them through a separately reviewed, authenticated data-transfer procedure. Do not copy a local SQLite file into production.
