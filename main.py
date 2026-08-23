#!/usr/bin/env python3
import os
import json
import time
import sqlite3
import ast
import logging
import http.server
import socketserver

DB_FILE = "nexora.db"
HOST = "0.0.0.0"
PORT = 8090

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
    datefmt="%H:%M:%S"
)

# ------------------------------------------------------------
# Hugging Face
# ------------------------------------------------------------

HF_AVAILABLE = False

try:
    from huggingface_hub import InferenceClient
    HF_AVAILABLE = True
except ImportError:
    pass

HF_TOKEN = os.environ.get("HF_TOKEN", "").strip()

MODELS = {
    "code": "Qwen/Qwen2.5-Coder-32B-Instruct",
    "reasoning": "deepseek-ai/DeepSeek-R1",
    "general": "meta-llama/Llama-3.3-70B-Instruct"
}

# ------------------------------------------------------------
# 1000 وكلاء موزعون على مهام فعلية
# ------------------------------------------------------------

AGENT_DOMAINS = [
    ("CORE", "النواة والمنطق الداخلي"),
    ("SECURITY", "الأمن والحماية"),
    ("CODE", "هندسة البرمجيات"),
    ("DEBUG", "كشف الأخطاء"),
    ("API", "واجهات API والتكامل"),
    ("DATABASE", "قواعد البيانات"),
    ("PERFORMANCE", "الأداء والتحسين"),
    ("AUTOMATION", "الأتمتة"),
    ("RESEARCH", "البحث والتحليل"),
    ("AI", "الذكاء الاصطناعي"),
    ("PRODUCT", "تطوير المنتجات"),
    ("UX", "تجربة المستخدم"),
    ("WEB", "الويب"),
    ("MOBILE", "تطبيقات الهاتف"),
    ("DEVOPS", "التشغيل والنشر"),
    ("MONITORING", "المراقبة"),
    ("TESTING", "الاختبارات"),
    ("DOCUMENTATION", "التوثيق"),
    ("MARKET", "تحليل السوق"),
    ("INNOVATION", "الابتكار"),
]

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    cur.execute("""
        CREATE TABLE IF NOT EXISTS agents (
            id INTEGER PRIMARY KEY,
            agent_id TEXT UNIQUE,
            domain TEXT,
            name TEXT,
            role TEXT,
            model TEXT,
            status TEXT DEFAULT 'ONLINE'
        )
    """)

    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            agent_id TEXT,
            task TEXT,
            result TEXT,
            created_at REAL
        )
    """)

    count = cur.execute(
        "SELECT COUNT(*) FROM agents"
    ).fetchone()[0]

    if count < 1000:
        for i in range(1, 1001):
            domain, description = AGENT_DOMAINS[(i - 1) % len(AGENT_DOMAINS)]

            if domain in ("CODE", "DEBUG"):
                model = MODELS["code"]
            elif domain in ("AI", "RESEARCH", "INNOVATION"):
                model = MODELS["reasoning"]
            else:
                model = MODELS["general"]

            cur.execute("""
                INSERT OR IGNORE INTO agents
                (id, agent_id, domain, name, role, model, status)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                i,
                f"AGENT_{i:04d}",
                domain,
                f"NEXORA-{domain}-{i:04d}",
                description,
                model,
                "ONLINE"
            ))

    conn.commit()
    conn.close()

# ------------------------------------------------------------
# اختيار الوكيل
# ------------------------------------------------------------

def route_agent(prompt):
    p = prompt.lower()

    rules = [
        (["security", "hack", "attack", "أمن", "حماية"], "SECURITY"),
        (["python", "javascript", "code", "برمج", "كود"], "CODE"),
        (["error", "bug", "debug", "خطأ", "تصحيح"], "DEBUG"),
        (["api", "endpoint", "واجهة"], "API"),
        (["sql", "database", "قاعدة", "بيانات"], "DATABASE"),
        (["speed", "performance", "سرعة", "أداء"], "PERFORMANCE"),
        (["automation", "أتمتة", "تشغيل تلقائي"], "AUTOMATION"),
        (["research", "بحث", "تحليل"], "RESEARCH"),
        (["ai", "ذكاء اصطناعي", "model", "نموذج"], "AI"),
        (["website", "web", "موقع", "ويب"], "WEB"),
        (["android", "mobile", "هاتف", "تطبيق"], "MOBILE"),
        (["test", "testing", "اختبار"], "TESTING"),
        (["market", "سوق", "business", "مشروع"], "MARKET"),
        (["idea", "ابتكار", "فكرة"], "INNOVATION"),
    ]

    domain = "CORE"

    for keywords, target in rules:
        if any(k in p for k in keywords):
            domain = target
            break

    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()

    agent = cur.execute("""
        SELECT agent_id, name, role, model, domain
        FROM agents
        WHERE domain = ?
        ORDER BY RANDOM()
        LIMIT 1
    """, (domain,)).fetchone()

    conn.close()

    if not agent:
        return None

    return {
        "id": agent[0],
        "name": agent[1],
        "role": agent[2],
        "model": agent[3],
        "domain": agent[4]
    }

# ------------------------------------------------------------
# فحص Python محلي
# ------------------------------------------------------------

def local_engine(prompt):
    try:
        tree = ast.parse(prompt)

        return (
            "تم فحص الإدخال بواسطة المحرك المحلي. "
            "تم التعرف على بنية Python صحيحة."
        ), (
            "# NEXORA LOCAL ANALYSIS\n"
            "# Syntax: VALID\n\n"
            f"{prompt}\n\n"
            "# انتهى الفحص المحلي."
        )

    except SyntaxError as e:

        line = e.lineno or 0

        response = (
            f"تم اكتشاف SyntaxError في السطر {line}: "
            f"{e.msg}"
        )

        lines = prompt.splitlines()

        if line > 0 and line <= len(lines):
            bad = lines[line - 1]

            if any(
                bad.strip().startswith(x)
                for x in (
                    "if ",
                    "for ",
                    "while ",
                    "def ",
                    "class ",
                    "elif ",
                    "else"
                )
            ) and not bad.rstrip().endswith(":"):
                lines[line - 1] = bad + ":"

        result = "\n".join(lines)

        return response, result

    except Exception as e:
        return (
            "تمت معالجة الطلب بواسطة المحرك المحلي.",
            prompt
        )

# ------------------------------------------------------------
# Hugging Face
# ------------------------------------------------------------

def hf_engine(prompt, model):
    if not HF_AVAILABLE:
        return None

    if not HF_TOKEN:
        return None

    try:
        client = InferenceClient(
            token=HF_TOKEN,
            model=model
        )

        response = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are NEXORA, an expert engineering "
                        "assistant. Analyze the request and provide "
                        "a useful safe solution."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            max_tokens=700
        )

        text = response.choices[0].message.content

        return (
            "تمت المعالجة عبر Hugging Face.",
            text
        )

    except Exception as e:

        logging.warning(
            "Hugging Face unavailable: %s",
            str(e)
        )

        return None

# ------------------------------------------------------------
# المحرك الرئيسي
# ------------------------------------------------------------

def process_request(prompt):

    started = time.time()

    agent = route_agent(prompt)

    if not agent:
        return {
            "status": "ERROR",
            "response": "تعذر اختيار وكيل.",
            "result": ""
        }

    hf_result = hf_engine(
        prompt,
        agent["model"]
    )

    if hf_result:
        response, result = hf_result
        engine = "Hugging Face"
    else:
        response, result = local_engine(prompt)
        engine = "NEXORA Local Engine"

    elapsed = round(
        (time.time() - started) * 1000,
        2
    )

    conn = sqlite3.connect(DB_FILE)

    conn.execute("""
        INSERT INTO tasks
        (agent_id, task, result, created_at)
        VALUES (?, ?, ?, ?)
    """, (
        agent["id"],
        prompt,
        result,
        time.time()
    ))

    conn.commit()
    conn.close()

    return {
        "status": "SUCCESS",

        "response": response,

        "result": result,

        "engine": engine,

        "execution_time_ms": elapsed,

        "agent": agent
    }

# ------------------------------------------------------------
# واجهة NEXORA
# ------------------------------------------------------------

HTML = r"""
<!DOCTYPE html>
<html lang="ar" dir="rtl">

<head>

<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>NEXORA OMNI</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    padding: 15px;
    background: #020617;
    color: #f8fafc;
    font-family: Arial, sans-serif;
}

.header {
    background:
    radial-gradient(
        circle at center,
        #0369a1,
        #020617 70%
    );

    border: 1px solid #164e63;
    border-radius: 18px;
    padding: 22px;
    text-align: center;
    margin-bottom: 15px;
}

.header h1 {
    margin: 0;
    font-size: 25px;
}

.status {
    display: inline-block;
    margin-top: 8px;
    padding: 5px 12px;
    border-radius: 20px;
    background: #064e3b;
    color: #6ee7b7;
    font-size: 12px;
}

.grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 15px;
}

.card {
    background: #0f172a;
    border: 1px solid #1e293b;
    border-radius: 15px;
    padding: 15px;
}

textarea {
    width: 100%;
    min-height: 130px;
    resize: vertical;

    background: #020617;
    color: white;

    border: 1px solid #334155;
    border-radius: 10px;

    padding: 12px;

    font-family: monospace;
    font-size: 14px;
}

button {
    width: 100%;
    margin-top: 8px;

    border: 0;
    border-radius: 9px;

    padding: 12px;

    background: linear-gradient(
        135deg,
        #0284c7,
        #0369a1
    );

    color: white;
    font-weight: bold;
    cursor: pointer;
}

button:hover {
    opacity: .9;
}

.output {
    position: relative;

    background: #020617;

    border: 1px solid #334155;

    border-radius: 10px;

    padding: 14px;

    margin-top: 10px;
}

.output-title {
    color: #38bdf8;
    font-weight: bold;
    border-bottom: 1px solid #1e293b;
    padding-bottom: 7px;
    margin-bottom: 8px;
}

.result-title {
    color: #10b981;
}

pre {
    direction: ltr;
    text-align: left;

    white-space: pre-wrap;
    overflow-x: auto;

    color: #38bdf8;

    font-family: monospace;
    font-size: 13px;
}

.copy {
    width: auto;

    position: absolute;

    left: 10px;
    top: 10px;

    margin: 0;

    padding: 6px 12px;

    background: #10b981;

    font-size: 11px;
}

.copy.ok {
    background: #0284c7;
}

.meta {
    color: #94a3b8;
    font-size: 11px;
    margin-top: 10px;
}

.chat {
    max-height: 220px;
    overflow-y: auto;

    background: #020617;

    border: 1px solid #1e293b;

    border-radius: 10px;

    padding: 10px;

    margin-bottom: 10px;
}

.message {
    padding: 9px;
    margin-bottom: 8px;

    border-radius: 8px;

    background: #172033;

    font-size: 13px;
}

@media(max-width:850px) {

    .grid {
        grid-template-columns: 1fr;
    }

}

</style>

</head>

<body>

<div class="header">

<h1>⚡ NEXORA OMNI</h1>

<div>
1000 وكيل • توجيه ذكي • محرك محلي • Hugging Face
</div>

<div class="status">
● النظام يعمل
</div>

</div>

<div class="grid">

<div class="card">

<h3>🎯 النتيجة</h3>

<div class="output">

<div class="output-title">
💬 الرد والتحليل
</div>

<div id="response">
بانتظار الطلب...
</div>

</div>

<div class="output">

<button
class="copy"
id="copyButton"
onclick="copyResult()">
نسخ النتيجة 📋
</button>

<div class="output-title result-title">
🎯 النتيجة الفعلية
</div>

<pre id="result">
ستظهر النتيجة هنا...
</pre>

</div>

<div
class="meta"
id="meta">
المحرك: بانتظار الطلب
</div>

</div>

<div class="card">

<h3>💬 NEXORA</h3>

<div class="chat" id="chat">

<div class="message">
أدخل طلبك أو الكود الذي تريد تحليله.
</div>

</div>

<textarea
id="prompt"
placeholder="اكتب طلبك هنا..."></textarea>

<button onclick="sendRequest()">
⚡ إرسال ومعالجة
</button>

</div>

</div>

<script>

async function sendRequest() {

    const input =
        document.getElementById("prompt");

    const text =
        input.value.trim();

    if (!text) return;

    const chat =
        document.getElementById("chat");

    chat.innerHTML +=
        `<div class="message">
        👤 ${escapeHtml(text)}
        </div>`;

    input.value = "";

    try {

        const response =
            await fetch("/api/process", {

                method: "POST",

                headers: {
                    "Content-Type":
                    "application/json"
                },

                body: JSON.stringify({
                    prompt: text
                })

            });

        const data =
            await response.json();

        document.getElementById(
            "response"
        ).innerText =
            data.response || "";

        document.getElementById(
            "result"
        ).innerText =
            data.result || "";

        if (data.agent) {

            document.getElementById(
                "meta"
            ).innerText =
                `🤖 ${data.agent.name} | ` +
                `المجال: ${data.agent.domain} | ` +
                `المحرك: ${data.engine} | ` +
                `الزمن: ${data.execution_time_ms} ms`;

        }

        chat.innerHTML +=
            `<div class="message">
            ✅ تمت المعالجة — شاهد النتيجة.
            </div>`;

        chat.scrollTop =
            chat.scrollHeight;

    }

    catch(error) {

        chat.innerHTML +=
            `<div class="message">
            ❌ حدث خطأ في الاتصال بالخادم.
            </div>`;

    }

}

function escapeHtml(text) {

    return text
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");

}

async function copyResult() {

    const result =
        document.getElementById(
            "result"
        ).innerText;

    const button =
        document.getElementById(
            "copyButton"
        );

    if (
        !result ||
        result === "ستظهر النتيجة هنا..."
    ) {
        return;
    }

    try {

        await navigator.clipboard.writeText(
            result
        );

        button.innerText =
            "تم النسخ ✓";

        button.classList.add("ok");

        setTimeout(() => {

            button.innerText =
                "نسخ النتيجة 📋";

            button.classList.remove("ok");

        }, 1800);

    }

    catch(error) {

        button.innerText =
            "تعذر النسخ";

        setTimeout(() => {

            button.innerText =
                "نسخ النتيجة 📋";

        }, 1800);

    }

}

document
    .getElementById("prompt")
    .addEventListener(
        "keydown",
        function(event) {

            if (
                event.ctrlKey &&
                event.key === "Enter"
            ) {
                sendRequest();
            }

        }
    );

</script>

</body>

</html>
"""

# ------------------------------------------------------------
# HTTP Server
# ------------------------------------------------------------

class Handler(
    http.server.BaseHTTPRequestHandler
):

    def send_json(self, data):

        raw = json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(200)

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

    def do_GET(self):

        if self.path == "/":

            raw = HTML.encode("utf-8")

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

            return

        if self.path == "/api/status":

            conn = sqlite3.connect(DB_FILE)

            count = conn.execute(
                "SELECT COUNT(*) FROM agents"
            ).fetchone()[0]

            conn.close()

            self.send_json({
                "status": "ONLINE",
                "agents": count,
                "hf_available": HF_AVAILABLE,
                "hf_token": bool(HF_TOKEN)
            })

            return

        self.send_response(404)
        self.end_headers()

    def do_POST(self):

        if self.path != "/api/process":

            self.send_response(404)
            self.end_headers()
            return

        try:

            length = int(
                self.headers.get(
                    "Content-Length",
                    0
                )
            )

            body = self.rfile.read(length)

            data = json.loads(
                body.decode("utf-8")
            )

            prompt = str(
                data.get("prompt", "")
            ).strip()

            if not prompt:

                self.send_json({
                    "status": "ERROR",
                    "response": "الطلب فارغ.",
                    "result": ""
                })

                return

            result = process_request(
                prompt
            )

            self.send_json(result)

        except Exception as e:

            logging.exception(
                "Request error"
            )

            self.send_json({
                "status": "ERROR",
                "response": "حدث خطأ داخلي.",
                "result": "",
                "error": str(e)
            })

    def log_message(
        self,
        format,
        *args
    ):
        return

# ------------------------------------------------------------
# تشغيل
# ------------------------------------------------------------

def main():

    init_db()

    try:

        socketserver.ThreadingTCPServer.allow_reuse_address = True

        server = socketserver.ThreadingTCPServer(
            (HOST, PORT),
            Handler
        )

        logging.info(
            "NEXORA ONLINE http://127.0.0.1:%s",
            PORT
        )

        server.serve_forever()

    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
