#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import urllib.request

HOST = "127.0.0.1"
PORT = 8080
CORE = "http://127.0.0.1:8091"

HTML = r'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#050816">
<title>NEXORA OMNI — Command Center</title>

<style>
*{box-sizing:border-box}
:root{
 --bg:#050816;
 --panel:#0a1020;
 --panel2:#0d1629;
 --line:#1c2a42;
 --cyan:#67e8f9;
 --blue:#818cf8;
 --green:#86efac;
 --text:#f8fafc;
 --muted:#8ea0b9;
 --danger:#fca5a5;
}
body{
 margin:0;
 background:var(--bg);
 color:var(--text);
 font-family:system-ui,-apple-system,"Segoe UI",sans-serif;
}
button,input,textarea{font:inherit}
button{cursor:pointer}
.app{
 min-height:100vh;
 background:
 radial-gradient(circle at 50% -15%,#172554 0,transparent 38%),
 radial-gradient(circle at 100% 50%,#0c1b38 0,transparent 28%),
 var(--bg);
}
.top{
 height:70px;
 display:flex;
 align-items:center;
 justify-content:space-between;
 padding:0 22px;
 border-bottom:1px solid var(--line);
 background:#070c18ee;
 backdrop-filter:blur(20px);
 position:sticky;
 top:0;
 z-index:50;
}
.logo{
 font-size:23px;
 font-weight:950;
 letter-spacing:.5px;
}
.logo span{color:var(--cyan)}
.live{
 display:flex;
 align-items:center;
 gap:8px;
 padding:8px 13px;
 border-radius:99px;
 border:1px solid #14532d;
 background:#052e1a;
 color:var(--green);
 font-size:12px;
 font-weight:800;
}
.dot{
 width:7px;
 height:7px;
 border-radius:50%;
 background:#4ade80;
 box-shadow:0 0 12px #4ade80;
}
.shell{
 max-width:1400px;
 margin:auto;
 padding:18px;
 display:grid;
 grid-template-columns:230px 1fr;
 gap:18px;
}
.sidebar{
 background:#080e1b;
 border:1px solid var(--line);
 border-radius:22px;
 padding:12px;
 height:max-content;
 position:sticky;
 top:88px;
}
.navtitle{
 color:#52637b;
 font-size:11px;
 font-weight:900;
 padding:12px;
}
.nav{
 width:100%;
 border:1px solid transparent;
 background:transparent;
 color:#aab8ca;
 padding:12px;
 border-radius:13px;
 text-align:right;
 margin-bottom:4px;
}
.nav:hover{
 background:#101a2c;
 color:#fff;
}
.nav.active{
 background:linear-gradient(90deg,#0e2534,#101b36);
 border-color:#164e63;
 color:var(--cyan);
}
.main{min-width:0}
.hero{
 padding:20px 8px 24px;
}
.eyebrow{
 color:var(--cyan);
 font-size:11px;
 font-weight:900;
 letter-spacing:1.5px;
}
h1{
 margin:9px 0;
 font-size:clamp(38px,6vw,70px);
 line-height:1;
}
.hero p{
 margin:0;
 max-width:720px;
 color:var(--muted);
 line-height:1.8;
}
.command{
 background:linear-gradient(145deg,#0c1526,#080e1b);
 border:1px solid #263650;
 border-radius:25px;
 padding:18px;
 box-shadow:0 25px 90px #0009;
}
.command-top{
 display:flex;
 align-items:center;
 justify-content:space-between;
 margin-bottom:12px;
}
.command-title{
 font-weight:900;
}
.command-state{
 color:#64748b;
 font-size:11px;
}
textarea{
 width:100%;
 min-height:155px;
 resize:vertical;
 background:#050a14;
 color:#fff;
 border:1px solid #1d2b43;
 outline:none;
 border-radius:18px;
 padding:17px;
 line-height:1.8;
}
textarea:focus{border-color:#22d3ee}
.command-actions{
 display:flex;
 gap:10px;
 margin-top:12px;
}
.btn{
 border:0;
 border-radius:14px;
 padding:13px 18px;
 font-weight:900;
}
.primary{
 flex:1;
 background:linear-gradient(90deg,#22d3ee,#818cf8);
 color:#061018;
}
.secondary{
 background:#111827;
 color:#cbd5e1;
 border:1px solid #263247;
}
.result{
 margin-top:14px;
}
.resultbox{
 background:#050a14;
 border:1px solid #164e63;
 border-radius:18px;
 padding:16px;
}
.result-grid{
 display:grid;
 grid-template-columns:repeat(4,1fr);
 gap:8px;
 margin-bottom:14px;
}
.metric{
 background:#0b1424;
 border:1px solid #17253a;
 border-radius:13px;
 padding:12px;
}
.metric small{
 color:#71839d;
 display:block;
 font-size:10px;
 margin-bottom:5px;
}
.metric strong{
 color:var(--cyan);
 font-size:13px;
}
.answer{
 padding:14px;
 border-radius:14px;
 background:#0b1424;
 color:#dbeafe;
 line-height:1.8;
 border:1px solid #17253a;
}
.dashboard{
 display:grid;
 grid-template-columns:repeat(4,1fr);
 gap:12px;
 margin-top:15px;
}
.stat{
 background:var(--panel);
 border:1px solid var(--line);
 border-radius:18px;
 padding:16px;
}
.stat-icon{font-size:21px}
.stat-name{
 color:#71839d;
 font-size:11px;
 margin-top:7px;
}
.stat-value{
 font-size:20px;
 font-weight:900;
 margin-top:3px;
}
.page{display:none}
.page.active{display:block}
.panel{
 background:var(--panel);
 border:1px solid var(--line);
 border-radius:20px;
 padding:18px;
 margin-top:15px;
}
.panel-head{
 display:flex;
 align-items:center;
 justify-content:space-between;
 margin-bottom:15px;
}
.panel-head h2{
 margin:0;
 font-size:17px;
}
.badge{
 color:var(--cyan);
 background:#08202c;
 border:1px solid #164e63;
 padding:5px 9px;
 border-radius:99px;
 font-size:10px;
}
.cards{
 display:grid;
 grid-template-columns:repeat(auto-fit,minmax(190px,1fr));
 gap:12px;
}
.card{
 background:var(--panel2);
 border:1px solid var(--line);
 border-radius:17px;
 padding:17px;
}
.card:hover{
 border-color:#31506e;
 transform:translateY(-1px);
}
.card-icon{font-size:25px}
.card h3{margin:8px 0 5px}
.card p{
 color:var(--muted);
 font-size:12px;
 line-height:1.7;
 margin:0;
}
pre{
 white-space:pre-wrap;
 word-break:break-word;
 color:#cbd5e1;
 font-size:12px;
 margin:0;
}
table{
 width:100%;
 border-collapse:collapse;
 font-size:12px;
}
th,td{
 padding:11px;
 border-bottom:1px solid #172033;
 text-align:right;
}
th{color:var(--cyan)}
.loading{color:var(--cyan)}
.error{
 color:var(--danger);
 background:#2a0b0b;
 border:1px solid #7f1d1d;
 border-radius:13px;
 padding:12px;
}
.footer{
 color:#4f6078;
 text-align:center;
 font-size:11px;
 padding:35px 0 10px;
}
.mobile-nav{
 display:none;
}
@media(max-width:900px){
 .shell{grid-template-columns:1fr}
 .sidebar{display:none}
 .mobile-nav{
  display:flex;
  overflow:auto;
  gap:6px;
  margin-bottom:12px;
 }
 .mobile-nav .nav{min-width:max-content}
 .dashboard{grid-template-columns:repeat(2,1fr)}
 .result-grid{grid-template-columns:repeat(2,1fr)}
}
@media(max-width:560px){
 .top{padding:0 12px}
 .shell{padding:10px}
 .dashboard{grid-template-columns:1fr 1fr}
 .command-actions{flex-direction:column}
 .hero{padding-top:12px}
}
</style>
</head>

<body>
<div class="app">

<header class="top">
 <div class="logo">NEXORA <span>OMNI</span></div>
 <div id="live" class="live">
  <span class="dot"></span>
  <span>جاري الاتصال...</span>
 </div>
</header>

<div class="shell">

<aside class="sidebar">

<div class="navtitle">COMMAND CENTER</div>

<button class="nav active" onclick="page('home',this)">⌂ الرئيسية</button>
<button class="nav" onclick="page('tasks',this)">◫ المهام</button>
<button class="nav" onclick="page('agents',this)">◈ الوكلاء</button>
<button class="nav" onclick="page('memory',this)">◉ الذاكرة</button>
<button class="nav" onclick="page('events',this)">◌ الأحداث</button>
<button class="nav" onclick="page('system',this)">⚙ النظام</button>

<div class="navtitle">NEXORA CORE</div>

<button class="nav" onclick="refreshAll()">↻ تحديث المنظومة</button>

</aside>

<main class="main">

<div class="mobile-nav">
<button class="nav active" onclick="page('home',this)">الرئيسية</button>
<button class="nav" onclick="page('tasks',this)">المهام</button>
<button class="nav" onclick="page('agents',this)">الوكلاء</button>
<button class="nav" onclick="page('memory',this)">الذاكرة</button>
<button class="nav" onclick="page('events',this)">الأحداث</button>
<button class="nav" onclick="page('system',this)">النظام</button>
</div>

<section id="home" class="page active">

<div class="hero">
 <div class="eyebrow">INTELLIGENCE • AUTOMATION • RESULTS</div>
 <h1>من المشكلة<br><span style="color:var(--cyan)">إلى النتيجة.</span></h1>
 <p>
 مركز القيادة الحقيقي لـ NEXORA.
 أرسل الهدف، راقب التحليل، تابع الوكلاء والتنفيذ والتحقق، ثم احتفظ بالنتيجة في الذاكرة.
 </p>
</div>

<div class="command">

<div class="command-top">
 <div class="command-title">🧠 NEXORA COMMAND</div>
 <div id="commandState" class="command-state">جاهز</div>
</div>

<textarea id="prompt"
placeholder="اكتب ما تريد من NEXORA...&#10;&#10;مثال: حلل المشروع، حدد الملفات المهمة، ثم اقترح الخطوة التالية."></textarea>

<div class="command-actions">
 <button class="btn primary" onclick="sendTask()">🧠 تشغيل NEXORA</button>
 <button class="btn secondary" onclick="clearPrompt()">مسح</button>
</div>

<div id="result" class="result"></div>

</div>

<div class="dashboard">

<div class="stat">
 <div class="stat-icon">⚡</div>
 <div class="stat-name">CORE</div>
 <div id="coreStat" class="stat-value">—</div>
</div>

<div class="stat">
 <div class="stat-icon">🤖</div>
 <div class="stat-name">AGENTS</div>
 <div id="agentStat" class="stat-value">—</div>
</div>

<div class="stat">
 <div class="stat-icon">📋</div>
 <div class="stat-name">TASKS</div>
 <div id="taskStat" class="stat-value">—</div>
</div>

<div class="stat">
 <div class="stat-icon">🧠</div>
 <div class="stat-name">MEMORY</div>
 <div id="memoryStat" class="stat-value">—</div>
</div>

</div>

<div class="panel">
<div class="panel-head">
<h2>ماذا تستطيع NEXORA؟</h2>
<span class="badge">OMNI</span>
</div>

<div class="cards">

<div class="card">
<div class="card-icon">🧠</div>
<h3>تحليل ذكي</h3>
<p>فهم الهدف وتعقيد الطلب وتحديد الحاجة إلى الأدوات.</p>
</div>

<div class="card">
<div class="card-icon">🤖</div>
<h3>توجيه الوكلاء</h3>
<p>توزيع المهمة على الوكلاء المسجلين داخل CORE.</p>
</div>

<div class="card">
<div class="card-icon">⚙️</div>
<h3>Action Engine</h3>
<p>طبقة منفصلة للتنفيذ مع عدم تمرير نص المستخدم مباشرة إلى shell.</p>
</div>

<div class="card">
<div class="card-icon">🛡️</div>
<h3>Verification</h3>
<p>فحص نتيجة التنفيذ قبل اعتبار المهمة مكتملة.</p>
</div>

<div class="card">
<div class="card-icon">🧠</div>
<h3>Memory</h3>
<p>حفظ سياق العمل والنتائج داخل قاعدة NEXORA.</p>
</div>

<div class="card">
<div class="card-icon">🌐</div>
<h3>API Gateway</h3>
<p>بوابة واحدة تربط الواجهة بالـ CORE والذكاء والخدمات.</p>
</div>

</div>
</div>

</section>

<section id="tasks" class="page">
<div class="panel">
<div class="panel-head">
<h2>📋 مركز المهام</h2>
<span class="badge">LIVE DATA</span>
</div>
<div id="tasksData" class="loading">جاري التحميل...</div>
</div>
</section>

<section id="agents" class="page">
<div class="panel">
<div class="panel-head">
<h2>🤖 مركز الوكلاء</h2>
<span class="badge">AGENT NETWORK</span>
</div>
<div id="agentsData" class="loading">جاري التحميل...</div>
</div>
</section>

<section id="memory" class="page">
<div class="panel">
<div class="panel-head">
<h2>🧠 NEXORA MEMORY</h2>
<span class="badge">PERSISTENT</span>
</div>
<div id="memoryData" class="loading">جاري التحميل...</div>
</div>
</section>

<section id="events" class="page">
<div class="panel">
<div class="panel-head">
<h2>📡 سجل الأحداث</h2>
<span class="badge">EVENT STREAM</span>
</div>
<div id="eventsData" class="loading">جاري التحميل...</div>
</div>
</section>

<section id="system" class="page">

<div class="panel">
<div class="panel-head">
<h2>🛡️ مركز النظام</h2>
<span class="badge">HEALTH</span>
</div>
<div id="systemData" class="loading">جاري الفحص...</div>
</div>

<div class="panel">
<div class="panel-head">
<h2>🔌 الخدمات</h2>
<span class="badge">SERVICES</span>
</div>

<div class="cards">

<div class="card">
<div class="card-icon">⚡</div>
<h3>CORE API</h3>
<p>127.0.0.1:8091</p>
</div>

<div class="card">
<div class="card-icon">🖥️</div>
<h3>CLIENT</h3>
<p>127.0.0.1:8080</p>
</div>

<div class="card">
<div class="card-icon">💾</div>
<h3>DATABASE</h3>
<p>nexora_unified.db</p>
</div>

<div class="card">
<div class="card-icon">🌐</div>
<h3>AI GATEWAY</h3>
<p>OpenAI / Local fallback</p>
</div>

</div>
</div>

</section>

<div class="footer">
NEXORA OMNI © 2026 — Unified Intelligence Command Center
</div>

</main>
</div>
</div>

<script>

const CORE="http://127.0.0.1:8091";

function esc(v){
 return String(v ?? "")
 .replaceAll("&","&amp;")
 .replaceAll("<","&lt;")
 .replaceAll(">","&gt;")
 .replaceAll('"',"&quot;")
 .replaceAll("'","&#039;");
}

async function api(path,options={}){
 const r=await fetch(CORE+path,options);
 const data=await r.json();
 if(!r.ok) throw new Error(data.error||"API_ERROR");
 return data;
}

function page(id,btn){

 document.querySelectorAll(".page")
 .forEach(x=>x.classList.remove("active"));

 const target=document.getElementById(id);
 if(target) target.classList.add("active");

 document.querySelectorAll(".nav")
 .forEach(x=>x.classList.remove("active"));

 if(btn) btn.classList.add("active");

 if(id==="tasks") loadTasks();
 if(id==="agents") loadAgents();
 if(id==="memory") loadMemory();
 if(id==="events") loadEvents();
 if(id==="system") loadSystem();
}

function clearPrompt(){
 document.getElementById("prompt").value="";
 document.getElementById("prompt").focus();
}

async function sendTask(){

 const prompt=document.getElementById("prompt");
 const result=document.getElementById("result");
 const state=document.getElementById("commandState");
 const task=prompt.value.trim();

 if(!task){
  prompt.focus();
  return;
 }

 state.textContent="NEXORA تعمل...";
 result.innerHTML=
 '<div class="resultbox"><div class="loading">🧠 تحليل الطلب وربطه بالـ CORE...</div></div>';

 try{

  const data=await api("/api/task",{
   method:"POST",
   headers:{"Content-Type":"application/json"},
   body:JSON.stringify({task})
  });

  const analyst=data.analysis?.analyst||{};
  const ai=data.ai||{};
  const execution=data.execution;

  result.innerHTML=`
  <div class="resultbox">

   <div class="result-grid">

    <div class="metric">
     <small>TASK ID</small>
     <strong>${esc(data.task_id)}</strong>
    </div>

    <div class="metric">
     <small>STATUS</small>
     <strong>${esc(data.status)}</strong>
    </div>

    <div class="metric">
     <small>ANALYST</small>
     <strong>${esc(analyst.complexity||"unknown")}</strong>
    </div>

    <div class="metric">
     <small>TOOLS</small>
     <strong>${analyst.requires_tools?"YES":"NO"}</strong>
    </div>

   </div>

   <div class="answer">
    <strong>🧠 NEXORA RESPONSE</strong>
    <div style="margin-top:8px">
    ${esc(ai.answer||"تمت معالجة الطلب.")}
    </div>
   </div>

   ${
    execution
    ? `
    <div class="panel" style="margin-top:12px">
     <div class="panel-head">
      <h2>⚙️ التنفيذ</h2>
      <span class="badge">ACTION</span>
     </div>
     <pre>${esc(JSON.stringify(execution,null,2))}</pre>
    </div>
    `
    : ""
   }

  </div>
  `;

  state.textContent="تمت المعالجة";
  refreshStats();

 }catch(e){

  state.textContent="حدث خطأ";

  result.innerHTML=
  '<div class="error">⚠️ '+esc(e.message)+'</div>';

 }

}

async function loadTasks(){

 const box=document.getElementById("tasksData");

 try{
  const data=await api("/api/tasks");
  box.innerHTML=format(data);
 }catch(e){
  box.innerHTML='<div class="error">'+esc(e.message)+'</div>';
 }

}

async function loadAgents(){

 const box=document.getElementById("agentsData");

 try{
  const data=await api("/api/agents");
  box.innerHTML=format(data);
 }catch(e){
  box.innerHTML='<div class="error">'+esc(e.message)+'</div>';
 }

}

async function loadMemory(){

 const box=document.getElementById("memoryData");

 try{
  const data=await api("/api/memories");
  box.innerHTML=format(data);
 }catch(e){
  box.innerHTML='<div class="error">'+esc(e.message)+'</div>';
 }

}

async function loadEvents(){

 const box=document.getElementById("eventsData");

 try{
  const data=await api("/api/events");
  box.innerHTML=format(data);
 }catch(e){
  box.innerHTML='<div class="error">'+esc(e.message)+'</div>';
 }

}

async function loadSystem(){

 const box=document.getElementById("systemData");

 try{
  const data=await api("/api/status");

  box.innerHTML=`
  <div class="cards">

   <div class="card">
    <div class="card-icon">⚡</div>
    <h3>CORE</h3>
    <p>${esc(data.core||data.status)}</p>
   </div>

   <div class="card">
    <div class="card-icon">🌐</div>
    <h3>API</h3>
    <p>${esc(data.api||"online")}</p>
   </div>

   <div class="card">
    <div class="card-icon">💾</div>
    <h3>DATABASE</h3>
    <p>${esc(data.database||"online")}</p>
   </div>

   <div class="card">
    <div class="card-icon">🤖</div>
    <h3>AI GATEWAY</h3>
    <p>${esc(data.ai_gateway||"unknown")}</p>
   </div>

  </div>

  <div style="margin-top:15px">
  <pre>${esc(JSON.stringify(data,null,2))}</pre>
  </div>
  `;

 }catch(e){
  box.innerHTML='<div class="error">'+esc(e.message)+'</div>';
 }

}

function format(data){

 if(Array.isArray(data)){

  if(!data.length)
   return '<p style="color:#71839d">لا توجد بيانات حالياً.</p>';

  return '<pre>'+esc(JSON.stringify(data,null,2))+'</pre>';
 }

 return '<pre>'+esc(JSON.stringify(data,null,2))+'</pre>';
}

async function refreshStats(){

 try{

  const status=await api("/api/status");

  document.getElementById("coreStat").textContent=
   status.core||status.status||"online";

  document.getElementById("agentStat").textContent=
   status.agents||"online";

  document.getElementById("taskStat").textContent=
   status.tasks||"—";

  document.getElementById("memoryStat").textContent=
   status.memory||status.memories||"—";

 }catch(e){

  document.getElementById("coreStat").textContent="offline";

 }

}

async function health(){

 const live=document.getElementById("live");

 try{

  const data=await api("/api/status");

  live.innerHTML=
  '<span class="dot"></span><span>المنظومة متاحة</span>';

 }catch(e){

  live.innerHTML=
  '<span style="color:#f87171">● CORE غير متصل</span>';

 }

}

async function refreshAll(){

 await health();
 await refreshStats();

 const active=document.querySelector(".page.active");

 if(active){

  if(active.id==="tasks") loadTasks();
  if(active.id==="agents") loadAgents();
  if(active.id==="memory") loadMemory();
  if(active.id==="events") loadEvents();
  if(active.id==="system") loadSystem();

 }

}

health();
refreshStats();

setInterval(health,5000);
setInterval(refreshStats,10000);

document.getElementById("prompt")
.addEventListener("keydown",function(e){
 if((e.ctrlKey||e.metaKey)&&e.key==="Enter"){
  sendTask();
 }
});

</script>

</body>
</html>
'''

class Handler(BaseHTTPRequestHandler):

    def send_json(self,data,status=200):

        body=json.dumps(
            data,
            ensure_ascii=False
        ).encode()

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header(
            "Content-Length",
            str(len(body))
        )
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):

        if self.path == "/api/status":

            try:

                req=urllib.request.Request(
                    CORE+"/api/status"
                )

                with urllib.request.urlopen(
                    req,
                    timeout=3
                ) as r:

                    data=json.loads(
                        r.read().decode()
                    )

                self.send_json(data)

            except Exception as e:

                self.send_json(
                    {
                        "status":"offline",
                        "error":str(e)
                    },
                    503
                )

            return

        body=HTML.encode()

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )
        self.send_header(
            "Content-Length",
            str(len(body))
        )
        self.end_headers()
        self.wfile.write(body)

    def log_message(self,*args):
        pass


if __name__=="__main__":

    print(
        f"NEXORA OMNI V3 "
        f"http://{HOST}:{PORT}"
    )

    ThreadingHTTPServer(
        (HOST,PORT),
        Handler
    ).serve_forever()
