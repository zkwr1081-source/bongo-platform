import os
import json
import sqlite3
import urllib.request
import urllib.error
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from dotenv import load_dotenv

BASE = Path(__file__).resolve().parents[2]
ENV_FILE = BASE / ".env"
load_dotenv(ENV_FILE)

HOST = "127.0.0.1"
PORT = 8080
CORE_URL = os.getenv("NEXORA_CORE_URL", "http://127.0.0.1:8091")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "").strip()
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o").strip()
DB = BASE / "nexora_ui.db"

def db():
    conn = sqlite3.connect(DB)
    conn.execute("CREATE TABLE IF NOT EXISTS chats (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT NOT NULL, content TEXT NOT NULL, created_at DATETIME DEFAULT CURRENT_TIMESTAMP)")
    conn.commit()
    return conn

def save_chat(role, content):
    conn = db()
    conn.execute("INSERT INTO chats(role,content) VALUES (?,?)", (role, content))
    conn.commit()
    conn.close()

def openai_request(prompt):
    if not OPENAI_API_KEY or "ضع_مفتاح" in OPENAI_API_KEY:
        return {"ok": False, "error": "يرجى تعيين OPENAI_API_KEY في ملف .env بمفتاح صالح"}
    payload = json.dumps({"model": OPENAI_MODEL, "messages": [{"role": "user", "content": prompt}]}).encode()
    req = urllib.request.Request("https://api.openai.com/v1/chat/completions", data=payload, headers={"Content-Type": "application/json", "Authorization": "Bearer " + OPENAI_API_KEY}, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode())
        text = data.get("choices", [{}])[0].get("message", {}).get("content", "")
        return {"ok": True, "answer": text or "تمت معالجة الطلب."}
    except urllib.error.HTTPError as e:
        return {"ok": False, "error": f"HTTP {e.code}: {e.read().decode(errors='replace')}"}
    except Exception as e:
        return {"ok": False, "error": str(e)}

HTML = r"""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>NEXORA OMNI</title>
<style>
*{box-sizing:border-box}
html,body{margin:0;min-height:100%;background:#05070d;color:#fff;font-family:system-ui,sans-serif}
body{background:radial-gradient(circle at 50% -10%,#17365d 0,#09111f 35%,#05070d 70%)}
nav{height:70px;display:flex;align-items:center;justify-content:space-between;padding:0 22px;border-bottom:1px solid #1e293b;background:#070b13dd;backdrop-filter:blur(18px);position:sticky;top:0;z-index:5}
.logo{font-weight:900;font-size:21px}.logo span{color:#67e8f9}
.status{color:#86efac;font-size:12px;border:1px solid #14532d;background:#092719;padding:7px 12px;border-radius:99px}
main{width:min(1000px,94%);margin:auto;padding:50px 0 80px}
.hero{text-align:center;padding:25px 0}
.badge{display:inline-block;padding:8px 13px;border-radius:99px;border:1px solid #164e63;color:#67e8f9;font-size:12px}
h1{font-size:clamp(42px,9vw,76px);line-height:1;margin:20px 0}h1 span{color:#67e8f9}
.hero p{max-width:700px;margin:auto;color:#94a3b8;line-height:1.9}
.workspace{margin:35px auto;padding:18px;max-width:850px;background:#0a101cdd;border:1px solid #263247;border-radius:28px;box-shadow:0 30px 100px #0009}
textarea{width:100%;height:150px;resize:vertical;border:0;outline:0;border-radius:20px;background:#060a12;color:white;padding:18px;font-size:16px;line-height:1.8}
textarea::placeholder{color:#64748b}
.actions{display:flex;gap:10px;margin-top:12px}
button{border:0;cursor:pointer;font-weight:800}
.send{flex:1;padding:15px;border-radius:15px;background:linear-gradient(90deg,#22d3ee,#818cf8);color:#041018}
.clear{padding:15px 22px;border-radius:15px;background:#151d2c;color:#cbd5e1}
.result{display:none;margin-top:18px;padding:20px;border-radius:20px;background:#070d17;border:1px solid #164e63}
.result.show{display:block}
.answer{white-space:pre-wrap;line-height:1.9;color:#e2e8f0}
.error{color:#fca5a5}
</style>
</head>
<body>
<nav><div class="logo">NEXORA <span>OMNI</span></div><div class="status">● المنظومة متاحة</div></nav>
<main>
<section class="hero"><div class="badge">INTELLIGENCE • AUTOMATION • RESULTS</div><h1>من المشكلة<br><span>إلى النتيجة.</span></h1><p>تحدث مع NEXORA بلغتك الطبيعية.</p></section>
<section class="workspace">
<textarea id="prompt" placeholder="ماذا تريد من NEXORA؟"></textarea>
<div class="actions"><button class="send" onclick="ask()">🧠 اسأل NEXORA</button><button class="clear" onclick="clearChat()">مسح</button></div>
<div id="result" class="result"><div id="answer" class="answer"></div></div>
</section>
</main>
<script>
async function ask(){
const input=document.getElementById("prompt");
const result=document.getElementById("result");
const answer=document.getElementById("answer");
const task=input.value.trim();
if(!task){input.focus();return;}
result.classList.add("show");
answer.textContent="🧠 NEXORA تفكر...";
try{
const response=await fetch("/api/ask",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify({task:task})});
const data=await response.json();
if(!response.ok || !data.ok){throw new Error(data.error || "تعذر تنفيذ الطلب");}
answer.textContent=data.answer || "تمت معالجة الطلب.";
}catch(error){answer.innerHTML='<span class="error">تعذر الاتصال بالعقل الخارجي.</span>\n\n'+error.message;}
}
function clearChat(){document.getElementById("prompt").value="";document.getElementById("answer").textContent="";document.getElementById("result").classList.remove("show");}
</script>
</body>
</html>
"""

class Handler(BaseHTTPRequestHandler):
    def send_json(self, data, code=200):
        raw = json.dumps(data, ensure_ascii=False).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self.end_headers()
        self.wfile.write(raw)

    def do_GET(self):
        if self.path == "/":
            raw = HTML.encode()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
            return
        if self.path == "/api/status":
            self.send_json({"status": "online", "service": "NEXORA OMNI", "core": CORE_URL, "ai_provider": "openai" if (OPENAI_API_KEY and "ضع_مفتاح" not in OPENAI_API_KEY) else "not_configured", "model": OPENAI_MODEL})
            return
        self.send_json({"error": "not_found"}, 404)

    def do_POST(self):
        if self.path != "/api/ask":
            self.send_json({"error": "not_found"}, 404)
            return
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = self.rfile.read(length)
            data = json.loads(body.decode())
            task = str(data.get("task", "")).strip()
            if not task:
                self.send_json({"error": "empty_task"}, 400)
                return
            save_chat("user", task)
            result = openai_request(task)
            if not result["ok"]:
                self.send_json(result, 502)
                return
            answer = result["answer"]
            save_chat("assistant", answer)
            self.send_json({"ok": True, "answer": answer, "model": OPENAI_MODEL})
        except Exception as e:
            self.send_json({"ok": False, "error": str(e)}, 500)

if __name__ == "__main__":
    db()
    server = ThreadingHTTPServer((HOST, PORT), Handler)
    server.serve_forever()
