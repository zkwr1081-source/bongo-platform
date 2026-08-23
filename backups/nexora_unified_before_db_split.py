#!/usr/bin/env python3
import os
import json
import sqlite3
import threading
import time
import traceback
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from datetime import datetime
from action_engine import ActionEngine

# ============================================================
# NEXORA UNIFIED
# Core + Agents + Memory + AI Gateway + Automation + API + UI
# ============================================================

HOST = "127.0.0.1"
PORT = 8091
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_FILE = os.path.join(BASE_DIR, "nexora.db")
LOG_FILE = os.path.join(BASE_DIR, "nexora.log")

VERSION = "2.0.0-unified"

OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "").strip()
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "").strip()

OPENAI_MODEL = os.environ.get("NEXORA_OPENAI_MODEL", "gpt-4o-mini")
GEMINI_MODEL = os.environ.get("NEXORA_GEMINI_MODEL", "gemini-2.5-flash")


# ============================================================
# LOGGING
# ============================================================

def log(message):
    text = "[{}] {}".format(
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        message
    )
    try:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(text + "\n")
    except Exception:
        pass
    print(text, flush=True)


# ============================================================
# DATABASE
# ============================================================

class Database:
    def __init__(self):
        self.path = DB_FILE
        self.lock = threading.Lock()
        self.init()

    def connect(self):
        return sqlite3.connect(
            self.path,
            check_same_thread=False
        )

    def init(self):
        with self.lock:
            con = self.connect()
            cur = con.cursor()

            cur.execute("""
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS tasks (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    task TEXT NOT NULL,
                    status TEXT NOT NULL,
                    result TEXT,
                    created_at TEXT NOT NULL
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS agents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL,
                    role TEXT NOT NULL,
                    status TEXT NOT NULL
                )
            """)

            cur.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    event TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
            """)

            con.commit()
            con.close()

    def add_memory(self, content):
        with self.lock:
            con = self.connect()
            con.execute(
                "INSERT INTO memories(content,created_at) VALUES(?,?)",
                (content, datetime.now().isoformat())
            )
            con.commit()
            con.close()

    def memories(self, limit=20):
        con = self.connect()
        rows = con.execute(
            "SELECT id,content,created_at FROM memories "
            "ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
        con.close()

        return [
            {
                "id": r[0],
                "content": r[1],
                "created_at": r[2]
            }
            for r in rows
        ]

    def add_task(self, task, status="received", result=""):
        with self.lock:
            con = self.connect()
            cur = con.execute(
                "INSERT INTO tasks(task,status,result,created_at) "
                "VALUES(?,?,?,?)",
                (
                    task,
                    status,
                    result,
                    datetime.now().isoformat()
                )
            )
            task_id = cur.lastrowid
            con.commit()
            con.close()
            return task_id

    def update_task(self, task_id, status, result=""):
        with self.lock:
            con = self.connect()
            con.execute(
                "UPDATE tasks SET status=?,result=? WHERE id=?",
                (status, result, task_id)
            )
            con.commit()
            con.close()

    def tasks(self, limit=20):
        con = self.connect()
        rows = con.execute(
            "SELECT id,task,status,result,created_at "
            "FROM tasks ORDER BY id DESC LIMIT ?",
            (limit,)
        ).fetchall()
        con.close()

        return [
            {
                "id": r[0],
                "task": r[1],
                "status": r[2],
                "result": r[3],
                "created_at": r[4]
            }
            for r in rows
        ]

    def seed_agents(self):
        agents = [
            ("CORE", "تنسيق النظام والوكلاء"),
            ("ANALYST", "تحليل المشاكل والطلبات"),
            ("RESEARCH", "البحث والاستكشاف"),
            ("PLANNER", "التخطيط وتحويل الطلب إلى خطوات"),
            ("BUILDER", "بناء الحلول والبرمجيات"),
            ("SECURITY", "الأمن والتحقق والمراجعة"),
            ("MEMORY", "إدارة المعرفة والذاكرة"),
            ("AUTOMATION", "تنسيق الأتمتة"),
            ("INNOVATION", "اكتشاف فرص التطوير"),
            ("VERIFY", "التحقق من النتائج"),
        ]

        with self.lock:
            con = self.connect()

            for name, role in agents:
                con.execute(
                    """
                    INSERT OR IGNORE INTO agents(name,role,status)
                    VALUES(?,?,?)
                    """,
                    (name, role, "online")
                )

            con.commit()
            con.close()

    def agents(self):
        con = self.connect()
        rows = con.execute(
            "SELECT id,name,role,status FROM agents "
            "ORDER BY id"
        ).fetchall()
        con.close()

        return [
            {
                "id": r[0],
                "name": r[1],
                "role": r[2],
                "status": r[3]
            }
            for r in rows
        ]

    def add_event(self, event):
        with self.lock:
            con = self.connect()
            con.execute(
                "INSERT INTO events(event,created_at) VALUES(?,?)",
                (event, datetime.now().isoformat())
            )
            con.commit()
            con.close()

    def stats(self):
        con = self.connect()

        memories = con.execute(
            "SELECT COUNT(*) FROM memories"
        ).fetchone()[0]

        tasks = con.execute(
            "SELECT COUNT(*) FROM tasks"
        ).fetchone()[0]

        agents = con.execute(
            "SELECT COUNT(*) FROM agents WHERE status='online'"
        ).fetchone()[0]

        con.close()

        return {
            "memories": memories,
            "tasks": tasks,
            "agents_online": agents
        }


DB = Database()
DB.seed_agents()

ACTION_ENGINE = ActionEngine(BASE_DIR)


# ============================================================
# AI GATEWAY
# ============================================================

def call_openai(prompt):
    if not OPENAI_API_KEY:
        return None

    url = "https://api.openai.com/v1/chat/completions"

    payload = {
        "model": OPENAI_MODEL,
        "messages": [
            {
                "role": "system",
                "content": (
                    "You are NEXORA, an AI orchestration system. "
                    "Analyze requests clearly, safely and practically."
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.2
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json",
            "Authorization": "Bearer " + OPENAI_API_KEY
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

        return result["choices"][0]["message"]["content"]

    except Exception as e:
        log("OpenAI error: " + str(e))
        return None


def call_gemini(prompt):
    if not GEMINI_API_KEY:
        return None

    url = (
        "https://generativelanguage.googleapis.com/v1beta/"
        "models/" + GEMINI_MODEL +
        ":generateContent?key=" + GEMINI_API_KEY
    )

    payload = {
        "contents": [
            {
                "parts": [
                    {
                        "text": (
                            "You are NEXORA AI.\n\n" +
                            prompt
                        )
                    }
                ]
            }
        ]
    }

    data = json.dumps(payload).encode("utf-8")

    req = urllib.request.Request(
        url,
        data=data,
        headers={
            "Content-Type": "application/json"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=90) as response:
            result = json.loads(
                response.read().decode("utf-8")
            )

        return result["candidates"][0]["content"]["parts"][0]["text"]

    except Exception as e:
        log("Gemini error: " + str(e))
        return None


def ai_gateway(prompt):
    answer = call_openai(prompt)

    if answer:
        return {
            "provider": "openai",
            "model": OPENAI_MODEL,
            "answer": answer
        }

    answer = call_gemini(prompt)

    if answer:
        return {
            "provider": "gemini",
            "model": GEMINI_MODEL,
            "answer": answer
        }

    return {
        "provider": "local",
        "model": "nexora-local",
        "answer": local_reasoning(prompt)
    }


# ============================================================
# LOCAL NEXORA CORE
# ============================================================

def local_reasoning(prompt):
    p = prompt.lower()

    if any(x in p for x in [
        "مشروع",
        "project",
        "build",
        "بناء"
    ]):
        return (
            "تم استلام الطلب. NEXORA قسمت المهمة إلى: "
            "تحليل المشكلة، تحديد المتطلبات، التخطيط، "
            "التنفيذ، التحقق، ثم النتيجة."
        )

    if any(x in p for x in [
        "حلل",
        "تحليل",
        "analyze"
    ]):
        return (
            "تحليل NEXORA المحلي: "
            "المطلوب يحتاج تحديد الهدف والمدخلات والقيود "
            "ثم بناء خطوات قابلة للتحقق."
        )

    return (
        "NEXORA استلمت الطلب محليًا. "
        "يمكن ربط بوابات الذكاء الاصطناعي لإعطاء "
        "استجابة نماذج خارجية عند توفر مفاتيح API."
    )


# ============================================================
# ORCHESTRATOR
# ============================================================

def process_task(task):
    task_id = DB.add_task(task, "analyzing")

    try:
        DB.add_event("Task received: " + task[:200])

        DB.add_memory(
            "User request: " + task
        )

        result = ai_gateway(task)

        # ----------------------------------------------------
        # ACTION BRIDGE
        # ----------------------------------------------------
        # التنفيذ لا يحدث إلا إذا طلبت المهمة Action صريحة.
        # في هذه المرحلة نختبر المسار بأمر آمن ومحدد فقط.
        action = None

        if task.strip().lower() == "nexora test execution":
            action = {
                "type": "shell",
                "command": "pwd"
            }

        execution = None

        if action:
            execution = ACTION_ENGINE.execute_action(action)

        response = {
            "task_id": task_id,
            "status": "completed",
            "analysis": {
                "agents": [
                    "CORE",
                    "ANALYST",
                    "PLANNER",
                    "VERIFY"
                ]
            },
            "ai": result,
            "action": action,
            "execution": execution,
            "memory_saved": True
        }

        DB.update_task(
            task_id,
            "completed",
            json.dumps(response, ensure_ascii=False)
        )

        DB.add_event(
            "Task completed: " + str(task_id)
        )

        return response

    except Exception as e:
        error = str(e)

        DB.update_task(
            task_id,
            "error",
            error
        )

        log(traceback.format_exc())

        return {
            "task_id": task_id,
            "status": "error",
            "error": error
        }


# ============================================================
# AUTOMATION
# ============================================================

def automation_info():
    return {
        "enabled": True,
        "mode": "controlled",
        "description": (
            "NEXORA automation coordinator. "
            "Dangerous/destructive operations require review."
        ),
        "supported": [
            "task orchestration",
            "AI requests",
            "memory",
            "planning",
            "verification",
            "project tracking"
        ]
    }


# ============================================================
# API
# ============================================================

class Handler(BaseHTTPRequestHandler):

    def send_json(self, data, status=200):
        raw = json.dumps(
            data,
            ensure_ascii=False,
            indent=2
        ).encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header(
            "Content-Length",
            str(len(raw))
        )
        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )
        self.end_headers()
        self.wfile.write(raw)

    def read_json(self):
        length = int(
            self.headers.get("Content-Length", "0")
        )

        if length <= 0:
            return {}

        raw = self.rfile.read(length)

        return json.loads(
            raw.decode("utf-8")
        )

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header(
            "Access-Control-Allow-Origin",
            "*"
        )
        self.send_header(
            "Access-Control-Allow-Methods",
            "GET,POST,OPTIONS"
        )
        self.send_header(
            "Access-Control-Allow-Headers",
            "Content-Type"
        )
        self.end_headers()

    def do_GET(self):

        try:

            if self.path == "/":
                self.send_html()
                return

            if self.path == "/api/status":
                self.send_json({
                    "status": "online",
                    "version": VERSION,
                    "core": "online",
                    "api": "online",
                    "database": "online",
                    "agents": "online",
                    "ai_gateway": (
                        "openai"
                        if OPENAI_API_KEY
                        else (
                            "gemini"
                            if GEMINI_API_KEY
                            else "local"
                        )
                    ),
                    "url": "http://127.0.0.1:8091",
                    "database_file": DB_FILE
                })
                return

            if self.path == "/api/agents":
                self.send_json({
                    "agents": DB.agents()
                })
                return

            if self.path == "/api/memory":
                self.send_json({
                    "memories": DB.memories()
                })
                return

            if self.path == "/api/tasks":
                self.send_json({
                    "tasks": DB.tasks()
                })
                return

            if self.path == "/api/stats":
                self.send_json(DB.stats())
                return

            if self.path == "/api/automation":
                self.send_json(
                    automation_info()
                )
                return

            self.send_json(
                {"error": "not_found"},
                404
            )

        except Exception as e:
            log(traceback.format_exc())

            self.send_json(
                {"error": str(e)},
                500
            )

    def do_POST(self):
        try:

            if self.path == "/api/task":
                data = self.read_json()

                task = str(
                    data.get("task", "")
                ).strip()

                if not task:
                    self.send_json(
                        {
                            "error": "task_required"
                        },
                        400
                    )
                    return

                result = process_task(task)

                self.send_json(result)
                return

            if self.path == "/api/memory":
                data = self.read_json()

                content = str(
                    data.get("content", "")
                ).strip()

                if not content:
                    self.send_json(
                        {
                            "error": "content_required"
                        },
                        400
                    )
                    return

                DB.add_memory(content)

                self.send_json({
                    "status": "saved"
                })
                return

            self.send_json(
                {"error": "not_found"},
                404
            )

        except Exception as e:
            log(traceback.format_exc())

            self.send_json(
                {"error": str(e)},
                500
            )

    def send_html(self):

        html = r"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport"
content="width=device-width,initial-scale=1">

<title>NEXORA</title>

<style>

*{
box-sizing:border-box
}

body{
margin:0;
font-family:Arial,Tahoma,sans-serif;
background:
radial-gradient(circle at top,#18275d,#050914 65%);
color:#eef3ff;
min-height:100vh
}

header{
padding:22px;
border-bottom:1px solid #1d2945;
background:#071022dd;
backdrop-filter:blur(12px);
position:sticky;
top:0;
z-index:5
}

.logo{
font-size:27px;
font-weight:900
}

.online{
color:#48e39a;
font-size:13px;
margin-top:5px
}

.container{
width:min(1150px,94%);
margin:auto;
padding:35px 0
}

.hero{
text-align:center;
padding:25px 0 35px
}

.hero h1{
font-size:42px;
margin:10px 0
}

.hero p{
color:#aebbd5;
font-size:16px
}

.grid{
display:grid;
grid-template-columns:
repeat(auto-fit,minmax(180px,1fr));
gap:15px
}

.card{
background:#0b1429e8;
border:1px solid #1c2a48;
border-radius:18px;
padding:20px;
box-shadow:0 10px 35px #0004
}

.card h3{
margin-top:0
}

.number{
font-size:30px;
font-weight:900
}

.workspace{
margin-top:20px
}

textarea{
width:100%;
min-height:160px;
resize:vertical;
border-radius:14px;
border:1px solid #263553;
background:#040917;
color:#fff;
padding:18px;
font-size:16px;
outline:none
}

button{
border:0;
border-radius:12px;
padding:13px 20px;
font-size:15px;
font-weight:bold;
cursor:pointer;
background:#2d6df6;
color:#fff
}

button.secondary{
background:#18233b
}

.buttons{
display:flex;
gap:10px;
margin-top:12px;
flex-wrap:wrap
}

pre{
white-space:pre-wrap;
word-break:break-word;
background:#030713;
border:1px solid #1a2948;
border-radius:14px;
padding:18px;
min-height:120px;
overflow:auto
}

.badge{
display:inline-block;
padding:7px 12px;
border-radius:20px;
background:#14233d;
margin:4px;
font-size:13px
}

footer{
text-align:center;
padding:35px;
color:#7785a4
}

</style>
</head>

<body>

<header>
<div class="logo">NEXORA</div>
<div class="online">● النظام متاح</div>
</header>

<div class="container">

<section class="hero">

<h1>ممر NEXORA الذكي</h1>

<p>
من المشكلة → إلى التحليل → إلى الخطة
→ إلى التنفيذ → إلى النتيجة
</p>

</section>

<section class="grid">

<div class="card">
<h3>النواة</h3>
<div class="number">CORE</div>
<p>تنسيق الطلبات والوكلاء والنتائج</p>
</div>

<div class="card">
<h3>الوكلاء</h3>
<div class="number" id="agents">...</div>
<p>شبكة الوكلاء المتخصصة</p>
</div>

<div class="card">
<h3>المهام</h3>
<div class="number" id="tasks">...</div>
<p>المهام المسجلة</p>
</div>

<div class="card">
<h3>الذاكرة</h3>
<div class="number" id="memory">...</div>
<p>المعرفة والذاكرة</p>
</div>

</section>

<section class="card workspace">

<h2>مساحة العمل الذكية</h2>

<p>
اكتب المشكلة أو المهمة التي تريد من NEXORA تحليلها.
</p>

<textarea
id="task"
placeholder="مثال: أريد بناء مشروع تقني جديد وتحليل أفضل طريقة لتنفيذه..."
></textarea>

<div class="buttons">

<button onclick="runTask()">
✦ ابدأ NEXORA
</button>

<button
class="secondary"
onclick="document.getElementById('task').value=''"
>
مسح
</button>

</div>

<h3>النتيجة</h3>

<pre id="result">بانتظار المهمة...</pre>

</section>

<section class="card">

<h2>الوكلاء</h2>

<div id="agentList"></div>

</section>

<section class="card">

<h2>حالة النظام</h2>

<pre id="status">جاري الفحص...</pre>

</section>

</div>

<footer>
NEXORA Unified — Intelligence • Automation • Memory
</footer>

<script>

async function api(url,options){
const r=await fetch(url,options);
return await r.json();
}

async function refresh(){

try{

const s=await api('/api/status');

document.getElementById('status')
.textContent=
JSON.stringify(s,null,2);

const st=await api('/api/stats');

document.getElementById('agents')
.textContent=st.agents_online;

document.getElementById('tasks')
.textContent=st.tasks;

document.getElementById('memory')
.textContent=st.memories;

const a=await api('/api/agents');

document.getElementById('agentList')
.innerHTML=a.agents.map(x=>
'<span class="badge">'+
x.name+' — '+x.role+
'</span>'
).join('');

}catch(e){

document.getElementById('status')
.textContent='تعذر الاتصال بالنظام';

}

}

async function runTask(){

const box=document.getElementById('task');
const result=document.getElementById('result');

const task=box.value.trim();

if(!task){

result.textContent='اكتب المهمة أولًا.';
return;

}

result.textContent='NEXORA تعمل على تحليل المهمة...';

try{

const data=await api(
'/api/task',
{
method:'POST',
headers:{
'Content-Type':'application/json'
},
body:JSON.stringify({
task:task
})
}
);

result.textContent=
JSON.stringify(data,null,2);

refresh();

}catch(e){

result.textContent=
'حدث خطأ في الاتصال: '+e;

}

}

refresh();

setInterval(refresh,5000);

</script>

</body>
</html>
"""

        raw = html.encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )
        self.send_header(
            "Content-Length",
            str(len(raw))
        )
        self.end_headers()
        self.wfile.write(raw)


# ============================================================
# SERVER
# ============================================================

def start_server():

    server = ThreadingHTTPServer(
        (HOST, PORT),
        Handler
    )

    log(
        "NEXORA running at "
        "http://{}:{}".format(HOST, PORT)
    )

    server.serve_forever()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    print("=" * 60)
    print("NEXORA UNIFIED")
    print("VERSION:", VERSION)
    print("HOST:", HOST)
    print("PORT:", PORT)
    print("DATABASE:", DB_FILE)
    print("=" * 60)

    start_server()
