#!/data/data/com.termux/files/usr/bin/env python3
import http.server
import socketserver
import json
import threading

PORT = 8080

ULTIMATE_HTML = """<!DOCTYPE html>
<html lang="ar" dir="rtl" id="htmlRoot">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NEXORA OMNI ULTIMATE ECOSYSTEM</title>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
:root {
    --holo-primary: #00ffcc;
    --holo-secondary: #0088ff;
    --holo-accent: #bf00ff;
    --holo-gold: #ffaa00;
    --bg-space: #010308;
    --glass-bg: rgba(3, 8, 18, 0.95);
    --border-glow: rgba(0, 255, 204, 0.4);
    --text-main: #e2e8f0;
    --text-muted: #64748b;
}

* { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }
body { background: var(--bg-space); color: var(--text-main); min-height: 100vh; overflow-x: hidden; position: relative; }

#bgCanvas { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; pointer-events: none; }

.header {
    background: rgba(2, 5, 12, 0.96);
    backdrop-filter: blur(20px);
    border-bottom: 1px solid var(--border-glow);
    padding: 15px 30px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    position: sticky;
    top: 0;
    z-index: 100;
}

.logo { font-weight: 900; font-size: 1.1rem; color: var(--holo-primary); display: flex; align-items: center; gap: 10px; cursor: pointer; }
.badge { background: linear-gradient(135deg, var(--holo-primary), var(--holo-secondary)); color: #000; padding: 3px 10px; border-radius: 6px; font-size: 0.65rem; font-weight: 900; }

.controls-header { display: flex; gap: 10px; align-items: center; flex-wrap: wrap; }
.search-input, .lang-select { background: rgba(5,12,25,0.9); border: 1px solid var(--border-glow); color: var(--holo-primary); padding: 6px 12px; border-radius: 8px; font-weight: 700; outline: none; font-size: 0.8rem; }
.search-input { width: 180px; font-family: 'JetBrains Mono', monospace; }

.container { max-width: 1300px; margin: 25px auto; padding: 0 20px; }

.view-container { transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1); transform-origin: center; }
.telegram-dissolve { transform: scale(0) translateY(50px) rotate(5deg); opacity: 0; filter: blur(15px); }

@keyframes softPulseIn {
    0% { opacity: 0; transform: scale(0.95) translateY(-10px); filter: blur(5px); }
    100% { opacity: 1; transform: scale(1) translateY(0); filter: blur(0); }
}
.soft-fade-in { animation: softPulseIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards; }

.page-view { display: none; }
.page-view.active { display: block; }

.system-status-bar {
    background: var(--glass-bg);
    border: 1px solid var(--border-glow);
    padding: 15px 20px;
    border-radius: 12px;
    margin-bottom: 20px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.8rem;
    flex-wrap: wrap;
    gap: 15px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.5);
}
.status-item span { color: var(--holo-primary); font-weight: bold; }

.gamification-panel {
    background: linear-gradient(135deg, rgba(0,255,204,0.08), rgba(0,136,255,0.08));
    border: 1px solid var(--holo-primary);
    border-radius: 14px;
    padding: 20px;
    margin-bottom: 25px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    box-shadow: 0 0 25px rgba(0,255,204,0.15);
}

.grid-dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 16px; }
.service-square {
    background: var(--glass-bg);
    backdrop-filter: blur(15px);
    border: 1px solid var(--border-glow);
    border-radius: 14px;
    padding: 18px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 140px;
    position: relative;
    overflow: hidden;
}
.service-square::before {
    content: '';
    position: absolute;
    top: 0; right: 0; width: 4px; height: 100%;
    background: linear-gradient(to bottom, var(--holo-primary), var(--holo-secondary));
}
.service-square:hover {
    border-color: var(--holo-primary);
    transform: translateY(-4px) scale(1.02);
    box-shadow: 0 12px 35px rgba(0,255,204,0.25);
}
.square-num { font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; color: var(--holo-primary); font-weight: 700; }
.square-title { font-size: 0.9rem; font-weight: 900; color: var(--text-main); margin: 6px 0; }

.card { background: var(--glass-bg); backdrop-filter: blur(15px); border: 1px solid var(--border-glow); border-radius: 16px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); min-height: 420px; display: flex; flex-direction: column; justify-content: space-between; }
.card-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px; margin-bottom: 20px; }
.card-title { color: var(--holo-primary); font-size: 1.2rem; font-weight: 900; }
.page-counter { background: rgba(0,255,204,0.1); border: 1px solid var(--holo-primary); color: var(--holo-primary); padding: 4px 12px; border-radius: 20px; font-size: 0.8rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }

.content-body { flex: 1; display: flex; flex-direction: column; gap: 15px; font-size: 0.95rem; line-height: 1.8; color: var(--text-main); }
.interactive-box { background: rgba(1, 3, 7, 0.85); border: 1px solid rgba(0,255,204,0.25); border-radius: 12px; padding: 20px; font-family: 'JetBrains Mono', monospace; font-size: 0.85rem; color: var(--holo-primary); min-height: 110px; display: flex; align-items: center; justify-content: center; text-align: center; }

.nav-controls { display: flex; justify-content: space-between; align-items: center; margin-top: 25px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px; }
.nav-btn { background: linear-gradient(135deg, var(--holo-primary), var(--holo-secondary)); color: #000; border: none; font-weight: 900; padding: 10px 22px; border-radius: 10px; cursor: pointer; font-size: 0.9rem; transition: 0.3s; }
.nav-btn:hover { opacity: 0.9; transform: translateY(-2px); }
.btn-home { background: rgba(5,12,25,0.9); border: 1px solid var(--holo-gold); color: var(--holo-gold); }

.action-bar-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 15px; }
.action-card { background: rgba(0,255,204,0.05); border: 1px solid var(--border-glow); padding: 15px; border-radius: 10px; text-align: center; cursor: pointer; transition: 0.3s; }
.action-card:hover { background: rgba(0,255,204,0.15); border-color: var(--holo-primary); }
</style>
</head>
<body>

<canvas id="bgCanvas"></canvas>

<div class="header">
    <div class="logo" onclick="goToDashboard()">
        <span class="badge">NEXORA OMNI</span> 
        <span id="headerTitle">منظومة نكسورا السيبرانية الشاملة</span>
    </div>
    <div class="controls-header">
        <input type="text" class="search-input" id="searchInput" placeholder="بحث في المحاور..." oninput="filterAxes(this.value)">
        <select class="lang-select" id="langSelector" onchange="changeLanguage(this.value)">
            <option value="ar">العربية</option>
            <option value="en">English</option>
        </select>
        <button class="nav-btn btn-home" style="padding: 6px 12px; font-size:0.75rem;" onclick="goToDashboard()" id="homeBtnText">الرئيسية</button>
    </div>
</div>

<div class="container">
    <div id="dashboardView" class="page-view active view-container">
        
        <div class="system-status-bar">
            <div class="status-item">حالة النواة: <span id="lblCore">نشطة ومؤمنة (0.01ms)</span></div>
            <div class="status-item">الوكلاء المتزامنون: <span>5,000 / 5,000</span></div>
            <div class="status-item">الشبكة الحرة: <span>مفعلة بالكامل (بدون قيود)</span></div>
        </div>

        <div class="gamification-panel">
            <div>
                <h3 style="color:var(--holo-primary); font-size:1.1rem; margin-bottom:5px;">نقاط التطور العصبي (Neural XP)</h3>
                <p style="color:var(--text-muted); font-size:0.85rem;">اربح النقاط وافتح ترقيات الأوزان المفتوحة للوكلاء من خلال تفاعلك المستمر.</p>
            </div>
            <div style="font-family:'JetBrains Mono'; font-size:1.5rem; color:var(--holo-gold); font-weight:900;" id="xpCounter">99,999 XP</div>
        </div>

        <div style="margin-bottom: 20px;">
            <h1 style="color:var(--holo-primary); font-size:1.4rem; font-weight:900;" id="dashHeading">الخدمات المتكاملة والمحاور الـ 100</h1>
            <p style="color:var(--text-muted); font-size:0.85rem;" id="dashSub">انقر على أي محور لتفعيل العبور السينمائي الفوري وإدارة الأوزان والوكلاء.</p>
        </div>
        <div class="grid-dashboard" id="servicesGrid"></div>
    </div>

    <div id="serviceView" class="page-view view-container">
        <div class="card" id="serviceCardContent"></div>
    </div>
</div>

<script>
const axes100 = {
    ar: Array.from({length: 100}, (_, i) => ({
        title: `${i + 1}. محور نكسورا الاستراتيجي والذكاء العصبي`,
        desc: `محور سيبراني متطور رقم (${i + 1}) يدار بواسطة شبكة الوكلاء الـ 5,000، ويتضمن محرك الأفكار الجذرية، النظام المالي اللامركزي، وأوزان النماذج المفتوحة.`,
        status: `حالة المحور ${i + 1}: نشط، مؤمن، ومرتبط بشبكة الوكلاء الحرة (0.01ms).`
    })),
    en: Array.from({length: 100}, (_, i) => ({
        title: `${i + 1}. Nexora Strategic & Neural Axis`,
        desc: `Advanced cybernetic axis #${i + 1} managed by the 5,000 swarm, integrating radical idea forge, decentralized finance, and open weights.`,
        status: `Axis ${i + 1} Status: Active, secure, and synchronized at 0.01ms.`
    }))
};

let currentLang = 'ar';
let activeAxes = axes100.ar;
let userXP = 99999;

function changeLanguage(lang) {
    currentLang = lang;
    document.getElementById('htmlRoot').setAttribute('dir', lang === 'ar' ? 'rtl' : 'ltr');
    document.getElementById('headerTitle').innerText = lang === 'ar' ? "منظومة نكسورا السيبرانية الشاملة" : "Nexora Omni Cybernetic Ecosystem";
    document.getElementById('homeBtnText').innerText = lang === 'ar' ? "الرئيسية" : "Home";
    document.getElementById('dashHeading').innerText = lang === 'ar' ? "الخدمات المتكاملة والمحاور الـ 100" : "Integrated Services & 100 Axes";
    document.getElementById('dashSub').innerText = lang === 'ar' ? "انقر على أي محور لتفعيل العبور السينمائي الفوري وإدارة الأوزان والوكلاء." : "Click any axis to trigger cinematic transition and manage agents.";
    document.getElementById('searchInput').placeholder = lang === 'ar' ? "بحث في المحاور..." : "Search axes...";
    document.getElementById('lblCore').innerText = lang === 'ar' ? "نشطة ومؤمنة (0.01ms)" : "Active & Secured (0.01ms)";
    
    activeAxes = axes100[lang];
    renderDashboard(activeAxes);
}

function filterAxes(query) {
    const filtered = activeAxes.filter(item => item.title.includes(query) || item.desc.includes(query));
    renderDashboard(filtered);
}

function renderDashboard(axes) {
    const grid = document.getElementById('servicesGrid');
    grid.innerHTML = '';
    axes.forEach((s, index) => {
        const originalIndex = activeAxes.indexOf(s) + 1;
        grid.innerHTML += `
            <div class="service-square" onclick="openServicePage(${originalIndex})">
                <div>
                    <div class="square-num">AXIS ${originalIndex < 10 ? '0' + originalIndex : originalIndex} / 100</div>
                    <div class="square-title">${s.title}</div>
                </div>
                <div style="font-size:0.75rem; color:var(--text-muted);">
                    <span>▶ ${currentLang === 'ar' ? 'تفعيل وتشغيل' : 'Activate & Run'}</span>
                </div>
            </div>
        `;
    });
}

function transitionView(callback) {
    const activeView = document.querySelector('.page-view.active');
    activeView.classList.add('telegram-dissolve');
    setTimeout(() => {
        activeView.classList.remove('active', 'telegram-dissolve');
        callback();
    }, 380);
}

function goToDashboard() {
    userXP += 10;
    document.getElementById('xpCounter').innerText = userXP + " XP";
    transitionView(() => {
        const dash = document.getElementById('dashboardView');
        dash.classList.add('active', 'soft-fade-in');
        window.scrollTo({top: 0, behavior: 'smooth'});
    });
}

function openServicePage(pageNum) {
    transitionView(() => {
        renderServiceContent(pageNum);
        const serviceView = document.getElementById('serviceView');
        serviceView.classList.add('active', 'soft-fade-in');
        window.scrollTo({top: 0, behavior: 'smooth'});
    });
}

function renderServiceContent(pageNum) {
    const sData = activeAxes[pageNum - 1];
    const prevPage = pageNum === 1 ? 100 : pageNum - 1;
    const nextPage = pageNum === 100 ? 1 : pageNum + 1;

    const card = document.getElementById('serviceCardContent');
    card.innerHTML = `
        <div class="card-header">
            <div class="card-title">${sData.title}</div>
            <div class="page-counter">AXIS ${pageNum < 10 ? '0' + pageNum : pageNum} / 100</div>
        </div>
        <div class="content-body">
            <p>${sData.desc}</p>
            <div class="interactive-box">${sData.status}</div>
            
            <div class="action-bar-grid">
                <div class="action-card" onclick="alert('تم تفعيل مصنع الأفكار الجذرية لهذا المحور بنجاح!')">
                    <div style="font-weight:bold; color:var(--holo-primary);">💡 مصنع الأفكار</div>
                    <div style="font-size:0.75rem; color:var(--text-muted); margin-top:4px;">توليد خطط مستقبلية غير مطروحة</div>
                </div>
                <div class="action-card" onclick="alert('تم ربط النظام المالي ومحفظة الرموز الذكية!')">
                    <div style="font-weight:bold; color:var(--holo-gold);">💰 النظام المالي</div>
                    <div style="font-size:0.75rem; color:var(--text-muted); margin-top:4px;">إدارة التدفقات والأصول الذكية</div>
                </div>
                <div class="action-card" onclick="alert('تم مزامنة الوكلاء المفتوحين وأوزان الشبكة العصبية!')">
                    <div style="font-weight:bold; color:var(--holo-secondary);">🧠 الوكلاء والأوزان</div>
                    <div style="font-size:0.75rem; color:var(--text-muted); margin-top:4px;">تعديل حر بدون قيود سحابية</div>
                </div>
            </div>
        </div>
        <div class="nav-controls">
            <button class="nav-btn btn-home" onclick="openServicePage(${prevPage})">← ${currentLang === 'ar' ? 'السابق' : 'Prev'}</button>
            <button class="nav-btn btn-home" onclick="goToDashboard()">${currentLang === 'ar' ? 'الرئيسية ⌂' : 'Home ⌂'}</button>
            <button class="nav-btn" onclick="openServicePage(${nextPage})">${currentLang === 'ar' ? 'التالي' : 'Next'} →</button>
        </div>
    `;
}

renderDashboard(activeAxes);

const bgCanvas = document.getElementById('bgCanvas');
const bgCtx = bgCanvas.getContext('2d');
let w, h;
function resizeBg() { w = bgCanvas.width = window.innerWidth; h = bgCanvas.height = window.innerHeight; }
window.addEventListener('resize', resizeBg);
resizeBg();

const particles = Array.from({length: 45}, () => ({x: Math.random()*w, y: Math.random()*h, vx: (Math.random()-0.5)*0.3, vy: (Math.random()-0.5)*0.3}));
function animateBg() {
    bgCtx.clearRect(0, 0, w, h);
    bgCtx.fillStyle = 'rgba(0, 255, 204, 0.3)';
    bgCtx.strokeStyle = 'rgba(0, 255, 204, 0.04)';
    particles.forEach((p, i) => {
        p.x += p.vx; p.y += p.vy;
        if(p.x<0||p.x>w) p.vx*=-1; if(p.y<0||p.y>h) p.vy*=-1;
        bgCtx.beginPath(); bgCtx.arc(p.x, p.y, 1.2, 0, Math.PI*2); bgCtx.fill();
        for(let j=i+1; j<particles.length; j++) {
            let p2 = particles[j];
            if(Math.hypot(p.x-p2.x, p.y-p2.y) < 140) {
                bgCtx.beginPath(); bgCtx.moveTo(p.x, p.y); bgCtx.lineTo(p2.x, p2.y); bgCtx.stroke();
            }
        }
    });
    requestAnimationFrame(animateBg);
}
animateBg();
</script>
</body>
</html>
"""

class UltimateHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(ULTIMATE_HTML.encode('utf-8'))

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), UltimateHandler) as httpd:
        print(f"NEXORA OMNI ULTIMATE ONLINE AT http://127.0.0.1:{PORT}")
        httpd.serve_forever()
