from app.agent import answer_question

class Result:
    header=[[0,"incident_id"],[1,"incident"],[2,"status"],[3,"severity"],[4,"services"],[5,"owners"],[6,"on_call"],[7,"runbooks"],[8,"decisions"],[9,"related_incidents"]]
    result_set=[["INC-1042","Checkout failures after payment timeout","investigating","SEV-2",["Checkout API","Payment Gateway"],["Asha Mehta","Mira Shah"],["Rohan Singh"],["Payment timeout runbook"],["Use bounded retries"],["Payment gateway latency spike"]]]
class FakeGraph:
    def __init__(self): self.calls=[]
    def query(self,cypher,params=None): self.calls.append((cypher,params or {})); return Result()
def test_agent_answers_and_persists_memory():
    g=FakeGraph(); out=answer_question(g,"session-1","Why is checkout failing?")
    assert "INC-1042" in out["answer"] and "Asha Mehta" in out["answer"]
    assert out["analysis"]["evidence"] and any("CREATE (m:Memory" in q for q,_ in g.calls)
def test_memory_uses_parameters():
    g=FakeGraph(); answer_question(g,"session-1","checkout")
    params=next(p for q,p in g.calls if "CREATE (m:Memory" in q)
    assert params["session_id"]=="session-1" and params["question"]=="checkout"
