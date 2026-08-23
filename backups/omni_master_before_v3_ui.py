#!/usr/bin/env python3

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import time
import urllib.request
import urllib.error

HOST = "127.0.0.1"
PORT = 8080
CORE = "http://127.0.0.1:8091"

HTML = r'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#060914">
<title>NEXORA OMNI</title>

<style>
*{box-sizing:border-box}

body{
margin:0;
background:#050814;
color:#fff;
font-family:system-ui,-apple-system,"Segoe UI",sans-serif
}

button,input,textarea{font:inherit}

.app{
min-height:100vh;
background:
radial-gradient(circle at 50% -10%,#172554 0,#050814 42%),
#050814
}

nav{
height:68px;
display:flex;
align-items:center;
justify-content:space-between;
padding:0 20px;
border-bottom:1px solid #1e293b;
background:#080d18ee;
backdrop-filter:blur(18px);
position:sticky;
top:0;
z-index:20
}

.logo{
font-size:22px;
font-weight:900;
letter-spacing:.5px
}

.logo span{color:#67e8f9}

.status{
font-size:12px;
color:#86efac;
background:#052e1a;
border:1px solid #14532d;
padding:8px 13px;
border-radius:999px
}

.layout{
max-width:1250px;
margin:auto;
padding:25px 16px 60px
}

.hero{
padding:25px 0;
text-align:center
}

.eyebrow{
color:#67e8f9;
font-size:12px;
font-weight:800;
letter-spacing:1px
}

h1{
font-size:clamp(38px,7vw,70px);
line-height:1;
margin:12px 0
}

.hero p{
max-width:700px;
margin:auto;
color:#94a3b8;
line-height:1.8
}

.workspace{
background:#0b1220;
border:1px solid #263247;
border-radius:25px;
padding:18px;
box-shadow:0 25px 80px #0008
}

textarea{
width:100%;
min-height:145px;
resize:vertical;
border:1px solid #1e293b;
outline:none;
background:#060b15;
color:#fff;
border-radius:17px;
padding:17px;
line-height:1.8
}

textarea:focus{
border-color:#22d3ee
}

.actions{
display:grid;
grid-template-columns:1fr 1fr;
gap:10px;
margin-top:12px
}

.btn{
border:0;
border-radius:14px;
padding:14px;
font-weight:900;
cursor:pointer
}

.primary{
background:linear-gradient(90deg,#22d3ee,#818cf8);
color:#061018
}

.secondary{
background:#111827;
color:#cbd5e1;
border:1px solid #263247
}

.grid{
display:grid;
grid-template-columns:repeat(auto-fit,minmax(210px,1fr));
gap:14px;
margin-top:18px
}

.card{
background:#0b1220;
border:1px solid #1e293b;
border-radius:20px;
padding:20px
}

.card h3{
margin:8px 0
}

.muted{
color:#94a3b8;
font-size:13px;
line-height:1.7
}

.icon{
font-size:25px
}

.panel{
margin-top:18px;
background:#0b1220;
border:1px solid #1e293b;
border-radius:22px;
padding:20px
}

.panel-head{
display:flex;
justify-content:space-between;
align-items:center;
gap:10px;
margin-bottom:12px
}

.panel-head h2{
margin:0;
font-size:18px
}

.badge{
font-size:11px;
padding:6px 10px;
border-radius:999px;
background:#111827;
color:#67e8f9
}

.result{
background:#060b15;
border:1px solid #164e63;
border-radius:17px;
padding:17px;
line-height:1.8
}

.row{
display:flex;
justify-content:space-between;
gap:15px;
padding:10px 0;
border-bottom:1px solid #172033
}

.row:last-child{border:0}

.value{
color:#67e8f9;
font-weight:700
}

pre{
white-space:pre-wrap;
word-break:break-word;
color:#cbd5e1;
font-size:12px;
margin:0
}

table{
width:100%;
border-collapse:collapse;
font-size:13px
}

th,td{
padding:11px;
border-bottom:1px solid #172033;
text-align:right
}

th{color:#67e8f9}

.nav-buttons{
display:flex;
gap:8px;
overflow:auto;
margin:18px 0
}

.nav-btn{
white-space:nowrap;
background:#0b1220;
color:#cbd5e1;
border:1px solid #1e293b;
border-radius:12px;
padding:10px 14px;
cursor:pointer
}

.nav-btn.active{
border-color:#22d3ee;
color:#67e8f9
}

.section{display:none}
.section.active{display:block}

.loading{
color:#67e8f9
}

.error{
color:#fca5a5;
background:#450a0a;
border:1px solid #7f1d1d;
padding:12px;
border-radius:12px
}

footer{
text-align:center;
color:#64748b;
font-size:12px;
margin-top:45px
}

@media(max-width:600px){
.actions{grid-template-columns:1fr}
nav{padding:0 12px}
.layout{padding:15px 10px 40px}
}
</style>
</head>

<body>

<div class="app">

<nav>
<div class="logo">NEXORA <span>OMNI</span></div>
<div id="status" class="status">● جاري الفحص</div>
</nav>

<div class="layout">

<section class="hero">
<div class="eyebrow">INTELLIGENCE • AUTOMATION • RESULTS</div>
<h1>من المشكلة<br><span style="color:#67e8f9">إلى النتيجة.</span></h1>
<p>
مركز التحكم الموحد لـ NEXORA:
الذكاء، الوكلاء، المهام، الذاكرة، التنفيذ والتحقق.
</p>
</section>

<div class="nav-buttons">
<button class="nav-btn active" onclick="showSection('home',this)">الرئيسية</button>
<button class="nav-btn" onclick="showSection('tasks',this)">المهام</button>
<button class="nav-btn" onclick="showSection('agents',this)">الوكلاء</button>
<button class="nav-btn" onclick="showSection('memory',this)">الذاكرة</button>
<button class="nav-btn" onclick="showSection('events',this)">الأحداث</button>
<button class="nav-btn" onclick="showSection('system',this)">النظام</button>
</div>

<section id="home" class="section active">

<div class="workspace">

<textarea id="prompt"
placeholder="اكتب ما تريد من NEXORA...&#10;&#10;مثال: حلل المشروع وحدد الملفات المهمة واقترح الخطوة التالية."></textarea>

<div class="actions">
<button class="btn primary" onclick="sendTask()">🧠 ابدأ مع NEXORA</button>
<button class="btn secondary" onclick="clearPrompt()">مسح</button>
</div>

<div id="taskResult" style="margin-top:15px"></div>

</div>

<div class="grid">

<div class="card">
<div class="icon">🧠</div>
<h3>الذكاء</h3>
<p class="muted">إرسال الطلبات إلى طبقة الذكاء ومعالجة النتائج.</p>
</div>

<div class="card">
<div class="icon">🤖</div>
<h3>الوكلاء</h3>
<p class="muted">ANALYST والوكلاء المسجلون في المنظومة.</p>
</div>

<div class="card">
<div class="icon">⚙️</div>
<h3>التنفيذ</h3>
<p class="muted">تنفيذ الإجراءات عبر طبقة Action Engine عند السماح.</p>
</div>

<div class="card">
<div class="icon">🛡️</div>
<h3>التحقق</h3>
<p class="muted">فحص حالة التنفيذ والنتائج قبل إتمام المهمة.</p>
</div>

<div class="card">
<div class="icon">🧠</div>
<h3>الذاكرة</h3>
<p class="muted">حفظ سياق المهام والنتائج في قاعدة NEXORA.</p>
</div>

<div class="card">
<div class="icon">🌐</div>
<h3>CORE API</h3>
<p class="muted">الواجهة متصلة مباشرة بخدمة NEXORA على المنفذ 8091.</p>
</div>

</div>

</section>

<section id="tasks" class="section">

<div class="panel">

<div class="panel-head">
<h2>📋 المهام</h2>
<span class="badge">CORE</span>
</div>

<div id="tasksData">جاري التحميل...</div>

</div>

</section>

<section id="agents" class="section">

<div class="panel">

<div class="panel-head">
<h2>🤖 الوكلاء</h2>
<span class="badge">AGENTS</span>
</div>

<div id="agentsData">جاري التحميل...</div>

</div>

</section>

<section id="memory" class="section">

<div class="panel">

<div class="panel-head">
<h2>🧠 الذاكرة</h2>
<span class="badge">MEMORY</span>
</div>

<div id="memoryData">جاري التحميل...</div>

</div>

</section>

<section id="events" class="section">

<div class="panel">

<div class="panel-head">
<h2>📡 الأحداث</h2>
<span class="badge">EVENTS</span>
</div>

<div id="eventsData">جاري التحميل...</div>

</div>

</section>

<section id="system" class="section">

<div class="panel">

<div class="panel-head">
<h2>🛡️ حالة المنظومة</h2>
<span class="badge">SYSTEM</span>
</div>

<div id="systemData">جاري الفحص...</div>

</div>

</section>

<footer>
NEXORA OMNI © 2026 — Unified Intelligence Portal
</footer>

</div>
</div>

<script>

const CORE = "http://127.0.0.1:8091";

function showSection(id,button){

document.querySelectorAll('.section')
.forEach(x=>x.classList.remove('active'));

document.getElementById(id)
.classList.add('active');

document.querySelectorAll('.nav-btn')
.forEach(x=>x.classList.remove('active'));

button.classList.add('active');

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

const input=document.getElementById("prompt");
const result=document.getElementById("taskResult");
const task=input.value.trim();

if(!task){
input.focus();
return;
}

result.innerHTML=
'<div class="result"><div class="loading">🧠 NEXORA تعالج الطلب...</div></div>';

try{

const response=await fetch(CORE+"/api/task",{
method:"POST",
headers:{
"Content-Type":"application/json"
},
body:JSON.stringify({task:task})
});

const data=await response.json();

if(!response.ok){
throw new Error(data.error || "request_failed");
}

const analyst=data.analysis?.analyst || {};
const ai=data.ai || {};
const execution=data.execution;

result.innerHTML=`

<div class="result">

<div class="row">
<span>الحالة</span>
<span class="value">${escapeHtml(data.status || "unknown")}</span>
</div>

<div class="row">
<span>Task ID</span>
<span class="value">${escapeHtml(String(data.task_id || ""))}</span>
</div>

<div class="row">
<span>ANALYST</span>
<span class="value">${escapeHtml(analyst.complexity || "unknown")}</span>
</div>

<div class="row">
<span>الأدوات المطلوبة</span>
<span class="value">${analyst.requires_tools ? "نعم" : "لا"}</span>
</div>

<div class="row">
<span>AI Provider</span>
<span class="value">${escapeHtml(ai.provider || "unknown")}</span>
</div>

<div class="row">
<span>AI Model</span>
<span class="value">${escapeHtml(ai.model || "unknown")}</span>
</div>

<div style="margin-top:15px">
<strong>الاستجابة</strong>
<p class="muted">${escapeHtml(ai.answer || "تمت معالجة الطلب.")}</p>
</div>

${execution ? `
<div style="margin-top:15px">
<strong>التنفيذ</strong>
<pre>${escapeHtml(JSON.stringify(execution,null,2))}</pre>
</div>
` : ""}

</div>
`;

}catch(error){

result.innerHTML=
'<div class="error">⚠️ '+escapeHtml(error.message)+'</div>';

}

}

async function api(path){

const response=await fetch(CORE+path);

const data=await response.json();

if(!response.ok){
throw new Error(data.error || "API error");
}

return data;

}

async function loadTasks(){

const box=document.getElementById("tasksData");

try{

const data=await api("/api/tasks");

box.innerHTML=renderData(data);

}catch(e){

box.innerHTML='<div class="error">'+escapeHtml(e.message)+'</div>';

}

}

async function loadAgents(){

const box=document.getElementById("agentsData");

try{

const data=await api("/api/agents");

box.innerHTML=renderData(data);

}catch(e){

box.innerHTML='<div class="error">'+escapeHtml(e.message)+'</div>';

}

}

async function loadMemory(){

const box=document.getElementById("memoryData");

try{

const data=await api("/api/memories");

box.innerHTML=renderData(data);

}catch(e){

box.innerHTML='<div class="error">'+escapeHtml(e.message)+'</div>';

}

}

async function loadEvents(){

const box=document.getElementById("eventsData");

try{

const data=await api("/api/events");

box.innerHTML=renderData(data);

}catch(e){

box.innerHTML='<div class="error">'+escapeHtml(e.message)+'</div>';

}

}

async function loadSystem(){

const box=document.getElementById("systemData");

try{

const data=await api("/api/status");

box.innerHTML=

'<pre>'+escapeHtml(JSON.stringify(data,null,2))+'</pre>';

}catch(e){

box.innerHTML='<div class="error">'+escapeHtml(e.message)+'</div>';

}

}

function renderData(data){

if(Array.isArray(data)){

if(data.length===0){
return '<p class="muted">لا توجد بيانات.</p>';
}

return '<pre>'+escapeHtml(JSON.stringify(data,null,2))+'</pre>';

}

if(data && Array.isArray(data.tasks)){
return '<pre>'+escapeHtml(JSON.stringify(data.tasks,null,2))+'</pre>';
}

if(data && Array.isArray(data.agents)){
return '<pre>'+escapeHtml(JSON.stringify(data.agents,null,2))+'</pre>';
}

if(data && Array.isArray(data.memories)){
return '<pre>'+escapeHtml(JSON.stringify(data.memories,null,2))+'</pre>';
}

if(data && Array.isArray(data.events)){
return '<pre>'+escapeHtml(JSON.stringify(data.events,null,2))+'</pre>';
}

return '<pre>'+escapeHtml(JSON.stringify(data,null,2))+'</pre>';

}

function escapeHtml(value){

return String(value)
.replaceAll("&","&amp;")
.replaceAll("<","&lt;")
.replaceAll(">","&gt;")
.replaceAll('"',"&quot;")
.replaceAll("'","&#039;");

}

async function health(){

const status=document.getElementById("status");

try{

const data=await api("/api/status");

status.textContent="● المنظومة متاحة";
status.style.color="#86efac";

}catch(e){

status.textContent="● CORE غير متصل";
status.style.color="#fca5a5";

}

}

health();

setInterval(health,10000);

</script>

</body>
</html>
'''

class Handler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):

        body=json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8")

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
                ) as response:

                    data=json.loads(
                        response.read().decode()
                    )

                self.send_json(data)

            except Exception as exc:

                self.send_json(
                    {
                        "status":"offline",
                        "error":str(exc)
                    },
                    503
                )

            return

        body=HTML.encode("utf-8")

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


if __name__ == "__main__":

    print(
        f"NEXORA OMNI CLIENT running at "
        f"http://{HOST}:{PORT}"
    )

    ThreadingHTTPServer(
        (HOST,PORT),
        Handler
    ).serve_forever()
