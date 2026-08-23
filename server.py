import http.server
import socketserver
import json

PORT = 8080

HTML_INTERFACE = """<!DOCTYPE html>
<html lang="ar" dir="rtl" id="htmlRoot">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NEXORA OMNI ECOSYSTEM</title>
<link href="https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>
:root {
    --holo-primary: #00ffcc;
    --holo-secondary: #0088ff;
    --holo-accent: #bf00ff;
    --holo-gold: #ffaa00;
    --bg-space: #010308;
    --glass-bg: rgba(3, 8, 18, 0.9);
    --border-glow: rgba(0, 255, 204, 0.35);
    --text-main: #e2e8f0;
    --text-muted: #64748b;
}

* { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Cairo', sans-serif; }
body { background: var(--bg-space); color: var(--text-main); min-height: 100vh; overflow-x: hidden; position: relative; }

#bgCanvas { position: fixed; top: 0; left: 0; width: 100vw; height: 100vh; z-index: -1; pointer-events: none; }

.header {
    background: rgba(2, 5, 12, 0.95);
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

.logo { font-weight: 900; font-size: 1.2rem; color: var(--holo-primary); display: flex; align-items: center; gap: 10px; cursor: pointer; }
.badge { background: linear-gradient(135deg, var(--holo-primary), var(--holo-secondary)); color: #000; padding: 3px 10px; border-radius: 6px; font-size: 0.7rem; font-weight: 900; }

.controls-header { display: flex; gap: 12px; align-items: center; }
.lang-select { background: rgba(5,12,25,0.9); border: 1px solid var(--border-glow); color: var(--holo-primary); padding: 6px 12px; border-radius: 8px; font-weight: 700; cursor: pointer; outline: none; }

.container { max-width: 1200px; margin: 30px auto; padding: 0 20px; }

/* تأثير التلاشي والانكماش الذكي مثل تلجرام */
.view-container {
    transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);
    transform-origin: center;
}
.telegram-dissolve {
    transform: scale(0) translateY(50px) rotate(5deg);
    opacity: 0;
    filter: blur(15px);
}

/* تأثير الوميض الهادئ والناعم للظهور */
@keyframes softPulseIn {
    0% { opacity: 0; transform: scale(0.95) translateY(-10px); filter: blur(5px); }
    50% { opacity: 0.8; filter: blur(2px); }
    100% { opacity: 1; transform: scale(1) translateY(0); filter: blur(0); }
}
.soft-fade-in {
    animation: softPulseIn 0.5s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.page-view { display: none; }
.page-view.active { display: block; }

/* شبكة المربعات الذكية للخدمات */
.grid-dashboard { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; }
.service-square {
    background: var(--glass-bg);
    backdrop-filter: blur(15px);
    border: 1px solid var(--border-glow);
    border-radius: 16px;
    padding: 25px;
    cursor: pointer;
    transition: all 0.3s ease;
    display: flex;
    flex-direction: column;
    justify-content: space-between;
    min-height: 180px;
    box-shadow: 0 8px 30px rgba(0,0,0,0.6);
    position: relative;
    overflow: hidden;
}
.service-square::before {
    content: '';
    position: absolute;
    top: 0; right: 0; width: 4px; height: 100%;
    background: linear-gradient(to bottom, var(--holo-primary), var(--holo-secondary));
    opacity: 0.7;
}
.service-square:hover {
    border-color: var(--holo-primary);
    transform: translateY(-5px) scale(1.02);
    box-shadow: 0 12px 40px rgba(0,255,204,0.25);
}
.square-num { font-family: 'JetBrains Mono', monospace; font-size: 0.8rem; color: var(--holo-primary); font-weight: 700; }
.square-title { font-size: 1.05rem; font-weight: 900; color: var(--text-main); margin: 10px 0; }

/* بطاقات الصفحات التفصيلية */
.card { background: var(--glass-bg); backdrop-filter: blur(15px); border: 1px solid var(--border-glow); border-radius: 16px; padding: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.8); min-height: 450px; display: flex; flex-direction: column; justify-content: space-between; }
.card-header { display: flex; justify-content: space-between; align-items: center; border-bottom: 1px solid rgba(255,255,255,0.1); padding-bottom: 15px; margin-bottom: 20px; }
.card-title { color: var(--holo-primary); font-size: 1.3rem; font-weight: 900; }
.page-counter { background: rgba(0,255,204,0.1); border: 1px solid var(--holo-primary); color: var(--holo-primary); padding: 5px 14px; border-radius: 20px; font-size: 0.85rem; font-weight: 700; font-family: 'JetBrains Mono', monospace; }

.content-body { flex: 1; display: flex; flex-direction: column; gap: 20px; font-size: 1rem; line-height: 1.8; color: var(--text-main); }
.interactive-box { background: rgba(1, 3, 7, 0.85); border: 1px solid rgba(0,255,204,0.25); border-radius: 12px; padding: 20px; font-family: 'JetBrains Mono', monospace; font-size: 0.9rem; color: var(--holo-primary); min-height: 140px; display: flex; align-items: center; justify-content: center; text-align: center; box-shadow: inset 0 0 15px rgba(0,255,204,0.05); }

.nav-controls { display: flex; justify-content: space-between; align-items: center; margin-top: 25px; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 20px; }
.nav-btn { background: linear-gradient(135deg, var(--holo-primary), var(--holo-secondary)); color: #000; border: none; font-weight: 900; padding: 12px 25px; border-radius: 10px; cursor: pointer; font-size: 0.95rem; transition: 0.3s; box-shadow: 0 0 20px rgba(0,255,204,0.3); }
.nav-btn:hover { opacity: 0.9; transform: translateY(-2px); }
.btn-home { background: rgba(5,12,25,0.9); border: 1px solid var(--holo-gold); color: var(--holo-gold); }
</style>
</head>
<body>

<canvas id="bgCanvas"></canvas>

<div class="header">
    <div class="logo" onclick="goToDashboard()">
        <span class="badge">NEXORA</span> 
        <span id="headerTitle">منظومة نكسورا الذكية</span>
    </div>
    <div class="controls-header">
        <select class="lang-select" id="langSelector" onchange="changeLanguage(this.value)">
            <option value="ar">العربية (Arabic)</option>
            <option value="en">English</option>
            <option value="fr">Français</option>
            <option value="es">Español</option>
            <option value="de">Deutsch</option>
        </select>
        <button class="nav-btn btn-home" style="padding: 6px 14px; font-size:0.8rem;" onclick="goToDashboard()" id="homeBtnText">الرئيسية</button>
    </div>
</div>

<div class="container">

    <!-- لوحة التحكم الرئيسية (مربعات الخدمات) -->
    <div id="dashboardView" class="page-view active view-container">
        <div style="margin-bottom: 20px;">
            <h1 style="color:var(--holo-primary); font-size:1.6rem; font-weight:900;" id="dashHeading">خدمات نكسورا المركزية (10 محاور)</h1>
            <p style="color:var(--text-muted); font-size:0.95rem;" id="dashSub">انقر على أي مربع خدمة لتفعيل العبور السينمائي الذكي.</p>
        </div>
        <div class="grid-dashboard" id="servicesGrid">
            <!-- سيتم تعبئتها ديناميكياً عبر الجافاسكريبت لضمان تفعيل كامل الأزرار ولغة النظام -->
        </div>
    </div>

    <!-- الصفحات الفردية للخدمات (1 إلى 10) -->
    <div id="serviceView" class="page-view view-container">
        <div class="card" id="serviceCardContent">
            <!-- المحتوى الداخلي يتغير حسب الصفحة النشطة -->
        </div>
    </div>

</div>

<script>
// قاموس اللغات الشامل لجميع اللغات المطلوبة
const i18n = {
    ar: {
        headerTitle: "منظومة نكسورا الذكية",
        homeBtn: "الرئيسية",
        dashHeading: "خدمات نكسورا المركزية (10 محاور)",
        dashSub: "انقر على أي مربع خدمة لتفعيل العبور السينمائي الذكي.",
        prev: "السابق",
        next: "التالي",
        backToDash: "العودة للرئيسية ⌂",
        services: [
            { title: "1. الممر العصبي غير المتزامن", desc: "معالجة الطلبات البرمجية والوكلاء بشكل غير متزامن باستخدام asyncio داخل بيئة Termux لضمان استجابة فورية.", status: "حالة الممر: نشط ويعمل بتناغم فوري بدون تأخير." },
            { title: "2. قاعدة بيانات المتجهات والذاكرة المطلقة", desc: "محرك بحث دلالي محلي يحافظ على السياق التاريخي للمحادثة بدقة تامة دون نسيان أي تفصيل مهما طال الحوار.", status: "الذاكرة الدلالية متصلة ومحدثة بنجاح تام." },
            { title: "3. حارس المعالجة الذاتية للأخطاء", desc: "مراقب برمجي داخلي يرصد الاستثناءات ويعيد تشغيل الخدمات المعطلة تلقائياً مع تسجيل وتصحيح الأخطاء فورياً.", status: "حارس الأخطاء يعمل في الخلفية بكفاءة عالية." },
            { title: "4. نفق الاتصال الآمن للواجهة", desc: "ربط محلي ومشفر بالكامل يتيح فتح واجهة العملاء الهلوجرامية من أي متصفح خارجي بسرعة وكفاءة فائقة.", status: "النفق الآمن مؤمن باتصال SSL محلي." },
            { title: "5. نظام التخزين المؤقت للردود", desc: "تخزين الأوامر المتكررة في ذاكرة الوصول العشوائي (RAM) لتقليل استهلاك الموارد وتسريع ظهور الردود إلى أجزاء من الثانية.", status: "معدل استجابة الذاكرة المؤقتة: فوري (0.01ms)." },
            { title: "6. جدول المهام الزمنية التلقائية", desc: "محرك جدولة داخلي بايثوني لتنفيذ مهام المزامنة والتحديثات الخلفية بدقة مطلقة دون تدخل بشري.", status: "الجدول الزمني الخلفي نشط ومنتظم." },
            { title: "7. تشفير البلوكشين المتقدم", desc: "توقيعات رقمية متصلة ومرتبطة بـ Merkle Trees لضمان استحالة التعديل أو التلاعب بسجلات المعاملات والبيانات.", status: "الكتل المشفرة والمدققة آمنة بنسبة 100%." },
            { title: "8. إدارة الموارد واستهلاك الذاكرة", desc: "مراقبة استهلاك المعالج والخفض المؤقت للعمليات الثانوية عند ارتفاع الحمل لمنع خروج النظام عن الخدمة داخل Termux.", status: "معدل استهلاك المعالج والذاكرة مستقر تماماً." },
            { title: "9. توثيق واجهات الـ API", desc: "صفحة توثيق تفاعلية لجميع مسارات الخادم لتسهيل عملية ربط واجهات الجوال وتطبيقات Expo المستقبلية بسلاسة.", status: "مسارات API جاهزة وموثقة بالكامل." },
            { title: "10. النسخ الاحتياطي التلقائي المشفر", desc: "أداة دورية تنشئ نسخاً احتياطية مشفرة لقاعدة البيانات وملفات الإعدادات وتحفظها في مسار آمن بعيداً عن مجلد العمل.", status: "تم أخذ آخر نسخة احتياطية مشفرة بنجاح." }
        ]
    },
    en: {
        headerTitle: "Nexora Intelligent Ecosystem",
        homeBtn: "Home",
        dashHeading: "Nexora Core Services (10 Axes)",
        dashSub: "Click any service box to trigger smart cinematic transition.",
        prev: "Previous",
        next: "Next",
        backToDash: "Back to Home ⌂",
        services: [
            { title: "1. Asynchronous Neural Pipeline", desc: "Asynchronous processing of requests and agents using asyncio inside Termux for instant responses.", status: "Pipeline status: Active with zero latency." },
            { title: "2. Vector Database & Absolute Memory", desc: "Local semantic search engine maintaining full conversation context without forgetting any detail.", status: "Semantic memory connected and updated." },
            { title: "3. Self-Healing Error Daemon", desc: "Internal software monitor that detects exceptions, restarts failed services, and logs corrections.", status: "Error sentinel running smoothly in background." },
            { title: "4. Secure Local/Remote Tunneling", desc: "Fully encrypted local bonding allowing fast access to holographic client interfaces from external browsers.", status: "Secure tunnel bonded with local SSL." },
            { title: "5. RAM Response Caching", desc: "Caching repetitive commands in RAM to reduce resource consumption and speed up responses.", status: "Cache response rate: Instant (0.01ms)." },
            { title: "6. Automated APScheduler Integration", desc: "Internal Python scheduling engine to execute background sync and update tasks with high precision.", status: "Background scheduler active and regular." },
            { title: "7. Advanced Blockchain Integrity", desc: "Connected digital signatures linked via Merkle Trees ensuring immutability of transaction records.", status: "Encrypted blocks secured at 100%." },
            { title: "8. Resource & Memory Throttling", desc: "Monitoring CPU consumption (`psutil`) and temporarily throttling secondary processes under high load.", status: "CPU and memory usage completely stable." },
            { title: "9. OpenAPI / Swagger Documentation", desc: "Interactive documentation page for all server endpoints to seamlessly connect mobile Expo apps.", status: "API routes ready and fully documented." },
            { title: "10. Automated Encrypted Backups", desc: "Periodic tool generating encrypted snapshots of databases and configurations safely stored away.", status: "Latest encrypted backup successfully created." }
        ]
    },
    fr: {
        headerTitle: "Écosystème Intelligent Nexora",
        homeBtn: "Accueil",
        dashHeading: "Services Centraux Nexora (10 Axes)",
        dashSub: "Cliquez sur une boîte pour déclencher la transition cinématographique.",
        prev: "Précédent",
        next: "Suivant",
        backToDash: "Retour à l'accueil ⌂",
        services: [
            { title: "1. Pipeline Neural Asynchrone", desc: "Traitement asynchrone des requêtes avec asyncio sous Termux.", status: "Statut : Actif sans latence." },
            { title: "2. Base de Données Vectorielle", desc: "Moteur de recherche sémantique local pour un contexte parfait.", status: "Mémoire sémantique connectée." },
            { title: "3. Démon d'Auto-Guérison", desc: "Surveillance interne des erreurs et redémarrage automatique.", status: "Sentinelle active." },
            { title: "4. Tunneling Sécurisé", desc: "Liaison chiffrée locale pour interfaces holographiques.", status: "Tunnel sécurisé." },
            { title: "5. Cache RAM Intelligent", desc: "Mise en cache des commandes répétitives pour une vitesse maximale.", status: "Cache instantané." },
            { title: "6. Planificateur de Tâches", desc: "Moteur de planification interne en Python.", status: "Planificateur actif." },
            { title: "7. Intégrité Blockchain Avancée", desc: "Signatures numériques liées par Arbres de Merkle.", status: "Blocs sécurisés." },
            { title: "8. Gestion des Ressources", desc: "Surveillance CPU et limitation dynamique.", status: "Ressources stables." },
            { title: "9. Documentation API", desc: "Page interactive pour endpoints et applications mobiles.", status: "API documentée." },
            { title: "10. Sauvegardes Automatiques", desc: "Création périodique de sauvegardes chiffrées.", status: "Sauvegarde réussie." }
        ]
    },
    es: {
        headerTitle: "Ecosistema Inteligente Nexora",
        homeBtn: "Inicio",
        dashHeading: "Servicios Centrales de Nexora (10 Ejes)",
        dashSub: "Haga clic en cualquier cuadro para activar la transición cinemática.",
        prev: "Anterior",
        next: "Siguiente",
        backToDash: "Volver al inicio ⌂",
        services: [
            { title: "1. Canalización Neural Asíncrona", desc: "Procesamiento asíncrono usando asyncio en Termux.", status: "Estado: Activo sin latencia." },
            { title: "2. Base de Datos Vectorial", desc: "Búsqueda semántica local que preserva el contexto completo.", status: "Memoria semántica conectada." },
            { title: "3. Daemon de Autocuración", desc: "Monitor interno que detecta excepciones y reinicia servicios.", status: "Centinela activo." },
            { title: "4. Túnel de Conexión Segura", desc: "Enlace cifrado local para interfaces holográficas.", status: "Túnel asegurado." },
            { title: "5. Caché de Respuestas RAM", desc: "Almacenamiento en caché para velocidad extrema.", status: "Caché instantáneo." },
            { title: "6. Planificador de Tareas", desc: "Motor de programación interno en Python.", status: "Programador activo." },
            { title: "7. Integridad Blockchain Avanzada", desc: "Firmas digitales conectadas mediante Merkle Trees.", status: "Bloques seguros." },
            { title: "8. Gestión de Recursos", desc: "Monitoreo de CPU y limitación de carga en Termux.", status: "Recursos estables." },
            { title: "9. Documentación API", desc: "Página interactiva para rutas de servidor y apps Expo.", status: "API lista." },
            { title: "10. Copias de Seguridad Automáticas", desc: "Generación periódica de respaldos cifrados.", status: "Respaldo creado." }
        ]
    },
    de: {
        headerTitle: "Nexora Intelligentes Ökosystem",
        homeBtn: "Startseite",
        dashHeading: "Nexora Zentrale Dienste (10 Achsen)",
        dashSub: "Klicken Sie auf ein Feld für einen cineastischen Übergang.",
        prev: "Vorherige",
        next: "Nächste",
        backToDash: "Zur Startseite ⌂",
        services: [
            { title: "1. Asynchrone Neurale Pipeline", desc: "Asynchrone Verarbeitung mit asyncio in Termux.", status: "Status: Aktiv ohne Latenz." },
            { title: "2. Vektordatenbank & Absoluter Speicher", desc: "Lokale semantische Suche für perfekten Kontext.", status: "Speicher verbunden." },
            { title: "3. Selbstheilungs-Daemon", desc: "Interne Überwachung zur Fehlerbehebung.", status: "Wächter aktiv." },
            { title: "4. Sicheres Tunneling", desc: "Verschlüsselte lokale Verbindung für Hologramme.", status: "Tunnel sicher." },
            { title: "5. RAM-Cashing", desc: "Zwischenspeicherung für sofortige Antworten.", status: "Cache aktiv." },
            { title: "6. Automatisierter APScheduler", desc: "Interner Python-Planungsmotor.", status: "Planer aktiv." },
            { title: "7. Erweiterte Blockchain-Integrität", desc: "Digitale Signaturen über Merkle Trees.", status: "Blöcke gesichert." },
            { title: "8. Ressourcenmanagement", desc: "CPU-Überwachung und Lastausgleich in Termux.", status: "Ressourcen stabil." },
            { title: "9. API-Dokumentation", desc: "Interaktive Dokumentationsseite für Endpunkte.", status: "API bereit." },
            { title: "10. Automatisierte Backups", desc: "Regelmäßige verschlüsselte Sicherungen.", status: "Backup erstellt." }
        ]
    }
};

let currentLang = 'ar';

function changeLanguage(lang) {
    currentLang = lang;
    const dir = (lang === 'ar') ? 'rtl' : 'ltr';
    document.getElementById('htmlRoot').setAttribute('dir', dir);
    
    // تحديث النصوص العامة
    document.getElementById('headerTitle').innerText = i18n[lang].headerTitle;
    document.getElementById('homeBtnText').innerText = i18n[lang].homeBtn;
    document.getElementById('dashHeading').innerText = i18n[lang].dashHeading;
    document.getElementById('dashSub').innerText = i18n[lang].dashSub;
    
    renderDashboard();
}

function renderDashboard() {
    const grid = document.getElementById('servicesGrid');
    grid.innerHTML = '';
    i18n[currentLang].services.forEach((s, index) => {
        const pageNum = index + 1;
        grid.innerHTML += `
            <div class="service-square" onclick="openServicePage(${pageNum})">
                <div>
                    <div class="square-num">0${pageNum} / 10</div>
                    <div class="square-title">${s.title}</div>
                </div>
                <div style="font-size:0.8rem; color:var(--text-muted); display:flex; align-items:center; gap:5px;">
                    <span>▶ تفعيل الخدمة</span>
                </div>
            </div>
        `;
    });
}

// تنفيذ تأثير التلاشي والانكماش (مثل تلجرام) ثم فتح الصفحة التالية بوميض هادئ
function transitionView(callback) {
    const activeView = document.querySelector('.page-view.active');
    activeView.classList.add('telegram-dissolve');
    
    setTimeout(() => {
        activeView.classList.remove('active', 'telegram-dissolve');
        callback();
    }, 380);
}

function goToDashboard() {
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
    const sData = i18n[currentLang].services[pageNum - 1];
    const t = i18n[currentLang];
    
    // دورة مغلقة تامة (الصفحة 10 تعود تلقائياً لـ 1 والعكس)
    const prevPage = pageNum === 1 ? 10 : pageNum - 1;
    const nextPage = pageNum === 10 ? 1 : pageNum + 1;

    const card = document.getElementById('serviceCardContent');
    card.innerHTML = `
        <div class="card-header">
            <div class="card-title">${sData.title}</div>
            <div class="page-counter">0${pageNum} / 10</div>
        </div>
        <div class="content-body">
            <p>${sData.desc}</p>
            <div class="interactive-box">${sData.status}</div>
        </div>
        <div class="nav-controls">
            <button class="nav-btn btn-home" onclick="openServicePage(${prevPage})">← ${t.prev}</button>
            <button class="nav-btn btn-home" onclick="goToDashboard()">${t.backToDash}</button>
            <button class="nav-btn" onclick="openServicePage(${nextPage})">${t.next} →</button>
        </div>
    `;
}

// تهيئة الواجهة عند التحميل
renderDashboard();

/* خلفية حية متسقة لشبكة النيون */
const bgCanvas = document.getElementById('bgCanvas');
const bgCtx = bgCanvas.getContext('2d');
let w, h;
function resizeBg() { w = bgCanvas.width = window.innerWidth; h = bgCanvas.height = window.innerHeight; }
window.addEventListener('resize', resizeBg);
resizeBg();

const particles = Array.from({length: 35}, () => ({x: Math.random()*w, y: Math.random()*h, vx: (Math.random()-0.5)*0.3, vy: (Math.random()-0.5)*0.3}));
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

class NexoraServerHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/favicon.ico':
            self.send_response(204)
            self.end_headers()
        else:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_INTERFACE.encode('utf-8'))

if __name__ == '__main__':
    with socketserver.TCPServer(("", PORT), NexoraServerHandler) as httpd:
        print(f"NEXORA OMNI ECOSYSTEM ONLINE AT http://127.0.0.1:{PORT}")
        httpd.serve_forever()
