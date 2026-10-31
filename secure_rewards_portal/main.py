"""Secure rewards portal starter.

This service deliberately never accepts, processes, logs, or stores payment
card numbers, expiry dates, or CVV values. Payment must happen on a PCI-compliant
provider-hosted checkout page.
"""
from __future__ import annotations

import os
from html import escape
from urllib.parse import urlparse

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel, Field, HttpUrl

APP_VERSION = "1.0.0"
CHECKOUT_URL = os.getenv("REWARDS_CHECKOUT_URL", "").strip()

app = FastAPI(
    title="BONGO Secure Rewards Portal",
    description="Arabic-first rewards portal using provider-hosted checkout.",
    version=APP_VERSION,
    docs_url=None if os.getenv("ENVIRONMENT") == "production" else "/docs",
    redoc_url=None,
)


class RewardRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=100)
    email: str = Field(min_length=5, max_length=254)


@app.middleware("http")
async def security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "no-referrer"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    response.headers["Content-Security-Policy"] = (
        "default-src 'self'; style-src 'self' 'unsafe-inline'; "
        "script-src 'self' 'unsafe-inline'; form-action 'self'; "
        "base-uri 'none'; frame-ancestors 'none'"
    )
    response.headers["Cache-Control"] = "no-store"
    return response


@app.get("/health")
async def health():
    return {"ok": True, "service": "secure-rewards-portal", "version": APP_VERSION}


@app.get("/", response_class=HTMLResponse)
async def landing_page():
    return HTMLResponse("""<!doctype html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#090f1f">
<title>بوابة المكافآت الآمنة | BONGO</title>
<style>
:root{color-scheme:dark;font-family:system-ui,Tahoma,sans-serif;background:#090f1f;color:#eef2ff}
*{box-sizing:border-box}body{margin:0;min-height:100vh;display:grid;place-items:center;padding:24px;
background:radial-gradient(ellipse at 15% 10%,#312e8155,transparent 45%),radial-gradient(ellipse at 85% 90%,#0e749055,transparent 40%),#090f1f}
main{width:min(100%,520px);padding:34px;border:1px solid #293653;border-radius:26px;background:#111a2deF;box-shadow:0 25px 90px #0008}
.tag{display:inline-block;padding:7px 12px;border:1px solid #256b60;border-radius:30px;color:#7ee7c2;background:#0c332c}
h1{font-size:clamp(26px,6vw,36px);margin:20px 0 8px}p{color:#aab8d2;line-height:1.8}
label{display:block;margin:18px 0 7px;color:#cbd5e1;font-size:14px}
input{width:100%;padding:14px;border-radius:12px;border:1px solid #34445f;background:#091222;color:white;font:inherit}
input:focus{outline:2px solid #818cf8;border-color:transparent}
button,.checkout{display:block;width:100%;margin-top:22px;padding:15px;border:0;border-radius:13px;
background:linear-gradient(100deg,#6366f1,#8b5cf6);color:white;font-weight:750;font-size:15px;text-align:center;text-decoration:none;cursor:pointer}
.notice{margin-top:20px;padding:14px;border:1px solid #35566b;border-radius:13px;background:#102638;color:#b9e8f5;font-size:13px}
small{display:block;color:#8190aa;margin-top:18px;text-align:center}
[hidden]{display:none!important}
</style></head>
<body><main>
<span class="tag">● بوابة آمنة · BONGO</span>
<h1>بوابة المكافآت الذكية</h1>
<p>أكمل طلب المكافأة، ثم تابع الدفع حصراً عبر صفحة الدفع المستضافة لدى مزوّد الدفع المعتمد.</p>
<form id="claim">
<label for="name">الاسم الكامل</label><input id="name" name="full_name" minlength="2" maxlength="100" autocomplete="name" required>
<label for="email">البريد الإلكتروني</label><input id="email" name="email" type="email" maxlength="254" autocomplete="email" required>
<button id="submit" type="submit">متابعة آمنة</button>
</form>
<div class="notice">🔒 لا تطلب هذه البوابة رقم البطاقة أو تاريخ الانتهاء أو CVV، ولا تخزّنها. أدخل بيانات الدفع فقط داخل صفحة مزوّد الدفع الرسمية.</div>
<p id="status" role="status" aria-live="polite" hidden></p>
<small>اتصال مشفّر مطلوب في بيئة الإنتاج · لا تشارك رموز التحقق مع أي شخص</small>
<script>
const form=document.querySelector('#claim'),button=document.querySelector('#submit'),statusBox=document.querySelector('#status');
form.addEventListener('submit',async e=>{
 e.preventDefault();button.disabled=true;button.textContent='جارٍ التحقق…';
 try{
  const r=await fetch('/api/v1/checkout',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({
   full_name:form.full_name.value,email:form.email.value
  })});
  const data=await r.json();
  if(!r.ok)throw new Error(data.detail||'تعذر بدء عملية الدفع.');
  location.assign(data.checkout_url);
 }catch(err){statusBox.hidden=false;statusBox.textContent=err.message;}
 finally{button.disabled=false;button.textContent='متابعة آمنة';}
});
</script></main></body></html>""")


@app.post("/api/v1/checkout", status_code=status.HTTP_200_OK)
async def start_checkout(payload: RewardRequest):
    # Do not log or persist the submitted contact details.
    if not CHECKOUT_URL:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="لم يتم إعداد مزوّد الدفع بعد. لم يتم إرسال أي بيانات دفع.",
        )
    parsed = urlparse(CHECKOUT_URL)
    if parsed.scheme != "https" or not parsed.netloc:
        raise HTTPException(status_code=500, detail="إعداد رابط الدفع غير آمن.")
    return {"status": "ready", "checkout_url": CHECKOUT_URL}
