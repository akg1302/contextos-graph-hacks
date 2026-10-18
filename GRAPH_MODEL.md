# ContextOS graph model

ContextOS uses FalkorDB as its primary knowledge and reasoning store. All demo records are synthetic.

## Node labels

| Label | Properties | Purpose |
|---|---|---|
| Service | name, description, tier | Technical systems and dependencies |
| Person | name, role, email | Owners and on-call engineers; emails use example.test |
| Incident | id, title, status, severity, summary | Current and historical incidents |
| Decision | id, title, rationale, date | Response policy and decision context |
| Document | id, title, kind, steps | Runbooks and operating knowledge |
| Project | name, description | Groups services into a project |
| Session | id | Persistent session identity |
| Memory | id, question, answer, created_at | Stored conversation episodes |

## Relationships
- (Service)-[:DEPENDS_ON]->(Service): service dependency.
- (Person)-[:OWNS]->(Service): accountable owner.
- (Person)-[:ON_CALL_FOR]->(Service): on-call assignment.
- (Incident)-[:AFFECTS]->(Service): incident impact.
- (Incident)-[:RELEVANT_RUNBOOK]->(Document): operational guidance.
- (Incident)-[:GUIDED_BY|FOLLOWED_BY]->(Decision): prior decisions.
- (Project)-[:CONTAINS]->(Service): project membership.
- (Session)-[:CONTAINS_MEMORY]->(Memory): persistent episodic memory.

## Core Cypher traversal
```cypher
MATCH (i:Incident)-[:AFFECTS]->(s:Service)
OPTIONAL MATCH (p:Person)-[:OWNS]->(s)
OPTIONAL MATCH (o:Person)-[:ON_CALL_FOR]->(s)
RETURN i.id, i.title, collect(DISTINCT s.name),
       collect(DISTINCT p.name), collect(DISTINCT o.name)
```

Historical incident lookup:
```cypher
MATCH (old:Incident)-[:AFFECTS]->(s:Service)<-[:AFFECTS]-(current:Incident)
WHERE current.id = $incident_id AND old.id <> current.id
RETURN old.id, old.title, s.name
```

Memory lookup:
```cypher
MATCH (s:Session)-[:CONTAINS_MEMORY]->(m:Memory)
RETURN s.id, m.question, m.answer, m.created_at
ORDER BY m.created_at DESC LIMIT $limit
```

## Why FalkorDB is central
The agent discovers owners, on-call contacts, runbooks, and decisions by traversing graph edges. Removing FalkorDB removes the persistent relationship store and reasoning substrate. This demo composes deterministic graph-grounded answers rather than claiming to use an LLM.

## Safety and limitations
Data is fictional; emails use reserved example.test domains. Recommendations are advisory and no production actions are taken. A future version could add an LLM for intent extraction while retaining graph retrieval and source-grounded answers.
