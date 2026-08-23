#!/usr/bin/env python3
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json, time

PORT=8080
HTML=r'''<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#070b14">
<title>NEXORA | بوابتك الذكية</title>
<style>
*{box-sizing:border-box}
body{margin:0;background:#060914;color:#eef2ff;font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
button,input{font:inherit}
.app{min-height:100vh;background:radial-gradient(circle at 50% -10%,#172554 0,#060914 45%)}
nav{height:68px;display:flex;align-items:center;justify-content:space-between;padding:0 22px;border-bottom:1px solid #1e293b;background:#080d18cc;backdrop-filter:blur(18px);position:sticky;top:0;z-index:5}
.logo{font-size:22px;font-weight:900;letter-spacing:.5px}.logo span{color:#67e8f9}
.status{font-size:12px;color:#86efac;background:#052e1a;padding:8px 13px;border-radius:999px}
main{max-width:1050px;margin:auto;padding:42px 18px 70px}
.hero{text-align:center;padding:25px 0 35px}
.eyebrow{color:#67e8f9;font-size:13px;font-weight:800;margin-bottom:14px}
h1{font-size:clamp(34px,7vw,64px);line-height:1.05;margin:0 0 18px}
.hero p{color:#94a3b8;font-size:17px;max-width:680px;margin:auto;line-height:1.9}
.workspace{margin:30px auto 24px;max-width:820px;background:#0b1220;border:1px solid #263247;border-radius:26px;padding:18px;box-shadow:0 25px 80px #0008}
textarea{width:100%;min-height:130px;resize:vertical;border:0;outline:0;background:#070c16;color:#fff;border-radius:18px;padding:18px;font-size:16px;line-height:1.8}
.send{margin-top:12px;width:100%;border:0;border-radius:15px;padding:15px;background:linear-gradient(90deg,#22d3ee,#818cf8);font-weight:900;cursor:pointer;color:#061018}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(210px,1fr));gap:14px;margin-top:22px}
.card{background:#0b1220;border:1px solid #1e293b;border-radius:20px;padding:21px;transition:.25s}
.card:hover{transform:translateY(-3px);border-color:#334155}
.icon{font-size:25px}.card h3{margin:10px 0 6px}.card p{margin:0;color:#94a3b8;font-size:13px;line-height:1.7}
.result{display:none;margin-top:20px;background:#08111f;border:1px solid #164e63;border-radius:20px;padding:20px}
.result.show{display:block}.step{padding:10px 0;border-bottom:1px solid #172033;color:#cbd5e1}.step:last-child{border:0}
footer{text-align:center;color:#64748b;font-size:12px;margin-top:55px}
</style>
</head>
<body>
<div class="app">
<nav>
<div class="logo">NEXORA <span>OMNI</span></div>
<div class="status">● المنظومة متاحة</div>
</nav>
<main>
<section class="hero">
<div class="eyebrow">INTELLIGENCE • AUTOMATION • RESULTS</div>
<h1>من المشكلة<br><span style="color:#67e8f9">إلى النتيجة.</span></h1>
<p>أخبر NEXORA بما تريد، وهي تساعدك على فهم الهدف، بناء الخطة، اختيار الأدوات المناسبة، والتحقق من النتيجة.</p>
</section>

<section class="workspace">
<textarea id="prompt" placeholder="اكتب مشكلتك أو هدفك هنا...&#10;&#10;مثال: أريد بناء مشروع رقمي وأحتاج خطة كاملة للبدء."></textarea>
<button class="send" onclick="think()">🧠 ابدأ مع NEXORA</button>
<div id="result" class="result">
<strong>🧠 NEXORA تحلل طلبك</strong>
<div class="step">✓ فهم الهدف والسياق</div>
<div class="step">✓ تقسيم المهمة إلى خطوات</div>
<div class="step">● اختيار الأدوات والوكلاء المناسبين</div>
<div class="step">○ التنفيذ والتحقق</div>
</div>
</section>

<div class="grid">
<div class="card"><div class="icon">🧠</div><h3>ذكاء متقدم</h3><p>حوّل فكرتك أو مشكلتك إلى مسار عمل واضح.</p></div>
<div class="card"><div class="icon">🤖</div><h3>وكلاء ذكيون</h3><p>توزيع المهام على الوكلاء المناسبين بدل التنفيذ العشوائي.</p></div>
<div class="card"><div class="icon">⚙️</div><h3>أتمتة</h3><p>تنظيم الأعمال المتكررة وتحويلها إلى عمليات قابلة للتنفيذ.</p></div>
<div class="card"><div class="icon">🛡️</div><h3>تحقق وأمان</h3><p>التحقق من النتائج قبل اعتبار المهمة مكتملة.</p></div>
<div class="card"><div class="icon">📁</div><h3>مساحة العمل</h3><p>إدارة المهام والملفات والنتائج من مكان واحد.</p></div>
<div class="card"><div class="icon">🌐</div><h3>منظومة قابلة للتوسع</h3><p>أدوات وتكاملات وخدمات يمكن إضافتها مع نمو المنصة.</p></div>
</div>

<footer>NEXORA OMNI © 2026 — Client Intelligence Portal</footer>
</main>
</div>
<script>
async function think(){
 const p=document.getElementById('prompt').value.trim();
 if(!p){
   document.getElementById('prompt').focus();
   return;
 }

 const r=document.getElementById('result');
 r.classList.add('show');
 r.innerHTML = '<strong>🧠 NEXORA تعمل...</strong><div class="step">● إرسال الطلب إلى CORE</div>';

 try{
   const response = await fetch('http://127.0.0.1:8091/api/task',{
     method:'POST',
     headers:{'Content-Type':'application/json'},
     body:JSON.stringify({task:p})
   });

   const data = await response.json();

   if(!response.ok){
     throw new Error(data.error || 'request_failed');
   }

   const analyst = data.analysis?.analyst || {};
   const execution = data.execution;

   r.innerHTML = `
     <strong>🧠 NEXORA</strong>
     <div class="step">✓ الطلب وصل إلى CORE</div>
     <div class="step">✓ ANALYST: ${analyst.complexity || 'unknown'}</div>
     <div class="step">✓ الأدوات المطلوبة: ${analyst.requires_tools ? 'نعم' : 'لا'}</div>
     <div class="step">✓ الحالة: ${data.status}</div>
     ${execution ? '<div class="step">✓ التنفيذ: ' + execution.status + '</div>' : ''}
     <div class="step">${data.ai?.answer || 'تمت معالجة الطلب.'}</div>
   `;

   r.scrollIntoView({behavior:'smooth',block:'nearest'});

 }catch(error){
   r.innerHTML = `
     <strong>⚠️ NEXORA</strong>
     <div class="step">تعذر الاتصال بـ CORE: ${error.message}</div>
   `;
 }
}
</script>
</body>
</html>'''

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path=='/api/status':
            data={"status":"online","service":"NEXORA Client Portal","timestamp":int(time.time())}
            body=json.dumps(data,ensure_ascii=False).encode()
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
    def log_message(self,*args): pass

ThreadingHTTPServer(("127.0.0.1",PORT),Handler).serve_forever()
