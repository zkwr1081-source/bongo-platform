"""Arabic local dashboard for the BONGO discovery MVP."""
from __future__ import annotations
import html
import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from .discovery_engine import DiscoveryStore

DB_PATH = os.environ.get("BONGO_DISCOVERY_DB", "bongo_discovery.sqlite3")
store = DiscoveryStore(DB_PATH)
app = FastAPI(title="BONGO | محرك اكتشاف الاحتياجات")

class EvidenceIn(BaseModel):
    title: str
    source_name: str
    source_url: str
    excerpt: str
    domain: str
    claim_type: str
    geography: str
    license: str = "unspecified"
    published_at: str = "unknown"

class OpportunityIn(BaseModel):
    title: str
    problem: str
    proposal: str
    evidence_ids: list[int] = []
    scores: dict[str, float]

@app.get("/api/health")
def health():
    return {"status":"ok","evidence_count":store.count(),"mode":"local-first"}

@app.get("/api/evidence")
def evidence():
    return store.list_evidence()

@app.post("/api/evidence")
def add_evidence(item: EvidenceIn):
    try:
        record_id, created = store.add_evidence(item.model_dump())
        return {"id":record_id,"created":created}
    except ValueError as exc:
        raise HTTPException(422, str(exc))

@app.get("/api/opportunities")
def opportunities():
    return store.list_opportunities()

@app.post("/api/opportunities")
def add_opportunity(item: OpportunityIn):
    try:
        return {"id":store.add_opportunity(item.model_dump())}
    except ValueError as exc:
        raise HTTPException(422, str(exc))

@app.get("/", response_class=HTMLResponse)
def dashboard():
    evidence_rows = store.list_evidence()
    ideas = store.list_opportunities()
    idea_cards = "".join(
        f'<article class="card"><b>{html.escape(x["title"])}</b><p>{html.escape(x["problem"])}</p>'
        f'<small>النتيجة: {x["total_score"]}/5 · الثقة: {html.escape(x["confidence"])}</small></article>'
        for x in ideas) or '<p class="muted">لا توجد فرص بعد. أضف فرصة من نموذج API أو استورد بيانات JSON.</p>'
    evidence_cards = "".join(
        f'<article class="card"><b>{html.escape(x["title"])}</b><p>{html.escape(x["excerpt"][:260])}</p>'
        f'<small>{html.escape(x["source_name"])} · {html.escape(x["domain"])} · '
        f'<a href="{html.escape(x["source_url"], quote=True)}" target="_blank" rel="noopener">المصدر</a></small></article>'
        for x in evidence_rows) or '<p class="muted">قاعدة الأدلة فارغة. ابدأ بإضافة أدلة موثقة.</p>'
    return f"""<!doctype html><html lang="ar" dir="rtl"><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>BONGO Discovery</title>
<style>
:root{{--bg:#0b1220;--panel:#121e31;--line:#26364e;--ink:#edf4ff;--muted:#9fb0c7;--accent:#70d6c2}}
*{{box-sizing:border-box}}body{{margin:0;background:linear-gradient(140deg,#0b1220,#13243a);color:var(--ink);font:16px system-ui,sans-serif}}
main{{max-width:1050px;margin:auto;padding:28px 18px}}header{{padding:26px 0 18px}}h1{{font-size:clamp(28px,5vw,44px);margin:0 0 8px}}h2{{margin-top:30px}}
p{{line-height:1.8}}.muted,small{{color:var(--muted)}}.stats{{display:flex;gap:12px;flex-wrap:wrap}}
.stat,.card{{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:16px}}
.stat{{min-width:150px;flex:1}}.stat strong{{display:block;font-size:28px;color:var(--accent)}}
.grid{{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}}
.card p{{margin:8px 0}}a{{color:var(--accent)}}.tag{{display:inline-block;border:1px solid var(--line);border-radius:99px;padding:5px 10px;color:var(--accent)}}footer{{margin:34px 0;color:var(--muted);font-size:13px}}
</style><main><header><span class="tag">نسخة محلية أولية · MVP</span><h1>BONGO | مختبر اكتشاف الاحتياجات</h1>
<p>حوّل الإشارات والمصادر إلى أدلة قابلة للمراجعة، ثم رتّب فرص الحلول. لا يوجد اتصال تلقائي بمصادر خارجية في هذه النسخة، ولا تُعد الدرجات إثباتاً للجدوى.</p></header>
<section class="stats"><div class="stat"><strong>{len(evidence_rows)}</strong>دليل محفوظ محلياً</div><div class="stat"><strong>{len(ideas)}</strong>فرصة مسجلة</div><div class="stat"><strong>SQLite</strong>تخزين محلي</div></section>
<h2>فرص المشاريع</h2><section class="grid">{idea_cards}</section>
<h2>سجل الأدلة</h2><section class="grid">{evidence_cards}</section>
<footer>BONGO Discovery MVP · واجهة عربية · <a href="/docs">توثيق API</a> · البيانات في ملف SQLite محلي</footer></main></html>"""
