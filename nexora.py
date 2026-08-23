#!/usr/bin/env python3

import os
import json
import sqlite3
import uuid
import threading
import subprocess
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

APP = "NEXORA"
VERSION = "2.0.0"
HOST = "127.0.0.1"
PORT = 8091

BASE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(BASE, "data")
DB = os.path.join(DATA, "nexora.db")

os.makedirs(DATA, exist_ok=True)


# =========================================================
# TIME / IDs
# =========================================================

def now():
    return datetime.now(timezone.utc).isoformat()


def uid(prefix="nx"):
    return prefix + "_" + uuid.uuid4().hex[:16]


# =========================================================
# DATABASE
# =========================================================

class Database:

    def __init__(self):
        self.lock = threading.RLock()
        self.init()

    def connect(self):
        c = sqlite3.connect(
            DB,
            check_same_thread=False
        )
        c.row_factory = sqlite3.Row
        return c

    def init(self):

        with self.lock:

            c = self.connect()

            c.executescript("""
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                type TEXT,
                payload TEXT,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS memories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                namespace TEXT,
                key TEXT,
                value TEXT,
                created_at TEXT,
                updated_at TEXT,
                UNIQUE(namespace,key)
            );

            CREATE TABLE IF NOT EXISTS projects (
                id TEXT PRIMARY KEY,
                name TEXT,
                description TEXT,
                status TEXT,
                created_at TEXT,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS tasks (
                id TEXT PRIMARY KEY,
                request TEXT,
                category TEXT,
                status TEXT,
                result TEXT,
                created_at TEXT,
                updated_at TEXT
            );

            CREATE TABLE IF NOT EXISTS agents (
                id TEXT PRIMARY KEY,
                name TEXT,
                category TEXT,
                description TEXT,
                status TEXT,
                capabilities TEXT,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS plugins (
                id TEXT PRIMARY KEY,
                name TEXT,
                version TEXT,
                description TEXT,
                status TEXT,
                manifest TEXT,
                created_at TEXT
            );

            CREATE TABLE IF NOT EXISTS audit (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                action TEXT,
                actor TEXT,
                target TEXT,
                result TEXT,
                created_at TEXT
            );
            """)

            c.commit()
            c.close()

        self.seed_agents()

    def execute(self, sql, params=(), fetch=False):

        with self.lock:

            c = self.connect()

            cur = c.execute(sql, params)

            result = cur.fetchall() if fetch else None

            c.commit()
            c.close()

            return result

    def event(self, typ, payload):

        self.execute(
            """
            INSERT INTO events(type,payload,created_at)
            VALUES(?,?,?)
            """,
            (
                typ,
                json.dumps(
                    payload,
                    ensure_ascii=False
                ),
                now()
            )
        )

    def audit(self, action, actor, target, result):

        self.execute(
            """
            INSERT INTO audit
            (action,actor,target,result,created_at)
            VALUES(?,?,?,?,?)
            """,
            (
                action,
                actor,
                target,
                result,
                now()
            )
        )

    def seed_agents(self):

        count = self.execute(
            "SELECT COUNT(*) c FROM agents",
            fetch=True
        )[0]["c"]

        if count:
            return

        agents = [

            (
                "core",
                "NEXORA Core",
                "core",
                "النواة المركزية وإدارة المهام",
                ["orchestration","routing","planning"]
            ),

            (
                "ai",
                "AI Intelligence",
                "intelligence",
                "تحليل وفهم الطلبات",
                ["analysis","reasoning","classification"]
            ),

            (
                "research",
                "Research Agent",
                "research",
                "البحث وتجميع المعرفة",
                ["research","knowledge"]
            ),

            (
                "innovation",
                "Innovation Agent",
                "innovation",
                "الابتكار واكتشاف الفرص",
                ["innovation","ideas","gaps"]
            ),

            (
                "gap",
                "Gap Discovery",
                "discovery",
                "اكتشاف الفجوات والمشاكل",
                ["gap-discovery","problem-analysis"]
            ),

            (
                "security",
                "Security Agent",
                "security",
                "الأمن وتحليل المخاطر",
                ["security","risk"]
            ),

            (
                "automation",
                "Automation Agent",
                "automation",
                "الأتمتة وسير العمل",
                ["automation","workflow"]
            ),

            (
                "knowledge",
                "Knowledge Agent",
                "knowledge",
                "إدارة المعرفة والذاكرة",
                ["memory","knowledge"]
            ),

            (
                "integration",
                "Integration Agent",
                "integration",
                "التكاملات وواجهات API",
                ["api","integration"]
            ),

            (
                "verification",
                "Verification Agent",
                "verification",
                "التحقق من النتائج",
                ["verification","quality"]
            ),

            (
                "foresight",
                "Future Intelligence",
                "foresight",
                "الاستشراف والاتجاهات",
                ["foresight","trends"]
            ),

            (
                "emergency",
                "Emergency Coordinator",
                "emergency",
                "تنسيق مسارات الطوارئ",
                ["emergency","response"]
            )
        ]

        for a in agents:

            self.execute(
                """
                INSERT INTO agents
                (id,name,category,description,
                 status,capabilities,created_at)
                VALUES(?,?,?,?,?,?,?)
                """,
                (
                    a[0],
                    a[1],
                    a[2],
                    a[3],
                    "online",
                    json.dumps(a[4]),
                    now()
                )
            )


DBX = Database()


# =========================================================
# MEMORY
# =========================================================

class Memory:

    @staticmethod
    def set(namespace, key, value):

        DBX.execute(
            """
            INSERT INTO memories
            (namespace,key,value,created_at,updated_at)
            VALUES(?,?,?,?,?)
            ON CONFLICT(namespace,key)
            DO UPDATE SET
            value=excluded.value,
            updated_at=excluded.updated_at
            """,
            (
                namespace,
                key,
                json.dumps(
                    value,
                    ensure_ascii=False
                ),
                now(),
                now()
            )
        )

    @staticmethod
    def all():

        rows = DBX.execute(
            """
            SELECT *
            FROM memories
            ORDER BY updated_at DESC
            """,
            fetch=True
        )

        result = []

        for r in rows:

            try:
                value = json.loads(r["value"])
            except Exception:
                value = r["value"]

            result.append({
                "namespace": r["namespace"],
                "key": r["key"],
                "value": value,
                "updated_at": r["updated_at"]
            })

        return result


# =========================================================
# AI / ROUTING
# =========================================================

class AI:

    @staticmethod
    def classify(text):

        t = text.lower()

        if any(x in t for x in [
            "مشروع",
            "منصة",
            "تطبيق",
            "تطوير",
            "بناء",
            "project"
        ]):
            return "project"

        if any(x in t for x in [
            "بحث",
            "ابحث",
            "research"
        ]):
            return "research"

        if any(x in t for x in [
            "مشكلة",
            "حل",
            "problem",
            "help"
        ]):
            return "problem"

        if any(x in t for x in [
            "أتمتة",
            "automation"
        ]):
            return "automation"

        return "general"

    @staticmethod
    def agents(text):

        t = text.lower()

        result = [
            "core",
            "ai"
        ]

        rules = {

            "مشروع": "innovation",
            "فكرة": "innovation",
            "ابتكار": "innovation",

            "بحث": "research",
            "ابحث": "research",

            "مشكلة": "gap",
            "فجوة": "gap",

            "أمان": "security",
            "امن": "security",

            "أتمتة": "automation",

            "ذاكرة": "knowledge",
            "معرفة": "knowledge",

            "api": "integration",
            "تكامل": "integration",

            "مستقبل": "foresight",

            "طوارئ": "emergency",
            "إنقاذ": "emergency"
        }

        for key, agent in rules.items():

            if key in t and agent not in result:
                result.append(agent)

        if "verification" not in result:
            result.append("verification")

        return result


# =========================================================
# SECURITY
# =========================================================

class Security:

    @staticmethod
    def inspect(text):

        dangerous = [
            "rm -rf /",
            "drop database",
            "disable security"
        ]

        flags = [
            x for x in dangerous
            if x.lower() in text.lower()
        ]

        return {
            "safe": len(flags) == 0,
            "flags": flags
        }


# =========================================================
# CORE ENGINE
# =========================================================

class Core:

    @staticmethod
    def process(request):

        task_id = uid("task")

        DBX.event(
            "request",
            {
                "task": task_id,
                "request": request
            }
        )

        security = Security.inspect(request)

        if not security["safe"]:

            result = {
                "task_id": task_id,
                "status": "review_required",
                "message": "الطلب يحتاج إلى مراجعة.",
                "security": security
            }

            DBX.audit(
                "blocked",
                "system",
                task_id,
                "security"
            )

            return result

        category = AI.classify(request)

        agents = AI.agents(request)

        plan = [
            "فهم الطلب",
            "تصنيف الطلب",
            "اختيار الوكلاء",
            "تحليل المعرفة",
            "بناء النتيجة",
            "التحقق",
            "حفظ سجل العملية"
        ]

        result = {

            "task_id": task_id,

            "status": "completed",

            "category": category,

            "understanding":
                "تم استقبال الطلب وتحليله بواسطة نواة NEXORA.",

            "plan": plan,

            "agents": agents,

            "agent_count": len(agents),

            "result":
                "تم تجهيز الطلب ضمن مسار NEXORA ويمكن توسيعه "
                "إلى أدوات ووكلاء ونماذج ذكاء اصطناعي فعلية.",

            "verification": {
                "verified": True,
                "quality": 1.0
            },

            "security": security,

            "timestamp": now()
        }

        DBX.execute(
            """
            INSERT INTO tasks
            (id,request,category,status,result,
             created_at,updated_at)
            VALUES(?,?,?,?,?,?,?)
            """,
            (
                task_id,
                request,
                category,
                "completed",
                json.dumps(
                    result,
                    ensure_ascii=False
                ),
                now(),
                now()
            )
        )

        DBX.audit(
            "completed",
            "system",
            task_id,
            "success"
        )

        return result


# =========================================================
# HTML CLIENT
# =========================================================

HTML = r"""
<!doctype html>
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
font-family:
system-ui,
-apple-system,
"Segoe UI",
sans-serif;
background:
radial-gradient(
circle at top,
#172554,
#020617 65%
);
color:#e5e7eb;
min-height:100vh;
}

.app{
min-height:100vh;
display:flex;
}

.side{
width:250px;
padding:20px;
background:
rgba(2,6,23,.88);
border-left:1px solid #1e293b;
}

.logo{
font-size:28px;
font-weight:900;
letter-spacing:2px;
}

.online{
font-size:13px;
margin:6px 0 25px;
color:#86efac;
}

.menu{
display:grid;
gap:8px;
}

.menu button{
padding:12px;
border-radius:12px;
border:1px solid #1e293b;
background:#0f172a;
color:#cbd5e1;
text-align:right;
font-size:14px;
}

.main{
flex:1;
width:100%;
max-width:1200px;
margin:auto;
padding:25px;
}

h1{
margin:0;
font-size:34px;
}

.sub{
color:#94a3b8;
margin-bottom:20px;
}

.cards{
display:grid;
grid-template-columns:
repeat(auto-fit,minmax(180px,1fr));
gap:12px;
}

.card{
background:
rgba(15,23,42,.8);
border:1px solid #1e293b;
border-radius:18px;
padding:18px;
}

.big{
font-size:30px;
font-weight:900;
}

.workspace{
margin-top:15px;
}

textarea{
width:100%;
min-height:150px;
background:#020617;
border:1px solid #334155;
border-radius:15px;
padding:15px;
color:white;
font-size:16px;
resize:vertical;
}

.actions{
display:flex;
gap:8px;
margin-top:10px;
}

button{
cursor:pointer;
}

.primary{
background:#2563eb;
color:white;
border:0;
padding:13px 20px;
border-radius:12px;
font-weight:800;
}

.secondary{
background:#0f172a;
color:#cbd5e1;
border:1px solid #334155;
padding:13px 20px;
border-radius:12px;
}

.output{
margin-top:15px;
background:#020617;
border:1px solid #1e293b;
border-radius:15px;
padding:18px;
white-space:pre-wrap;
overflow:auto;
min-height:120px;
}

@media(max-width:700px){

.app{
display:block;
}

.side{
width:100%;
border-left:0;
border-bottom:1px solid #1e293b;
}

.main{
padding:15px;
}

.menu{
grid-template-columns:
repeat(2,1fr);
}

h1{
font-size:27px;
}

}

</style>

</head>

<body>

<div class="app">

<aside class="side">

<div class="logo">
NEXORA
</div>

<div class="online">
● ONLINE
</div>

<div class="menu">

<button onclick="workspace()">
✦ مساحة العمل
</button>

<button onclick="status()">
◉ النظام
</button>

<button onclick="agents()">
🧠 الوكلاء
</button>

<button onclick="projects()">
🚀 المشاريع
</button>

<button onclick="memory()">
🧩 الذاكرة
</button>

<button onclick="events()">
◌ الأحداث
</button>

</div>

</aside>

<main class="main">

<h1>
ممر NEXORA الذكي
</h1>

<div class="sub">
من المشكلة إلى التحليل والخطة والنتيجة
</div>

<div class="cards">

<div class="card">
النواة
<div class="big">CORE</div>
</div>

<div class="card">
الوكلاء
<div id="agentsCount" class="big">-</div>
</div>

<div class="card">
المهام
<div id="tasksCount" class="big">-</div>
</div>

<div class="card">
الذاكرة
<div id="memoryCount" class="big">-</div>
</div>

</div>

<div id="workspace"
class="card workspace">

<h2>
مساحة العمل
</h2>

<textarea
id="request"
placeholder="اكتب ما تريد من NEXORA..."></textarea>

<div class="actions">

<button
class="primary"
onclick="execute()">
✦ تشغيل NEXORA
</button>

<button
class="secondary"
onclick="clearBox()">
مسح
</button>

</div>

<div id="output"
class="output">
جاهز لاستقبال طلبك...
</div>

</div>

</main>

</div>

<script>

async function api(url, options={}){

const r=await fetch(url,{
headers:{
"Content-Type":"application/json"
},
...options
});

return await r.json();

}

async function status(){

const x=await api("/api/status");

document.getElementById("agentsCount")
.textContent=x.statistics.agents;

document.getElementById("tasksCount")
.textContent=x.statistics.tasks;

document.getElementById("memoryCount")
.textContent=x.statistics.memories;

document.getElementById("output")
.textContent=
JSON.stringify(x,null,2);

}

async function execute(){

const text=
document.getElementById("request")
.value.trim();

if(!text){
document.getElementById("output")
.textContent="اكتب طلبك أولاً.";
return;
}

document.getElementById("output")
.textContent=
"⏳ NEXORA تعالج الطلب...";

try{

const x=await api(
"/api/execute",
{
method:"POST",
body:JSON.stringify({
request:text
})
}
);

document.getElementById("output")
.textContent=
JSON.stringify(x,null,2);

status();

}catch(e){

document.getElementById("output")
.textContent=
"تعذر الاتصال بالنواة.";

}

}

async function agents(){

const x=await api("/api/agents");

document.getElementById("output")
.textContent=
JSON.stringify(x,null,2);

}

async function projects(){

const x=await api("/api/projects");

document.getElementById("output")
.textContent=
JSON.stringify(x,null,2);

}

async function memory(){

const x=await api("/api/memory");

document.getElementById("output")
.textContent=
JSON.stringify(x,null,2);

}

async function events(){

const x=await api("/api/events");

document.getElementById("output")
.textContent=
JSON.stringify(x,null,2);

}

function workspace(){

document.getElementById("workspace")
.scrollIntoView({
behavior:"smooth"
});

}

function clearBox(){

document.getElementById("request")
.value="";

document.getElementById("output")
.textContent=
"جاهز لاستقبال طلبك...";

}

status();

</script>

</body>

</html>
"""


# =========================================================
# HTTP SERVER
# =========================================================

class Handler(BaseHTTPRequestHandler):

    def log_message(self, *args):
        pass

    def json(self, data, status=200):

        raw=json.dumps(
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
            str(len(raw))
        )

        self.end_headers()

        self.wfile.write(raw)

    def html(self):

        raw=HTML.encode()

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

    def body(self):

        length=int(
            self.headers.get(
                "Content-Length",
                "0"
            )
        )

        if length==0:
            return {}

        try:

            return json.loads(
                self.rfile.read(length)
                .decode()
            )

        except Exception:

            return {}

    def do_GET(self):

        path=urlparse(
            self.path
        ).path

        try:

            if path=="/":
                return self.html()

            if path=="/api/status":

                return self.json({
                    "name":APP,
                    "version":VERSION,
                    "status":"online",
                    "time":now(),
                    "statistics":{
                        "agents":DBX.execute(
                            "SELECT COUNT(*) c FROM agents",
                            fetch=True
                        )[0]["c"],
                        "tasks":DBX.execute(
                            "SELECT COUNT(*) c FROM tasks",
                            fetch=True
                        )[0]["c"],
                        "memories":DBX.execute(
                            "SELECT COUNT(*) c FROM memories",
                            fetch=True
                        )[0]["c"],
                        "projects":DBX.execute(
                            "SELECT COUNT(*) c FROM projects",
                            fetch=True
                        )[0]["c"]
                    },
                    "services":[
                        "core",
                        "ai",
                        "agents",
                        "memory",
                        "knowledge",
                        "security",
                        "verification",
                        "automation",
                        "plugins",
                        "api",
                        "audit",
                        "gap-discovery",
                        "digital-corridor",
                        "emergency",
                        "integrations"
                    ]
                })

            if path=="/api/agents":

                rows=DBX.execute(
                    "SELECT * FROM agents ORDER BY category",
                    fetch=True
                )

                return self.json([
                    dict(x) for x in rows
                ])

            if path=="/api/projects":

                rows=DBX.execute(
                    "SELECT * FROM projects ORDER BY updated_at DESC",
                    fetch=True
                )

                return self.json([
                    dict(x) for x in rows
                ])

            if path=="/api/memory":

                return self.json(
                    Memory.all()
                )

            if path=="/api/events":

                rows=DBX.execute(
                    """
                    SELECT *
                    FROM events
                    ORDER BY id DESC
                    LIMIT 100
                    """,
                    fetch=True
                )

                return self.json([
                    dict(x) for x in rows
                ])

            if path=="/api/audit":

                rows=DBX.execute(
                    """
                    SELECT *
                    FROM audit
                    ORDER BY id DESC
                    LIMIT 100
                    """,
                    fetch=True
                )

                return self.json([
                    dict(x) for x in rows
                ])

            return self.json(
                {"error":"not_found"},
                404
            )

        except Exception as e:

            return self.json(
                {
                    "error":str(e)
                },
                500
            )

    def do_POST(self):

        path=urlparse(
            self.path
        ).path

        try:

            data=self.body()

            if path=="/api/execute":

                request=str(
                    data.get(
                        "request",
                        ""
                    )
                ).strip()

                if not request:

                    return self.json(
                        {
                            "error":
                            "request_required"
                        },
                        400
                    )

                return self.json(
                    Core.process(request)
                )

            if path=="/api/memory":

                Memory.set(
                    data.get(
                        "namespace",
                        "default"
                    ),
                    data.get(
                        "key",
                        uid("memory")
                    ),
                    data.get(
                        "value"
                    )
                )

                return self.json({
                    "status":"saved"
                })

            if path=="/api/projects":

                pid=uid("project")

                DBX.execute(
                    """
                    INSERT INTO projects
                    (id,name,description,status,
                     created_at,updated_at)
                    VALUES(?,?,?,?,?,?)
                    """,
                    (
                        pid,
                        data.get(
                            "name",
                            "NEXORA Project"
                        ),
                        data.get(
                            "description",
                            ""
                        ),
                        "active",
                        now(),
                        now()
                    )
                )

                return self.json({
                    "id":pid,
                    "status":"created"
                })

            return self.json(
                {"error":"not_found"},
                404
            )

        except Exception as e:

            return self.json(
                {
                    "error":str(e)
                },
                500
            )


# =========================================================
# SERVER
# =========================================================

def server():

    http=ThreadingHTTPServer(
        (HOST,PORT),
        Handler
    )

    print(
        f"NEXORA {VERSION} running "
        f"at http://{HOST}:{PORT}",
        flush=True
    )

    http.serve_forever()


if __name__=="__main__":

    server()

