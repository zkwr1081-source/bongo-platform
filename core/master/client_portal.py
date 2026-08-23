#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json, time

PORT = 8095

HTML = r'''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
<meta name="theme-color" content="#050816">
<title>NEXORA — بوابتك الذكية</title>
<style>
*{box-sizing:border-box}
:root{
 --bg:#050816;--panel:#0b1020;--panel2:#0e1528;
 --line:#202b43;--text:#f8fafc;--muted:#94a3b8;
 --cyan:#22d3ee;--violet:#8b5cf6;--green:#34d399
}
body{
 margin:0;background:
 radial-gradient(circle at 50% -15%,#18285b 0,#050816 48%);
 color:var(--text);
 font-family:system-ui,-apple-system,"Segoe UI",Tahoma,sans-serif;
 min-height:100vh
}
header{
 height:70px;padding:0 20px;display:flex;align-items:center;
 justify-content:space-between;border-bottom:1px solid var(--line);
 background:#050816d9;backdrop-filter:blur(18px);
 position:sticky;top:0;z-index:10
}
.logo{font-size:22px;font-weight:950;letter-spacing:.5px}
.logo b{color:var(--cyan)}
.online{
 padding:7px 12px;border:1px solid #14532d;background:#052e1b;
 color:#86efac;border-radius:999px;font-size:12px;font-weight:800
}
main{width:min(1080px,100%);margin:auto;padding:35px 17px 70px}
.hero{text-align:center;padding:28px 0}
.kicker{color:var(--cyan);font-size:12px;font-weight:900;letter-spacing:2px}
h1{font-size:clamp(38px,8vw,70px);line-height:1.02;margin:16px 0}
.gradient{
 background:linear-gradient(90deg,var(--cyan),#a78bfa);
 -webkit-background-clip:text;color:transparent
}
.hero p{
 color:var(--muted);max-width:690px;margin:auto;
 line-height:1.9;font-size:16px
}
.ai-box{
 max-width:850px;margin:30px auto;
 padding:12px;background:linear-gradient(135deg,#111a31,#080d1b);
 border:1px solid #263653;border-radius:28px;
 box-shadow:0 30px 100px #0008
}
textarea{
 width:100%;height:145px;resize:none;outline:none;border:0;
 border-radius:20px;background:#050914;color:#fff;
 padding:19px;font-size:16px;line-height:1.8
}
textarea::placeholder{color:#64748b}
.send{
 width:100%;margin-top:10px;padding:16px;border:0;border-radius:16px;
 background:linear-gradient(90deg,var(--cyan),var(--violet));
 color:#020617;font-weight:950;cursor:pointer
}
.quick{
 display:flex;gap:9px;flex-wrap:wrap;justify-content:center;
 margin-top:15px
}
.quick button{
 border:1px solid var(--line);background:#0b1222;color:#cbd5e1;
 padding:9px 13px;border-radius:999px;cursor:pointer
}
.workspace{
 display:none;margin:20px auto;max-width:850px;
 background:var(--panel);border:1px solid #243453;
 border-radius:23px;padding:20px
}
.workspace.show{display:block}
.phase{
 display:flex;align-items:center;gap:12px;padding:13px 0;
 border-bottom:1px solid #172238;color:#cbd5e1
}
.phase:last-child{border:0}
.dot{width:10px;height:10px;border-radius:50%;background:#334155}
.done .dot{background:var(--green);box-shadow:0 0 15px #34d399}
.active .dot{background:var(--cyan);box-shadow:0 0 18px #22d3ee}
.cards{
 display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));
 gap:14px;margin-top:25px
}
.card{
 background:#0a1020;border:1px solid var(--line);
 border-radius:20px;padding:22px;cursor:pointer;
 transition:.2s
}
.card:hover{transform:translateY(-3px);border-color:#3b82f6}
.icon{font-size:28px}.card h3{margin:12px 0 7px}
.card p{margin:0;color:var(--muted);font-size:13px;line-height:1.8}
.section{
 margin-top:28px;background:#080e1c;
 border:1px solid var(--line);border-radius:22px;padding:20px
}
.section h2{font-size:17px;margin:0 0 8px}
.section p{color:var(--muted);font-size:13px;line-height:1.8}
footer{text-align:center;color:#475569;font-size:11px;margin-top:55px}
</style>
</head>
<body>

<header>
 <div class="logo">NEXORA <b>OMNI</b></div>
 <div class="online">● متاحة الآن</div>
</header>

<main>

<section class="hero">
 <div class="kicker">INTELLIGENCE • AUTOMATION • RESULTS</div>
 <h1>ماذا تريد<br><span class="gradient">أن تنجز اليوم؟</span></h1>
 <p>
 NEXORA هي بوابتك الذكية لفهم المشكلات، بناء الخطط،
 تشغيل الأدوات والوكلاء، والوصول إلى نتيجة قابلة للتحقق.
 </p>
</section>

<section class="ai-box">
 <textarea id="prompt"
 placeholder="اكتب هدفك أو مشكلتك هنا...&#10;&#10;مثال: أريد إنشاء مشروع رقمي من الصفر."></textarea>

 <button class="send" onclick="startAI()">
 🧠 دع NEXORA تبدأ
 </button>

 <div class="quick">
  <button onclick="fill('أريد بناء مشروع جديد')">🚀 مشروع جديد</button>
  <button onclick="fill('أريد تحليل فكرة')">💡 تحليل فكرة</button>
  <button onclick="fill('أريد أتمتة مهمة')">⚙️ أتمتة</button>
  <button onclick="fill('أريد تحليل بيانات')">📊 بيانات</button>
  <button onclick="fill('أريد مساعدة تقنية')">💻 تقنية</button>
 </div>
</section>

<section id="workspace" class="workspace">
 <h2>🧠 مساحة العمل الذكية</h2>
 <p id="understood" style="color:#94a3b8"></p>

 <div class="phase done"><span class="dot"></span> فهم الطلب والسياق</div>
 <div class="phase active"><span class="dot"></span> بناء خطة العمل</div>
 <div class="phase"><span class="dot"></span> اختيار الأدوات والوكلاء</div>
 <div class="phase"><span class="dot"></span> التنفيذ</div>
 <div class="phase"><span class="dot"></span> التحقق من النتيجة</div>
</section>

<section class="cards">

 <div class="card">
  <div class="icon">🧠</div>
  <h3>العقل الذكي</h3>
  <p>يفهم هدفك قبل أن يقترح عليك الإجراء المناسب.</p>
 </div>

 <div class="card">
  <div class="icon">🤖</div>
  <h3>شبكة الوكلاء</h3>
  <p>توزيع المهام على وكلاء متخصصين بدل تشغيل كل شيء بطريقة واحدة.</p>
 </div>

 <div class="card">
  <div class="icon">🔎</div>
  <h3>اكتشاف وحل</h3>
  <p>تحليل المشكلة والبحث عن المسار الأنسب للوصول إلى النتيجة.</p>
 </div>

 <div class="card">
  <div class="icon">⚙️</div>
  <h3>أتمتة</h3>
  <p>تحويل الأعمال المتكررة إلى عمليات منظمة وقابلة للمراقبة.</p>
 </div>

 <div class="card">
  <div class="icon">🛡️</div>
  <h3>التحقق</h3>
  <p>النتيجة لا تعتبر مكتملة لمجرد أن النظام نفذ خطوة.</p>
 </div>

 <div class="card">
  <div class="icon">🧩</div>
  <h3>تكاملات</h3>
  <p>إمكانية توصيل الأدوات والخدمات الخارجية من خلال طبقة تكامل مستقلة.</p>
 </div>

</section>

<section class="section">
 <h2>🌐 NEXORA تتطور مع مهمتك</h2>
 <p>
 لا توجد أرقام وهمية أو معاملات مصطنعة في واجهة العميل.
 كل نتيجة مستقبلية ستُصنف بوضوح: حقيقية، قيد التحقق،
 محاكاة، أو غير متاحة.
 </p>
</section>

<footer>NEXORA OMNI © 2026</footer>

</main>

<script>
function fill(x){
 document.getElementById("prompt").value=x;
 document.getElementById("prompt").focus();
}

function startAI(){
 const text=document.getElementById("prompt").value.trim();
 if(!text){
   document.getElementById("prompt").focus();
   return;
 }

 document.getElementById("understood").textContent=
   "فهمت NEXORA طلبك: «"+text+"» — جاري تحويله إلى مسار عمل.";
 document.getElementById("workspace").classList.add("show");
 document.getElementById("workspace").scrollIntoView({
   behavior:"smooth",block:"center"
 });
}
</script>

</body>
</html>'''

class Handler(BaseHTTPRequestHandler):
 def do_GET(self):
  if self.path == "/api/status":
   body=json.dumps({
    "service":"NEXORA Client Portal",
    "status":"ONLINE",
    "mode":"CLIENT"
   },ensure_ascii=False).encode()
   self.send_response(200)
   self.send_header("Content-Type","application/json; charset=utf-8")
   self.send_header("Content-Length",str(len(body)))
   self.end_headers()
   self.wfile.write(body)
   return

  body=HTML.encode()
  self.send_response(200)
  self.send_header("Content-Type","text/html; charset=utf-8")
  self.send_header("Content-Length",str(len(body)))
  self.end_headers()
  self.wfile.write(body)

 def log_message(self,*args):
  pass

ThreadingHTTPServer(("127.0.0.1",PORT),Handler).serve_forever()
