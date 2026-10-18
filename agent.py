from app.graph_store import investigate_incident, save_memory

def answer_question(graph, session_id, question):
    analysis=investigate_incident(graph,question)
    if not analysis.get("incident"):
        answer="I couldn't find a matching incident in FalkorDB. Try Checkout API, Payment Gateway, ownership, on-call, or runbook."
        save_memory(graph,session_id,question,answer)
        return {"answer":answer,"analysis":analysis}
    def clean(key): return [x for x in analysis.get(key,[]) if x]
    related=[x for x in clean("related_incidents") if x != analysis.get("incident")]
    answer="\n\n".join([f"**{analysis.get('incident_id')}: {analysis.get('incident')}** ({analysis.get('severity')}, {analysis.get('status')}).",f"**Affected services:** {', '.join(clean('services')) or 'No linked service found'}.",f"**Suggested owners:** {', '.join(clean('owners')) or 'No owner relationship found'}.",f"**On-call:** {', '.join(clean('on_call')) or 'No on-call relationship found'}.",f"**Runbook:** {', '.join(clean('runbooks')) or 'No runbook linked'}.",f"**Related incident history:** {', '.join(related) or 'No additional matching incident found'}.",f"**Prior decision:** {'; '.join(clean('decisions')) if clean('decisions') else 'No decision linked'}.","Advisory recommendation grounded in the synthetic graph; no production action is executed."])
    save_memory(graph,session_id,question,answer)
    return {"answer":answer,"analysis":analysis}
