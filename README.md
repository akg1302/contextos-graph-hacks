# ContextOS — Evidence-first Company Brain

**Graph Hacks 2026 · WeMakeDevs × FalkorDB**

ContextOS is a graph-powered incident investigation assistant for a fictional company. It traverses a FalkorDB knowledge graph connecting incidents, services, owners, on-call engineers, runbooks, prior incidents, decisions, and persistent session memories. It explains recommendations with evidence paths. All seed data is synthetic.

## Run on Replit
1. Import the repository/ZIP with files at the project root (README, .replit, requirements.txt, streamlit_app.py).
2. Press **Run**. The run command installs dependencies and starts Streamlit on port 3000.
3. First launch seeds the graph automatically when empty. No LLM API key is required.
4. Try: “Why is checkout failing, and who should investigate?” Then ask “Have we seen a similar incident before? What did we decide?”
5. Inspect evidence paths, graph topology and persistent memory.

The app uses FalkorDBLite's embedded graph engine and Cypher queries, not a dictionary or mocked graph. Data is stored under `data/`. FalkorDBLite requires Python 3.12+.

## Run locally
```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
streamlit run streamlit_app.py
```

## Optional FalkorDB Cloud
Install `requirements-cloud.txt`, set `FALKORDB_MODE=cloud`, and provide `FALKORDB_HOST`, `FALKORDB_PORT`, `FALKORDB_USERNAME`, `FALKORDB_PASSWORD`, and `FALKORDB_SSL` as environment secrets. Never commit credentials.

## Graph model
Nodes: `Service`, `Person`, `Project`, `Incident`, `Decision`, `Document`, `Session`, `Memory`. Relationships include `DEPENDS_ON`, `OWNS`, `ON_CALL_FOR`, `AFFECTS`, `RELEVANT_RUNBOOK`, `GUIDED_BY`, `FOLLOWED_BY`, `CONTAINS`, and `CONTAINS_MEMORY`. See [docs/GRAPH_MODEL.md](docs/GRAPH_MODEL.md) and `app/graph_store.py` for the schema and Cypher.

## Tests
```bash
python -m pip install pytest
python -m pytest -q
```
Tests exercise agent composition and parameterized memory writes with a fake query interface; they do not replace live engine verification.

## Tracks
- Primary: **Track 03 — Company Brain**.
- Secondary candidate: **Track 01 — Agents That Act on Connected Data** (advisory triage only; no production actions execute).
- Do not claim Track 02 unless richer memory/coordination is implemented and demonstrated.

## AI assistance disclosure
AI assistance was used for planning, code drafting/refinement, tests, and documentation. The participant must review and understand the core graph queries, verify the app, and disclose the tools actually used. Do not misrepresent a local ZIP as a verified deployment or claim untested features.

## Demo video
Follow [docs/DEMO_SCRIPT.md](docs/DEMO_SCRIPT.md). Record only after startup and graph queries are verified.
