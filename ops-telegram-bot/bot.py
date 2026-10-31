"""Private Telegram engineering newsletter for GitHub portfolio updates.

Requires TELEGRAM_BOT_TOKEN and ALLOWED_TELEGRAM_USER_IDS.
Optional: GITHUB_TOKEN, GITHUB_REPOS, OPENAI_API_KEY, OPENAI_MODEL,
NEWSLETTER_INTERVAL_SECONDS (default 3600).
"""
from __future__ import annotations

import asyncio
import json
import logging
import os
import time
from datetime import datetime, timedelta, timezone
from typing import Any

import aiohttp

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
log = logging.getLogger("portfolio-newsletter")

TG_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ALLOWED_USERS = {
    int(value.strip())
    for value in os.getenv("ALLOWED_TELEGRAM_USER_IDS", "").split(",")
    if value.strip().isdigit()
}
if not ALLOWED_USERS:
    raise RuntimeError("Set ALLOWED_TELEGRAM_USER_IDS to your numeric Telegram user ID(s).")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
REPOS = [
    item.strip()
    for item in os.getenv("GITHUB_REPOS", "zkwr1081-source/bongo-platform,zkwr1081-source/AURA-BOT,zkwr1081-source/-ZozPoco2026Bot").split(",")
    if item.strip()
]
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")
INTERVAL = max(900, int(os.getenv("NEWSLETTER_INTERVAL_SECONDS", "3600")))
TG_API = f"https://api.telegram.org/bot{TG_TOKEN}"
GH_HEADERS = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
if GITHUB_TOKEN:
    GH_HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"


def allowed(user_id: int | None) -> bool:
    return user_id in ALLOWED_USERS


async def get_json(session: aiohttp.ClientSession, url: str, headers: dict[str, str] | None = None) -> Any:
    async with session.get(url, headers=headers) as response:
        response.raise_for_status()
        return await response.json()


async def github_snapshot(session: aiohttp.ClientSession) -> list[dict[str, Any]]:
    since = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat().replace("+00:00", "Z")
    snapshot = []
    for repo in REPOS:
        base = f"https://api.github.com/repos/{repo}"
        item: dict[str, Any] = {"repo": repo, "commits": [], "pulls": [], "issues": []}
        try:
            commits = await get_json(session, f"{base}/commits?since={since}&per_page=10", GH_HEADERS)
            item["commits"] = [
                {"message": c.get("commit", {}).get("message", "").splitlines()[0],
                 "url": c.get("html_url", "")}
                for c in commits if isinstance(c, dict)
            ]
        except Exception as exc:
            item["errors"] = item.get("errors", []) + [f"commits: {type(exc).__name__}"]
        try:
            pulls = await get_json(session, f"{base}/pulls?state=open&per_page=20", GH_HEADERS)
            item["pulls"] = [
                {"title": p.get("title", ""), "url": p.get("html_url", ""), "draft": p.get("draft", False)}
                for p in pulls if isinstance(p, dict)
            ]
        except Exception as exc:
            item["errors"] = item.get("errors", []) + [f"pull requests: {type(exc).__name__}"]
        try:
            issues = await get_json(session, f"{base}/issues?state=open&since={since}&per_page=20", GH_HEADERS)
            item["issues"] = [
                {"title": i.get("title", ""), "url": i.get("html_url", "")}
                for i in issues if isinstance(i, dict) and "pull_request" not in i
            ]
        except Exception as exc:
            item["errors"] = item.get("errors", []) + [f"issues: {type(exc).__name__}"]
        snapshot.append(item)
    return snapshot


async def summarize(snapshot: list[dict[str, Any]]) -> str:
    """Use the OpenAI API if configured; otherwise return a factual summary."""
    total_commits = sum(len(r["commits"]) for r in snapshot)
    total_prs = sum(len(r["pulls"]) for r in snapshot)
    lines = [f"📊 تحديث محفظة المشاريع — {datetime.now().astimezone().strftime('%Y-%m-%d %H:%M')}",
             f"آخر 24 ساعة: {total_commits} التزامًا حديثًا؛ {total_prs} طلب دمج مفتوحًا."]
    for repo in snapshot:
        lines.append(f"\n📦 {repo['repo']}")
        if repo["commits"]:
            lines.extend(f"• {c['message']} — {c['url']}" for c in repo["commits"][:3])
        else:
            lines.append("• لا توجد التزامات خلال آخر 24 ساعة، أو تعذّر جلبها.")
        if repo["pulls"]:
            lines.append("طلبات الدمج المفتوحة:")
            lines.extend(f"• {p['title']} — {p['url']}" for p in repo["pulls"][:4])
        if repo["issues"]:
            lines.append("المشكلات المفتوحة التي حُدّثت مؤخرًا:")
            lines.extend(f"• {issue['title']} — {issue['url']}" for issue in repo["issues"][:4])
        if repo.get("errors"):
            lines.append("⚠️ تعذّر جلب بعض البيانات؛ راجع صلاحيات GitHub والاتصال.")
    lines.append("\n💡 الأفكار المستقبلية تُعرض كتوصيات وليست مشاريع منفّذة أو أرباحًا مؤكدة.")
    factual = "\n".join(lines)
    if not OPENAI_API_KEY:
        return factual[:3900]
    try:
        payload = {
            "model": OPENAI_MODEL,
            "input": [
                {"role": "system", "content": "أنت محلل هندسي عربي. لخّص بيانات GitHub المرفقة بدقة. افصل العمل المنفذ عن المقترحات، واذكر المخاطر والخطوة التالية ذات العائد الأعلى. لا تختلق إنجازات أو أرباحًا أو نشرًا. احتفظ بروابط GitHub."},
                {"role": "user", "content": json.dumps({"facts": snapshot, "fallback": factual}, ensure_ascii=False)}
            ],
            "max_output_tokens": 900
        }
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=35)) as client:
            async with client.post(
                "https://api.openai.com/v1/responses",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}", "Content-Type": "application/json"},
                json=payload,
            ) as response:
                response.raise_for_status()
                data = await response.json()
        output = []
        for item in data.get("output", []):
            for content in item.get("content", []):
                if content.get("type") == "output_text":
                    output.append(content.get("text", ""))
        return ("\n".join(output).strip() or factual)[:3900]
    except Exception:
        log.exception("AI summary unavailable; using factual summary")
        return factual[:3900]


async def send_message(session: aiohttp.ClientSession, chat_id: int, text: str) -> None:
    async with session.post(f"{TG_API}/sendMessage", json={
        "chat_id": chat_id, "text": text[:4000], "disable_web_page_preview": True
    }) as response:
        response.raise_for_status()
        result = await response.json()
        if not result.get("ok"):
            raise RuntimeError("Telegram rejected sendMessage")


async def handle_update(session: aiohttp.ClientSession, update: dict[str, Any]) -> None:
    message = update.get("message") or update.get("edited_message")
    if not message or not message.get("text"):
        return
    user = message.get("from", {}).get("id")
    chat = message.get("chat", {}).get("id")
    command = message["text"].strip().split()[0].split("@")[0].lower()
    if not allowed(user):
        log.warning("Rejected unauthorized Telegram user")
        if command == "/start":
            await send_message(session, chat, "هذا بوت خاص. اطلب من مالك البوت إضافة رقم Telegram user ID إلى ALLOWED_TELEGRAM_USER_IDS.")
        return
    if command in ("/start", "/help"):
        await send_message(session, chat,
            "مرحبًا! أنا نشرة متابعة مشاريع GitHub الخاصة.\n"
            "/now — تقرير فوري عن آخر 24 ساعة وطلبات الدمج المفتوحة\n"
            "/projects — المستودعات التي أتابعها\n"
            "/ideas — أفكار تطوير مستقبلية، مبنية على حالة المستودعات\n"
            "أرسل نشرة تلقائية كل ساعة ما دام عامل التشغيل يعمل.")
    elif command == "/projects":
        await send_message(session, chat, "المستودعات المتابعة:\n" + "\n".join(f"• https://github.com/{repo}" for repo in REPOS))
    elif command in ("/now", "/ideas"):
        snapshot = await github_snapshot(session)
        report = await summarize(snapshot)
        if command == "/ideas":
            report += "\n\n🧭 أولويات مقترحة:\n1. مراجعة طلبات الدمج المفتوحة وفحوص CI.\n2. تثبيت نشر قابل للتحقق لـ BONGO قبل إضافة خدمات مدفوعة.\n3. بناء سجل استخدام وفوترة قبل ادعاء أي إيراد."
        await send_message(session, chat, report)


async def main() -> None:
    offset = 0
    last_newsletter = 0.0
    timeout = aiohttp.ClientTimeout(total=45, connect=10)
    async with aiohttp.ClientSession(timeout=timeout) as session:
        me = await get_json(session, f"{TG_API}/getMe")
        if not me.get("ok"):
            raise RuntimeError("Telegram bot token validation failed")
        log.info("Bot started as @%s", me.get("result", {}).get("username", "unknown"))
        while True:
            try:
                # Long polling and the hourly newsletter share one loop.
                if time.monotonic() - last_newsletter >= INTERVAL:
                    report = await summarize(await github_snapshot(session))
                    for user_id in sorted(ALLOWED_USERS):
                        await send_message(session, user_id, report)
                    last_newsletter = time.monotonic()
                updates = await get_json(session, f"{TG_API}/getUpdates?timeout=20&offset={offset}")
                for update in updates.get("result", []):
                    offset = max(offset, int(update["update_id"]) + 1)
                    try:
                        await handle_update(session, update)
                    except Exception:
                        log.exception("Failed to process Telegram update")
            except asyncio.CancelledError:
                raise
            except Exception:
                log.exception("Polling/newsletter cycle failed")
                await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(main())
