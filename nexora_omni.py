#!/usr/bin/env python3

import os
import json
import time
import sqlite3
import threading
import urllib.request
import urllib.error
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ============================================================
# NEXORA OMNI
# ============================================================

HOST = "0.0.0.0"
PORT = 8080

BASE_DIR = os.path.expanduser("~/NEXORA")
DB_FILE = os.path.join(BASE_DIR, "nexora_omni.db")

# ============================================================
# 🔴 مفتاح OpenAI
#
# لا تضع المفتاح الحقيقي هنا.
#
# ضعه في Termux قبل التشغيل:
#
# export OPENAI_API_KEY='ضع_مفتاحك_هنا'
#
# ============================================================

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()

# اسم النموذج منفصل عن المفتاح
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-5")

START_TIME = time.time()

TOOLS = [
    "INTELLIGENCE",
    "ANALYSIS",
    "PLANNING",
    "MEMORY",
    "VERIFICATION",
    "AUTOMATION",
    "API",
    "UI",
]

lock = threading.Lock()


# ============================================================
# DATABASE
# ============================================================

def database():

    os.makedirs(BASE_DIR, exist_ok=True)

    conn = sqlite3.connect(DB_FILE)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS conversations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            role TEXT NOT NULL,
            message TEXT NOT NULL,
            created_at INTEGER NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event TEXT NOT NULL,
            created_at INTEGER NOT NULL
        )
    """)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at INTEGER NOT NULL
        )
    """)

    conn.commit()

    return conn


def save_conversation(role, message):

    conn = database()

    conn.execute(
        """
        INSERT INTO conversations(role,message,created_at)
        VALUES(?,?,?)
        """,
        (
            role,
            message,
            int(time.time())
        )
    )

    conn.commit()
    conn.close()


def save_event(event_name):

    conn = database()

    conn.execute(
        """
        INSERT INTO events(event,created_at)
        VALUES(?,?)
        """,
        (
            event_name,
            int(time.time())
        )
    )

    conn.commit()
    conn.close()


def create_task(task):

    conn = database()

    cur = conn.execute(
        """
        INSERT INTO tasks(task,status,created_at)
        VALUES(?,?,?)
        """,
        (
            task,
            "processing",
            int(time.time())
        )
    )

    task_id = cur.lastrowid

    conn.commit()
    conn.close()

    return task_id


def finish_task(task_id, status):

    conn = database()

    conn.execute(
        """
        UPDATE tasks
        SET status=?
        WHERE id=?
        """,
        (
            status,
            task_id
        )
    )

    conn.commit()
    conn.close()


# ============================================================
# OPENAI
# ============================================================

def ask_openai(message):

    if not OPENAI_API_KEY:

        return {
            "ok": False,
            "error": "OPENAI_API_KEY غير موجودة في بيئة Termux."
        }

    payload = {

        "model": OPENAI_MODEL,

        "input": [
            {
                "role": "system",
                "content":
                    "أنت العقل الذكي لمنظومة NEXORA. "
                    "أجب بالعربية عندما يكون الطلب بالعربية. "
                    "كن واضحًا وعمليًا ولا تدّعي تنفيذ شيء لم يتم تنفيذه."
            },
            {
                "role": "user",
                "content": message
            }
        ]
    }

    request = urllib.request.Request(

        "https://api.openai.com/v1/responses",

        data=json.dumps(payload).encode("utf-8"),

        headers={
            "Content-Type": "application/json",
            "Authorization":
                "Bearer " + OPENAI_API_KEY
        },

        method="POST"
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=90
        ) as response:

            data = json.loads(
                response.read().decode("utf-8")
            )

        answer = data.get(
            "output_text",
            ""
        ).strip()

        if not answer:

            for item in data.get("output", []):

                for content in item.get("content", []):

                    if content.get("type") == "output_text":

                        answer += content.get(
                            "text",
                            ""
                        )

        if not answer:

            answer = "تمت معالجة الطلب."

        return {
            "ok": True,
            "answer": answer,
            "model": OPENAI_MODEL
        }

    except urllib.error.HTTPError as error:

        body = error.read().decode(
            "utf-8",
            errors="replace"
        )

        return {
            "ok": False,
            "error":
                f"OpenAI HTTP {error.code}: {body[:1200]}"
        }

    except Exception as error:

        return {
            "ok": False,
            "error": str(error)
        }


# ============================================================
# HTML
# ============================================================

HTML = r"""
<!DOCTYPE html>

<html lang="ar" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport"
      content="width=device-width,initial-scale=1">

<title>NEXORA OMNI</title>

<style>

*{
    box-sizing:border-box;
}

html,
body{

    margin:0;

    min-height:100%;

    font-family:
        system-ui,
        -apple-system,
        "Segoe UI",
        sans-serif;

    background:#020617;

    color:#f8fafc;
}

body{

    overflow-x:hidden;

}

button,
textarea{

    font:inherit;

}

.app{

    min-height:100vh;

    background:

        radial-gradient(
            circle at 50% -15%,
            #164e63 0,
            #07111f 28%,
            #020617 70%
        );

}

nav{

    position:sticky;

    top:0;

    z-index:50;

    height:70px;

    padding:0 20px;

    display:flex;

    align-items:center;

    justify-content:space-between;

    background:
        rgba(2,6,23,.78);

    backdrop-filter:
        blur(22px);

    border-bottom:
        1px solid #1e293b;

}

.logo{

    font-size:22px;

    font-weight:1000;

    letter-spacing:1px;

}

.logo span{

    color:#67e8f9;

}

.status{

    padding:
        8px 13px;

    border-radius:
        999px;

    font-size:
        12px;

    color:#86efac;

    background:#052e1b;

    border:
        1px solid #166534;

}

main{

    width:
        min(1150px,94%);

    margin:auto;

    padding:
        45px 0 80px;

}

.hero{

    text-align:center;

    padding:
        20px 0 35px;

}

.badge{

    display:inline-block;

    padding:
        8px 15px;

    border-radius:
        999px;

    border:
        1px solid #155e75;

    color:#67e8f9;

    background:#061522;

    font-size:12px;

}

h1{

    font-size:
        clamp(43px,9vw,82px);

    line-height:
        1.02;

    letter-spacing:
        -3px;

    margin:
        20px 0;

}

h1 span{

    color:#67e8f9;

}

.hero p{

    max-width:720px;

    margin:auto;

    color:#94a3b8;

    line-height:1.9;

    font-size:17px;

}

.command{

    max-width:900px;

    margin:
        30px auto;

    padding:18px;

    border:
        1px solid #263247;

    background:
        rgba(10,16,28,.9);

    border-radius:28px;

    box-shadow:
        0 30px 100px #000b;

}

textarea{

    width:100%;

    min-height:150px;

    resize:vertical;

    border:0;

    outline:0;

    border-radius:20px;

    background:#050a13;

    color:#fff;

    padding:20px;

    font-size:17px;

    line-height:1.8;

}

textarea::placeholder{

    color:#64748b;

}

.actions{

    display:flex;

    gap:10px;

    margin-top:12px;

}

button{

    border:0;

    cursor:pointer;

    border-radius:16px;

    padding:14px 18px;

    font-weight:900;

}

.primary{

    flex:1;

    color:#041018;

    background:
        linear-gradient(
            90deg,
            #22d3ee,
            #818cf8
        );

}

.secondary{

    background:#172033;

    color:#cbd5e1;

}

.result{

    display:none;

    margin-top:18px;

    padding:20px;

    border-radius:20px;

    background:#07101c;

    border:
        1px solid #155e75;

}

.result.show{

    display:block;

}

.answer{

    white-space:pre-wrap;

    line-height:1.9;

    color:#e2e8f0;

}

.thinking{

    color:#67e8f9;

}

.dashboard{

    display:grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(180px,1fr)
        );

    gap:12px;

    margin:
        25px auto;

}

.metric{

    padding:18px;

    border:
        1px solid #1e293b;

    background:#0a101c;

    border-radius:20px;

}

.metric small{

    color:#64748b;

}

.metric strong{

    display:block;

    margin-top:8px;

    font-size:23px;

}

.tools{

    display:grid;

    grid-template-columns:
        repeat(
            auto-fit,
            minmax(220px,1fr)
        );

    gap:14px;

    margin-top:25px;

}

.tool{

    padding:23px;

    border:
        1px solid #1e293b;

    background:#0a101c;

    border-radius:21px;

    transition:
        .25s;

}

.tool:hover{

    transform:
        translateY(-4px);

    border-color:#155e75;

}

.tool h3{

    margin:
        10px 0 7px;

}

.tool p{

    margin:0;

    color:#94a3b8;

    line-height:1.7;

    font-size:14px;

}

.icon{

    font-size:28px;

}

.footer{

    text-align:center;

    color:#475569;

    margin-top:60px;

    font-size:12px;

}

@media(max-width:650px){

    nav{

        padding:
            0 12px;

    }

    h1{

        letter-spacing:-2px;

    }

}

</style>

</head>

<body>

<div class="app">

<nav>

<div class="logo">
NEXORA <span>OMNI</span>
</div>

<div
    id="status"
    class="status">
● جاري الفحص
</div>

</nav>

<main>

<section class="hero">

<div class="badge">
INTELLIGENCE • AUTOMATION • RESULTS
</div>

<h1>
من المشكلة<br>
<span>إلى النتيجة.</span>
</h1>

<p>
مركز القيادة الذكي لـ NEXORA.
اكتب هدفك ودع العقل الخارجي يساعدك في التحليل والتخطيط والحل.
</p>

</section>


<section class="command">

<textarea
id="prompt"
placeholder="اكتب ما تريد من NEXORA...

مثال:
حلل مشروعي وحدد أهم الخطوات التالية."
></textarea>

<div class="actions">

<button
class="primary"
onclick="ask()">
🧠 تشغيل NEXORA
</button>

<button
class="secondary"
onclick="clearCommand()">
مسح
</button>

</div>

<div
id="result"
class="result">

<div
id="answer"
class="answer">
</div>

</div>

</section>


<section class="dashboard">

<div class="metric">

<small>CORE</small>

<strong id="core">
—
</strong>

</div>

<div class="metric">

<small>AI</small>

<strong id="ai">
—
</strong>

</div>

<div class="metric">

<small>TOOLS</small>

<strong id="tools">
—
</strong>

</div>

<div class="metric">

<small>UPTIME</small>

<strong id="uptime">
—
</strong>

</div>

</section>


<section class="tools">

<div class="tool">

<div class="icon">
🧠
</div>

<h3>
ذكاء
</h3>

<p>
طبقة الاتصال بالعقل الخارجي ومعالجة الطلبات.
</p>

</div>


<div class="tool">

<div class="icon">
🤖
</div>

<h3>
وكلاء
</h3>

<p>
بنية قابلة لإضافة وكلاء متخصصة مستقبلًا.
</p>

</div>


<div class="tool">

<div class="icon">
⚙️
</div>

<h3>
أتمتة
</h3>

<p>
إطار جاهز لربط أدوات تنفيذ حقيقية مع صلاحيات واضحة.
</p>

</div>


<div class="tool">

<div class="icon">
💾
</div>

<h3>
ذاكرة
</h3>

<p>
تخزين المحادثات والأحداث والمهام محليًا.
</p>

</div>


<div class="tool">

<div class="icon">
🛡️
</div>

<h3>
تحقق
</h3>

<p>
فصل مرحلة معالجة الطلب عن حالة التنفيذ والتحقق.
</p>

</div>


<div class="tool">

<div class="icon">
⚡
</div>

<h3>
تحديث حي
</h3>

<p>
تحديث حالة المنظومة تلقائيًا كل ثانية.
</p>

</div>

</section>


<div class="footer">
NEXORA OMNI © 2026
</div>

</main>

</div>


<script>

async function refresh(){

    try{

        const response =
            await fetch(
                "/api/status",
                {cache:"no-store"}
            );

        const data =
            await response.json();

        document
            .getElementById("status")
            .textContent =
                data.ai_ready
                ? "● الذكاء متصل"
                : "● المنظومة متاحة";

        document
            .getElementById("core")
            .textContent =
                data.status;

        document
            .getElementById("ai")
            .textContent =
                data.ai_ready
                ? "READY"
                : "OFF";

        document
            .getElementById("tools")
            .textContent =
                data.tools;

        document
            .getElementById("uptime")
            .textContent =
                data.uptime + "s";

    }catch(error){

        document
            .getElementById("status")
            .textContent =
                "● غير متصل";

    }

}


async function ask(){

    const input =
        document
            .getElementById("prompt");

    const result =
        document
            .getElementById("result");

    const answer =
        document
            .getElementById("answer");

    const message =
        input.value.trim();

    if(!message){

        input.focus();

        return;

    }

    result.classList.add("show");

    answer.innerHTML =
        '<span class="thinking">🧠 NEXORA تعمل...</span>';

    try{

        const response =
            await fetch(
                "/api/ask",
                {
                    method:"POST",

                    headers:{
                        "Content-Type":
                            "application/json"
                    },

                    body:
                        JSON.stringify({
                            message:message
                        })
                }
            );

        const data =
            await response.json();

        if(!response.ok || !data.ok){

            throw new Error(
                data.error ||
                "تعذر تنفيذ الطلب"
            );

        }

        answer.textContent =
            data.answer;

    }catch(error){

        answer.textContent =
            "تعذر الاتصال بالعقل الخارجي.\n\n" +
            error.message;

    }

    refresh();

}


function clearCommand(){

    document
        .getElementById("prompt")
        .value="";

    document
        .getElementById("answer")
        .textContent="";

    document
        .getElementById("result")
        .classList.remove("show");

}


document
    .getElementById("prompt")
    .addEventListener(
        "keydown",
        function(event){

            if(
                (event.ctrlKey ||
                 event.metaKey) &&
                event.key === "Enter"
            ){

                ask();

            }

        }
    );


refresh();

setInterval(
    refresh,
    1000
);

</script>

</body>

</html>
"""


# ============================================================
# HTTP SERVER
# ============================================================

class Handler(BaseHTTPRequestHandler):

    def json_response(self, data, status=200):

        body = json.dumps(
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

        self.send_header(
            "Cache-Control",
            "no-store"
        )

        self.end_headers()

        self.wfile.write(body)


    def do_GET(self):

        if self.path == "/api/status":

            self.json_response({

                "status":
                    "online",

                "ai_ready":
                    bool(OPENAI_API_KEY),

                "model":
                    OPENAI_MODEL,

                "tools":
                    len(TOOLS),

                "uptime":
                    int(
                        time.time()
                        - START_TIME
                    ),

                "timestamp":
                    int(time.time())

            })

            return


        body = HTML.encode(
            "utf-8"
        )

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


    def do_POST(self):
        if self.path != "/api/ask":
            self.json_response(
                {"ok": False, "error": "not_found"},
                404,
            )
            return

        try:
            length = int(self.headers.get("Content-Length", "0"))
            raw = self.rfile.read(length)
            data = json.loads(raw.decode("utf-8"))
            message = str(data.get("message", "")).strip()

            if not message:
                self.json_response(
                    {"ok": False, "error": "empty_message"},
                    400,
                )
                return

            task_id = create_task(message)
            save_conversation("user", message)
            save_event("task_received")
            result = ask_openai(message)

            if result["ok"]:
                save_conversation("assistant", result["answer"])
                finish_task(task_id, "completed")
                save_event("task_completed")
                self.json_response(result)
            else:
                finish_task(task_id, "error")
                save_event("ai_error")
                self.json_response(result, 502)

        except Exception as error:
            self.json_response(
                {"ok": False, "error": str(error)},
                500,
            )


    def log_message(
        self,
        format,
        *args
    ):

        return


# ============================================================
# START
# ============================================================

def main():

    database().close()

    print()
    print("=" * 60)
    print("NEXORA OMNI")
    print("=" * 60)
    print(
        "AI:",
        "READY"
        if OPENAI_API_KEY
        else "NOT SET"
    )
    print(
        "MODEL:",
        OPENAI_MODEL
    )
    print(
        "URL:",
        f"http://127.0.0.1:{PORT}"
    )
    print("=" * 60)

    server =
        ThreadingHTTPServer(
            (HOST,PORT),
            Handler
        )

    server.serve_forever()


if __name__ == "__main__":

    main()

