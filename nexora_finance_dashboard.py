"""Local control dashboard for the NEXORA Finance Observer.

Read-only market telemetry with explicit start/stop controls. It does not trade,
send payments, create repositories, or execute shell commands.
"""
from __future__ import annotations

import asyncio
import hmac
import ipaddress
import logging
import os
import sqlite3
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import Depends, FastAPI, Header, HTTPException, Query
from fastapi.responses import HTMLResponse

from nexora_finance_observer import (
    DB_PATH,
    FinanceStore,
    NexoraFinanceObserver,
    Settings,
)

LOG = logging.getLogger("nexora.finance_dashboard")
TOKEN = os.getenv("NEXORA_DASHBOARD_TOKEN", "").strip()
HOST = os.getenv("NEXORA_DASHBOARD_HOST", "127.0.0.1").strip()
PORT = int(os.getenv("NEXORA_DASHBOARD_PORT", "8094"))
AUTO_START = os.getenv("NEXORA_AUTO_START", "0").strip().lower() in {"1", "true", "yes", "on"}

HTML = r"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#07111f">
<title>NEXORA | Finance Control</title>
<style>
:root{color-scheme:dark;--bg:#07111f;--panel:#101e31;--line:#20354e;--muted:#91a6bd;--text:#edf6ff;--cyan:#35c5ed;--green:#45d6a0;--red:#ff7185;--amber:#f4c66a}
*{box-sizing:border-box}
body{margin:0;background:radial-gradient(circle at 80% -10%,#123d5a 0,transparent 38%),var(--bg);color:var(--text);font-family:system-ui,-apple-system,"Segoe UI",Tahoma,Arial,sans-serif}
main{width:min(1180px,94%);margin:0 auto;padding:26px 0 54px}
header{display:flex;align-items:center;justify-content:space-between;gap:16px;flex-wrap:wrap;padding:22px 24px;border:1px solid var(--line);border-radius:20px;background:#0c1a2bdd;box-shadow:0 18px 60px #0005}
.brand{font-size:clamp(23px,4vw,34px);font-weight:900;letter-spacing:.08em}
.brand span{color:var(--cyan)}
.sub{color:var(--muted);font-size:13px;margin-top:5px}
.pill{display:inline-flex;align-items:center;gap:8px;padding:8px 13px;border-radius:999px;background:#142b3e;border:1px solid var(--line);font-size:12px}
.dot{width:8px;height:8px;border-radius:50%;background:var(--amber);box-shadow:0 0 12px currentColor}
.dot.on{background:var(--green)}
.controls{display:flex;gap:9px;align-items:center;flex-wrap:wrap;margin:18px 0}
input{min-width:190px;flex:1;background:#081524;border:1px solid var(--line);border-radius:10px;padding:11px 13px;color:var(--text)}
button{border:1px solid transparent;border-radius:10px;padding:11px 15px;color:#04131d;background:var(--cyan);font-weight:800;cursor:pointer}
button.secondary{background:#183047;color:var(--text);border-color:var(--line)}
button.danger{background:#4b2634;color:#ffdce3;border-color:#713447}
button:disabled{opacity:.45;cursor:not-allowed}
.grid{display:grid;grid-template-columns:repeat(4,minmax(0,1fr));gap:13px}
.card{background:linear-gradient(145deg,#12243a,#0c192a);border:1px solid var(--line);border-radius:16px;padding:17px;min-width:0}
.label{color:var(--muted);font-size:12px}
.value{font-size:clamp(20px,3vw,29px);font-weight:850;margin-top:8px;overflow-wrap:anywhere}
.note{color:var(--muted);font-size:11px;margin-top:6px}
.section{margin-top:18px}
.section h2{font-size:17px;margin:0 0 12px}
.panel{background:#0d1a2b;border:1px solid var(--line);border-radius:16px;padding:17px;overflow:hidden}
.table-wrap{overflow-x:auto}
table{width:100%;border-collapse:collapse;min-width:600px;font-size:13px}
th,td{text-align:right;padding:11px 10px;border-bottom:1px solid #1d3045;white-space:nowrap}
th{color:var(--muted);font-weight:650}
.signal{display:inline-block;padding:5px 9px;border-radius:999px;background:#17384a;color:#8ee6fa;font-size:11px}
.signal.negative{background:#452535;color:#ffb4c1}
.signal.positive{background:#173d35;color:#8ceac4}
.muted{color:var(--muted)}
#message{min-height:22px;color:var(--muted);font-size:12px;margin:8px 2px}
footer{text-align:center;color:#71869d;font-size:11px;padding:28px 0 0}
@media(max-width:820px){.grid{grid-template-columns:repeat(2,minmax(0,1fr))}}
@media(max-width:480px){main{width:92%;padding-top:14px}.grid{grid-template-columns:1fr 1fr}.card{padding:13px}header{padding:17px}.controls input{flex-basis:100%}.controls button{flex:1}}
</style>
</head>
<body>
<main>
<header>
  <div>
    <div class="brand">NEXORA <span>FINANCE</span></div>
    <div class="sub">مركز مراقبة البيانات المالية — قراءة فقط، بلا تداول أو تحويل أموال</div>
  </div>
  <div class="pill"><i class="dot" id="stateDot"></i><span id="engineState">جارٍ التحقق...</span></div>
</header>

<div class="controls">
  <input id="accessToken" type="password" autocomplete="off" placeholder="رمز لوحة التحكم (اتركه فارغاً محلياً)">
  <button class="secondary" onclick="applyToken()">تطبيق الرمز</button>
  <button onclick="action('/api/observer/start','بدء المراقب')">▶ تشغيل</button>
  <button class="danger" onclick="action('/api/observer/stop','إيقاف المراقب')">■ إيقاف</button>
  <button class="secondary" onclick="action('/api/observer/once','جمع قراءة واحدة')">↻ قراءة الآن</button>
  <button class="secondary" onclick="refreshAll()">تحديث</button>
</div>
<div id="message">لا توجد أوامر مالية في هذه اللوحة. زر القراءة يجلب بيانات عامة فقط.</div>

<section class="grid">
  <article class="card"><div class="label">آخر إشارة مرصودة</div><div class="value" id="signal">—</div><div class="note">وصف لحركة 24 ساعة، وليس تنبؤاً</div></article>
  <article class="card"><div class="label">تغير القيمة السوقية خلال 24 ساعة</div><div class="value" id="change">—</div><div class="note">المصدر: CoinGecko Global</div></article>
  <article class="card"><div class="label">عدد القراءات المحفوظة</div><div class="value" id="observations">0</div><div class="note">سجلات SQLite المحلية</div></article>
  <article class="card"><div class="label">سجلات الوكلاء</div><div class="value" id="agents">0</div><div class="note">سجلات تشغيل مسجلة، لا تعني وكلاء نشطين</div></article>
</section>

<section class="section panel">
  <h2>حالة التشغيل</h2>
  <div class="table-wrap"><table><tbody>
    <tr><th>قاعدة البيانات</th><td id="databaseState">—</td></tr>
    <tr><th>فترة الجمع</th><td id="pollInterval">—</td></tr>
    <tr><th>حد إعداد العمال</th><td id="workerLimit">—</td></tr>
    <tr><th>آخر تحديث</th><td id="lastUpdated">—</td></tr>
    <tr><th>سجلات التوزيع المحاسبي</th><td id="allocations">0</td></tr>
  </tbody></table></div>
</section>

<section class="section panel">
  <h2>آخر قراءات السوق</h2>
  <div class="table-wrap"><table>
    <thead><tr><th>الوقت UTC</th><th>التغير 24h</th><th>الإشارة المرصودة</th><th>القيمة السوقية USD</th><th>الحجم 24h USD</th></tr></thead>
    <tbody id="observationsRows"><tr><td colspan="5" class="muted">لا توجد قراءات بعد.</td></tr></tbody>
  </table></div>
</section>

<section class="section panel">
  <h2>سجل التوزيعات المحاسبية</h2>
  <div class="note">عرض فقط. الحالة RECORDED_NOT_PAID تعني أن السجل محاسبي ولم يتم دفع أي مبلغ.</div>
  <div class="table-wrap"><table>
    <thead><tr><th>التاريخ</th><th>الإجمالي USD</th><th>إعادة استثمار 5%</th><th>المستفيد 95%</th><th>الحالة</th></tr></thead>
    <tbody id="revenueRows"><tr><td colspan="5" class="muted">لا توجد سجلات.</td></tr></tbody>
  </table></div>
</section>
<footer>NEXORA Finance Observer · Local control interface · No trading · No transfers</footer>
</main>
<script>
let bearerToken = "";
const el = (id) => document.getElementById(id);
function money(value){if(value===null||value===undefined)return "—";return new Intl.NumberFormat("en-US",{style:"currency",currency:"USD",maximumFractionDigits:0}).format(value);}
function cell(row,value){const td=document.createElement("td");td.textContent=value===null||value===undefined?"—":String(value);row.appendChild(td);}
function applyToken(){bearerToken=el("accessToken").value.trim();refreshAll();}
async function api(path,options){
  const headers=Object.assign({},options&&options.headers?options.headers:{});
  if(bearerToken)headers.Authorization="Bearer "+bearerToken;
  const response=await fetch(path,Object.assign({},options||{},{headers}));
  const data=await response.json().catch(()=>({detail:"استجابة غير صالحة"}));
  if(!response.ok)throw new Error(data.detail||("HTTP "+response.status));
  return data;
}
function drawObservations(items){
  const body=el("observationsRows");body.replaceChildren();
  if(!items.length){const r=body.insertRow();cell(r,"لا توجد قراءات بعد.");return;}
  items.forEach(item=>{
    const r=body.insertRow();cell(r,item.observed_at);cell(r,(Number(item.market_cap_change_24h_pct)||0).toFixed(3)+"%");
    const td=document.createElement("td");const badge=document.createElement("span");
    badge.className="signal "+(item.observed_signal==="NEGATIVE_MOMENTUM"?"negative":item.observed_signal==="POSITIVE_MOMENTUM"?"positive":"");
    badge.textContent=item.observed_signal;td.appendChild(badge);r.appendChild(td);
    cell(r,money(item.total_market_cap_usd));cell(r,money(item.total_volume_24h_usd));
  });
}
function drawRevenue(items){
  const body=el("revenueRows");body.replaceChildren();
  if(!items.length){const r=body.insertRow();cell(r,"لا توجد سجلات.");return;}
  items.forEach(item=>{const r=body.insertRow();cell(r,item.recorded_at);cell(r,money(item.gross_verified_revenue_usd));cell(r,money(item.reinvestment_5pct_usd));cell(r,money(item.beneficiary_95pct_usd));cell(r,item.status);});
}
async function refreshAll(){
  try{
    const [s,o,v]=await Promise.all([api("/api/status"),api("/api/observations?limit=20"),api("/api/revenue-allocations?limit=20")]);
    const running=s.observer_state==="RUNNING";
    el("engineState").textContent=running?"المراقب يعمل":"المراقب متوقف";
    el("stateDot").className="dot"+(running?" on":"");
    el("signal").textContent=s.latest_observation?s.latest_observation.observed_signal:"—";
    el("change").textContent=s.latest_observation?Number(s.latest_observation.market_cap_change_24h_pct).toFixed(3)+"%":"—";
    el("observations").textContent=s.observations_count;
    el("agents").textContent=s.agent_records_count;
    el("databaseState").textContent=s.database_state;
    el("pollInterval").textContent=s.poll_seconds+" ثانية";
    el("workerLimit").textContent=s.worker_setting+" (إعداد محدود، وليس عدداً لوكلاء نشطين)";
    el("lastUpdated").textContent=new Date().toLocaleString();
    el("allocations").textContent=s.revenue_records_count;
    drawObservations(o.items||[]);drawRevenue(v.items||[]);
    el("message").textContent="تم تحديث البيانات.";
  }catch(error){el("message").textContent="تعذر تحديث اللوحة: "+error.message;}
}
async function action(path,label){
  el("message").textContent=label+"...";
  try{
    const data=await api(path,{method:"POST"});
    el("message").textContent=data.message||("الحالة: "+data.status);
    await refreshAll();
  }catch(error){el("message").textContent="لم يكتمل الأمر: "+error.message;}
}
refreshAll();setInterval(refreshAll,10000);
</script>
</body>
</html>"""


def _rows(store: FinanceStore, table: str, limit: int) -> list[dict[str, Any]]:
    allowed = {
        "market_observations": "id, observed_at, market_cap_change_24h_pct, observed_signal, total_market_cap_usd, total_volume_24h_usd, source",
        "agent_metrics": "agent_id, tasks_completed, status, last_updated",
        "revenue_allocations": "id, gross_verified_revenue_usd, reinvestment_5pct_usd, beneficiary_95pct_usd, status, recorded_at",
    }
    if table not in allowed:
        raise ValueError("Unsupported table")
    order = "id DESC" if table != "agent_metrics" else "last_updated DESC"
    with sqlite3.connect(store.path) as db:
        db.row_factory = sqlite3.Row
        records = db.execute(
            "SELECT " + allowed[table] + " FROM " + table + " ORDER BY " + order + " LIMIT ?",
            (limit,),
        ).fetchall()
    return [dict(record) for record in records]


def _summary(store: FinanceStore, settings: Settings, state: dict[str, Any]) -> dict[str, Any]:
    with sqlite3.connect(store.path) as db:
        db.row_factory = sqlite3.Row
        observations = db.execute("SELECT COUNT(*) FROM market_observations").fetchone()[0]
        agents = db.execute("SELECT COUNT(*) FROM agent_metrics").fetchone()[0]
        revenue = db.execute("SELECT COUNT(*) FROM revenue_allocations").fetchone()[0]
        latest = db.execute(
            """SELECT observed_at, market_cap_change_24h_pct, observed_signal,
                      total_market_cap_usd, total_volume_24h_usd, source
               FROM market_observations ORDER BY id DESC LIMIT 1"""
        ).fetchone()
    task = state.get("task")
    running = bool(task and not task.done())
    return {
        "status": "ok",
        "observer_state": "RUNNING" if running else "STOPPED",
        "database_state": "READY",
        "database_file": str(store.path),
        "observations_count": observations,
        "agent_records_count": agents,
        "revenue_records_count": revenue,
        "poll_seconds": settings.poll_seconds,
        "worker_setting": settings.workers,
        "latest_observation": dict(latest) if latest else None,
        "is_forecast": False,
        "financial_actions_enabled": False,
    }


def create_app(
    store: FinanceStore | None = None,
    settings: Settings | None = None,
    token: str | None = None,
    auto_start: bool | None = None,
) -> FastAPI:
    active_store = store or FinanceStore(DB_PATH)
    active_settings = settings or Settings.from_env()
    access_token = TOKEN if token is None else token
    should_auto_start = AUTO_START if auto_start is None else auto_start
    state: dict[str, Any] = {"observer": None, "task": None, "lock": asyncio.Lock()}

    async def authorize(authorization: str | None = Header(default=None)) -> None:
        if access_token and not hmac.compare_digest(authorization or "", "Bearer " + access_token):
            raise HTTPException(status_code=401, detail="رمز الوصول غير صحيح أو غير موجود.")

    async def start_observer() -> dict[str, str]:
        async with state["lock"]:
            current = state.get("task")
            if current and not current.done():
                return {"status": "RUNNING", "message": "المراقب يعمل بالفعل."}
            observer = NexoraFinanceObserver(active_store, active_settings)
            task = asyncio.create_task(observer.run(), name="nexora-finance-observer")
            state["observer"] = observer
            state["task"] = task
            return {"status": "STARTING", "message": "تم إرسال إشارة التشغيل للمراقب."}

    async def stop_observer() -> dict[str, str]:
        async with state["lock"]:
            observer = state.get("observer")
            task = state.get("task")
            if not observer or not task or task.done():
                return {"status": "STOPPED", "message": "المراقب متوقف بالفعل."}
            observer.stop()
        try:
            await asyncio.wait_for(asyncio.shield(task), timeout=10)
        except asyncio.TimeoutError:
            return {"status": "STOPPING", "message": "وصلت إشارة الإيقاف؛ ينتظر انتهاء طلب البيانات الحالي."}
        finally:
            if task.done():
                state["observer"] = None
                state["task"] = None
        return {"status": "STOPPED", "message": "تم إيقاف المراقب."}

    @asynccontextmanager
    async def lifespan(_: FastAPI):
        active_store.initialize()
        if should_auto_start:
            await start_observer()
        try:
            yield
        finally:
            await stop_observer()

    app = FastAPI(
        title="NEXORA Finance Control",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=lifespan,
    )

    @app.get("/", response_class=HTMLResponse)
    async def dashboard() -> HTMLResponse:
        return HTMLResponse(HTML)

    @app.get("/healthz")
    async def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/api/status", dependencies=[Depends(authorize)])
    async def status() -> dict[str, Any]:
        return _summary(active_store, active_settings, state)

    @app.get("/api/observations", dependencies=[Depends(authorize)])
    async def observations(limit: int = Query(default=50, ge=1, le=200)) -> dict[str, Any]:
        return {"items": _rows(active_store, "market_observations", limit)}

    @app.get("/api/agents", dependencies=[Depends(authorize)])
    async def agents(limit: int = Query(default=50, ge=1, le=200)) -> dict[str, Any]:
        return {"items": _rows(active_store, "agent_metrics", limit)}

    @app.get("/api/revenue-allocations", dependencies=[Depends(authorize)])
    async def revenue_allocations(limit: int = Query(default=50, ge=1, le=200)) -> dict[str, Any]:
        return {"items": _rows(active_store, "revenue_allocations", limit)}

    @app.post("/api/observer/start", dependencies=[Depends(authorize)])
    async def observer_start() -> dict[str, str]:
        return await start_observer()

    @app.post("/api/observer/stop", dependencies=[Depends(authorize)])
    async def observer_stop() -> dict[str, str]:
        return await stop_observer()

    @app.post("/api/observer/once", dependencies=[Depends(authorize)])
    async def observer_once() -> dict[str, Any]:
        current = state.get("task")
        if current and not current.done():
            raise HTTPException(status_code=409, detail="أوقف المراقب قبل تنفيذ قراءة يدوية منفردة.")
        try:
            observer = NexoraFinanceObserver(active_store, active_settings)
            snapshot = await observer.observe_once()
            return {"status": "OBSERVED", "snapshot": snapshot}
        except Exception:
            LOG.exception("Manual market observation failed")
            raise HTTPException(status_code=502, detail="تعذر جلب بيانات السوق. لم يتم تنفيذ أي إجراء مالي.")

    return app


app = create_app()


def _validate_bind(host: str, token: str) -> None:
    if host == "localhost":
        return
    try:
        loopback = ipaddress.ip_address(host).is_loopback
    except ValueError:
        loopback = False
    if not loopback and len(token) < 24:
        raise SystemExit(
            "Refusing non-local bind: set NEXORA_DASHBOARD_TOKEN to a random value of at least 24 characters."
        )


if __name__ == "__main__":
    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO"),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    _validate_bind(HOST, TOKEN)
    uvicorn.run(app, host=HOST, port=PORT, log_level=os.getenv("LOG_LEVEL", "info").lower())
