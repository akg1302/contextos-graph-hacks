from __future__ import annotations
import os, uuid
from functools import lru_cache

def _connect():
    mode = os.getenv("FALKORDB_MODE", "embedded").lower()
    name = os.getenv("FALKORDB_GRAPH", "contextos_demo")
    if mode == "cloud":
        from falkordb import FalkorDB
        kw = {"host": os.environ["FALKORDB_HOST"], "port": int(os.getenv("FALKORDB_PORT", "6379")), "ssl": os.getenv("FALKORDB_SSL", "true").lower() == "true"}
        if os.getenv("FALKORDB_USERNAME"): kw["username"] = os.environ["FALKORDB_USERNAME"]
        if os.getenv("FALKORDB_PASSWORD"): kw["password"] = os.environ["FALKORDB_PASSWORD"]
        db = FalkorDB(**kw)
    else:
        from falkordblite import FalkorDB
        path = os.getenv("FALKORDB_DATA_DIR", "data")
        os.makedirs(path, exist_ok=True)
        db = FalkorDB(path=path)
    return db.select_graph(name)

@lru_cache(maxsize=1)
def get_graph(): return _connect()

def _query(graph, cypher, params=None):
    res = graph.query(cypher, params or {})
    headers, rows = getattr(res, "header", []) or [], getattr(res, "result_set", []) or []
    names = [h[1] if isinstance(h, (list, tuple)) and len(h)>1 else str(h) for h in headers]
    return [dict(zip(names, row)) for row in rows]

def graph_overview(graph):
    return {"nodes": _query(graph, "MATCH (n) RETURN labels(n)[0] AS label, count(n) AS count ORDER BY label"), "relationships": _query(graph, "MATCH ()-[r]->() RETURN type(r) AS type, count(r) AS count ORDER BY type")}

def seed_demo_graph(graph, reset=False):
    if reset: graph.query("MATCH (n) DETACH DELETE n")
    qs = [
      "MERGE (s:Service {name:'Checkout API'}) SET s.description='Handles checkout requests', s.tier=1",
      "MERGE (s:Service {name:'Payment Gateway'}) SET s.description='Authorizes payments', s.tier=1",
      "MERGE (s:Service {name:'Inventory Service'}) SET s.description='Reserves stock', s.tier=2",
      "MERGE (p:Person {name:'Asha Mehta'}) SET p.role='Backend engineer', p.email='asha@example.test'",
      "MERGE (p:Person {name:'Rohan Singh'}) SET p.role='SRE / on-call engineer', p.email='rohan@example.test'",
      "MERGE (p:Person {name:'Mira Shah'}) SET p.role='Payments engineer', p.email='mira@example.test'",
      "MERGE (i:Incident {id:'INC-1042'}) SET i.title='Checkout failures after payment timeout', i.status='investigating', i.severity='SEV-2', i.summary='Checkout requests fail when payment authorization times out'",
      "MERGE (d:Decision {id:'DEC-208'}) SET d.title='Use bounded retries for payment timeouts', d.rationale='Retries must be bounded to avoid cascading load', d.date='2026-09-12'",
      "MERGE (r:Document {id:'RB-17'}) SET r.title='Payment timeout runbook', r.kind='runbook', r.steps='Check gateway latency; inspect timeout rate; verify retry budget; roll back recent config if needed'",
      "MERGE (old:Incident {id:'INC-0991'}) SET old.title='Payment gateway latency spike', old.status='resolved', old.severity='SEV-3'",
      "MERGE (pr:Project {name:'Commerce Platform'}) SET pr.description='Customer purchase flow'",
      "MATCH (a:Service {name:'Checkout API'}),(b:Service {name:'Payment Gateway'}) MERGE (a)-[:DEPENDS_ON]->(b)",
      "MATCH (a:Service {name:'Checkout API'}),(b:Service {name:'Inventory Service'}) MERGE (a)-[:DEPENDS_ON]->(b)",
      "MATCH (i:Incident {id:'INC-1042'}),(s:Service {name:'Checkout API'}) MERGE (i)-[:AFFECTS]->(s)",
      "MATCH (i:Incident {id:'INC-1042'}),(s:Service {name:'Payment Gateway'}) MERGE (i)-[:AFFECTS]->(s)",
      "MATCH (p:Person {name:'Asha Mehta'}),(s:Service {name:'Checkout API'}) MERGE (p)-[:OWNS]->(s)",
      "MATCH (p:Person {name:'Mira Shah'}),(s:Service {name:'Payment Gateway'}) MERGE (p)-[:OWNS]->(s)",
      "MATCH (p:Person {name:'Rohan Singh'}),(s:Service {name:'Checkout API'}) MERGE (p)-[:ON_CALL_FOR]->(s)",
      "MATCH (i:Incident {id:'INC-1042'}),(r:Document {id:'RB-17'}) MERGE (i)-[:RELEVANT_RUNBOOK]->(r)",
      "MATCH (i:Incident {id:'INC-1042'}),(d:Decision {id:'DEC-208'}) MERGE (i)-[:GUIDED_BY]->(d)",
      "MATCH (i:Incident {id:'INC-0991'}),(s:Service {name:'Payment Gateway'}) MERGE (i)-[:AFFECTS]->(s)",
      "MATCH (i:Incident {id:'INC-0991'}),(d:Decision {id:'DEC-208'}) MERGE (i)-[:FOLLOWED_BY]->(d)",
      "MATCH (p:Project {name:'Commerce Platform'}),(s:Service {name:'Checkout API'}) MERGE (p)-[:CONTAINS]->(s)",
      "MATCH (p:Project {name:'Commerce Platform'}),(s:Service {name:'Payment Gateway'}) MERGE (p)-[:CONTAINS]->(s)"
    ]
    for q in qs: graph.query(q)
    ov=graph_overview(graph)
    return {"node_types":len(ov["nodes"]),"nodes":sum(int(x["count"]) for x in ov["nodes"]),"relationship_types":len(ov["relationships"]),"relationships":sum(int(x["count"]) for x in ov["relationships"])}

def investigate_incident(graph, question):
    rows=_query(graph, """MATCH (i:Incident)-[:AFFECTS]->(s:Service)
      OPTIONAL MATCH (p:Person)-[:OWNS]->(s) OPTIONAL MATCH (o:Person)-[:ON_CALL_FOR]->(s)
      OPTIONAL MATCH (i)-[:RELEVANT_RUNBOOK]->(r:Document)
      OPTIONAL MATCH (i)-[:GUIDED_BY|FOLLOWED_BY]->(d:Decision)
      OPTIONAL MATCH (old:Incident)-[:AFFECTS]->(s)
      RETURN i.id AS incident_id, i.title AS incident, i.status AS status, i.severity AS severity,
      collect(DISTINCT s.name) AS services, collect(DISTINCT p.name) AS owners,
      collect(DISTINCT o.name) AS on_call, collect(DISTINCT r.title) AS runbooks,
      collect(DISTINCT d.title) AS decisions, collect(DISTINCT old.title) AS related_incidents ORDER BY severity""")
    if not rows: return {"incident":None,"services":[],"owners":[],"on_call":[],"runbooks":[],"decisions":[],"evidence":[]}
    q=question.lower(); row=next((r for r in rows if any(w in q for w in ["checkout","payment","timeout","incident","failing","failure"])),rows[0])
    evidence=[{"path":f"({row['incident_id']})-[:AFFECTS]->(Service)","why":"Connects the incident to affected services."},{"path":"(Person)-[:OWNS]->(Service)","why":"Finds accountable service owners."},{"path":"(Person)-[:ON_CALL_FOR]->(Service)","why":"Finds the on-call contact."},{"path":f"({row['incident_id']})-[:RELEVANT_RUNBOOK|GUIDED_BY]->(Document|Decision)","why":"Retrieves runbook and prior decision context."}]
    return {**row,"evidence":evidence}

def save_memory(graph, session_id, question, answer):
    graph.query("""MERGE (s:Session {id:$session_id}) CREATE (m:Memory {id:$memory_id, question:$question, answer:$answer, created_at:datetime()}) MERGE (s)-[:CONTAINS_MEMORY]->(m) MERGE (m)-[:ABOUT]->(s)""", {"session_id":session_id,"memory_id":uuid.uuid4().hex,"question":question,"answer":answer})

def recent_memories(graph, limit=10):
    return _query(graph,"""MATCH (s:Session)-[:CONTAINS_MEMORY]->(m:Memory) RETURN m.question AS question, m.answer AS answer, s.id AS session, toString(m.created_at) AS created_at ORDER BY m.created_at DESC LIMIT $limit""",{"limit":int(limit)})
