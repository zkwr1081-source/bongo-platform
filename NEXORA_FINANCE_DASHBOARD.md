# NEXORA Finance Control Dashboard

واجهة عربية محلية لمراقبة وتشغيل **NEXORA Finance Observer**. الواجهة مستقلة عن بقية تطبيق BONGO ولا تعدّل واجهاته أو قاعدة بياناته.

## ما توفره

- حالة المراقب: تشغيل / إيقاف.
- قراءة سوق عامة واحدة عند الطلب، أو تشغيل الجمع الدوري.
- عرض أحدث قراءات السوق المحفوظة في SQLite.
- عرض سجلات الوكلاء المسجلة وسجلات التوزيع المحاسبي.
- حماية نقاط API برمز Bearer اختياري.
- لا تداول، ولا محافظ، ولا تحويل أموال، ولا إرسال رسائل، ولا أوامر نظام.

> إشارات السوق وصف لحركة مرصودة خلال 24 ساعة وليست توقعاً أو توصية استثمارية. سجلات التوزيع حالتها **RECORDED_NOT_PAID** ولا تعني دفعاً.

## التشغيل على Termux أو Linux

من مجلد المستودع:

~~~bash
على Termux ثبّت الحزم الخفيفة المتوافقة مع Android:

~~~bash
python -m pip install -r requirements-termux.txt
~~~

على Linux أو خادم اعتيادي استخدم requirements.txt. ثم شغّل:

~~~bash
export NEXORA_DASHBOARD_HOST=127.0.0.1
export NEXORA_DASHBOARD_PORT=8094
python nexora_finance_dashboard.py
~~~

افتح في متصفح الهاتف أو الحاسوب الذي يشغّل الخدمة:

~~~text
http://127.0.0.1:8094
~~~

ثم اضغط **تشغيل** لبدء المراقب. زر **قراءة الآن** يجلب قراءة واحدة فقط عندما يكون المراقب متوقفاً.

## الإعدادات

| المتغير | الافتراضي | الغرض |
|---|---:|---|
| NEXORA_FINANCE_DB | nexora_finance_observer.db | ملف SQLite المشترك مع المراقب |
| NEXORA_DASHBOARD_HOST | 127.0.0.1 | عنوان الاستماع المحلي |
| NEXORA_DASHBOARD_PORT | 8094 | منفذ الواجهة |
| NEXORA_DASHBOARD_TOKEN | فارغ | رمز Bearer لحماية API |
| NEXORA_AUTO_START | 0 | اجعل المراقب يبدأ تلقائياً عند تشغيل الواجهة |
| NEXORA_WORKERS | 4 | إعداد محدود محفوظ من المراقب (ليس عدد وكلاء متزامنين) |
| NEXORA_POLL_SECONDS | 300 | فترة الجمع، 60 ثانية على الأقل |

## الوصول من جهاز آخر

الأفضل إبقاء الخدمة على 127.0.0.1. إذا غيّرت عنوان الاستماع إلى عنوان غير محلي، يجب ضبط رمز عشوائي لا يقل عن 24 محرفاً:

~~~bash
export NEXORA_DASHBOARD_HOST=0.0.0.0
export NEXORA_DASHBOARD_TOKEN='ضع-رمزاً-عشوائياً-قوياً-محلياً'
~~~

لا تعرض المنفذ مباشرة على الإنترنت؛ رمز Bearer لا يغني عن HTTPS أو جدار ناري أو نفق آمن. لا تحفظ الرمز في Git ولا ترسله في المحادثات.

## تشغيل مستمر في Termux

يمكن إبقاء العملية داخل جلسة tmux:

~~~bash
pkg install tmux
tmux new -s nexora-finance
python nexora_finance_dashboard.py
~~~

للفصل عن الجلسة: اضغط Ctrl+B ثم D. للعودة: tmux attach -t nexora-finance. استمرار Android في الخلفية يعتمد على إعدادات البطارية والنظام؛ لا يوجد ضمان تشغيل 24/7 من دون ضبط الجهاز.

## الاختبارات

~~~bash
python -m pip install pytest httpx2
python -m pytest -q tests/test_nexora_finance_observer.py tests/test_nexora_finance_dashboard.py
~~~

نقاط API الأساسية: /api/status, /api/observations, /api/agents, /api/revenue-allocations, /api/observer/start, /api/observer/stop, /api/observer/once.
