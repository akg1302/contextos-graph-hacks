# ContextOS — Evidence-first Company Brain

**Graph Hacks 2026 · WeMakeDevs × FalkorDB**

ContextOS is a graph-powered incident investigation assistant for a fictional company. It traverses a FalkorDB knowledge graph connecting incidents, services, owners, on-call engineers, runbooks, prior incidents, decisions, and persistent session memories. It explains its recommendations with graph evidence paths. All seed data is synthetic.

## Run it on Replit (no Docker, WSL, cloud credentials, or API key)

1. Import this ZIP as a Replit project. Make sure the files inside the ZIP land at the project root (you should see `.replit`, `requirements.txt`, and `streamlit_app.py` together).
2. Open the project and press **Run**. The `.replit` run command installs dependencies and starts Streamlit on port 3000. First install can take a few minutes because FalkorDBLite includes a graph engine.
3. On first launch, the app automatically seeds a synthetic demo graph if the selected graph is empty. No API key is required.
4. Try: **“Why is checkout failing, and who should investigate?”** Then ask **“Have we seen a similar incident before? What did we decide?”**
5. Inspect the evidence paths, graph topology, and persistent memory panel.

The app uses the real embedded FalkorDB engine via FalkorDBLite and Cypher queries; it does not replace the graph with a dictionary or a mock. Local database files are stored under `data/`. FalkorDBLite requires Python 3.12 or newer.

### If Replit does not start the app

Open the Build/Console panel and inspect the first installation or startup error. The common blocker is a platform/runtime mismatch while installing the embedded database binary. Do not add credentials or switch to a fake in-memory graph. Use the exact error to diagnose the environment.

## Run locally (Linux/macOS with Python 3.12+)

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

On Windows, use PowerShell activation (`.venv\Scripts\Activate.ps1`). If FalkorDBLite cannot install on your machine, the optional managed-cloud path is documented below; it is not required for the Replit path.

## Optional managed FalkorDB Cloud connection

Install `requirements-cloud.txt`, set `FALKORDB_MODE=cloud`, and provide `FALKORDB_HOST`, `FALKORDB_PORT`, `FALKORDB_USERNAME`, `FALKORDB_PASSWORD`, and `FALKORDB_SSL` through environment secrets. Only use this mode when the instance is healthy. Never commit credentials or use private company data in the demo.

## Graph model and key implementation

- **Nodes:** `Service`, `Person`, `Project`, `Incident`, `Decision`, `Document`, `Session`, `Memory`.
- **Relationships:** `DEPENDS_ON`, `OWNS`, `ON_CALL_FOR`, `AFFECTS`, `INVOLVES`, `RESOLVED_BY`, `FOLLOWED_BY`, `RELEVANT_RUNBOOK`, `DOCUMENTED_IN`, `CONTAINS_MEMORY`, `ABOUT`, and more.
- **Why graph matters:** multi-hop traversals connect an incident to affected services, ownership, runbooks, and prior decisions. Session episodes are persisted in the same graph. Removing FalkorDB removes the relationship store and reasoning substrate.
- See [`docs/GRAPH_MODEL.md`](docs/GRAPH_MODEL.md) and [`app/graph_store.py`](app/graph_store.py) for the schema and Cypher.

## Tests

```bash
python -m pip install pytest
python -m pytest -q
```

The included unit tests check routing, memory writes, and parameterization using a fake query interface. They are **not** a substitute for testing the embedded database engine. The live FalkorDBLite startup/query flow must be verified in the target workspace before submission.

## Tracks

- **Primary:** Track 03 — Company Brain.
- **Secondary candidate:** Track 01 — Agents That Act on Connected Data (advisory triage only; no production actions are executed).
- Do not claim Track 02 unless richer memory/coordination is implemented and demonstrated.

## AI assistance and competition integrity

AI assistance was used for project planning, code drafting/refinement, tests, and documentation. The participant must personally review and understand the core graph queries, verify the app, and disclose the tools actually used. This ZIP is a development artifact, not proof of a verified live deployment. Follow the event's rules on when work may begin; do not misrepresent pre-event scaffolding as work completed after the start.

## Demo flow

See [`docs/DEMO_SCRIPT.md`](docs/DEMO_SCRIPT.md). Record a demo only after the app starts and the graph queries have been verified in the target environment.
