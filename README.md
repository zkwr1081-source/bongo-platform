# BONGO
### ممرّ الحلول المتكامل · Integrated Solutions Platform

<div align="center">

**منصة قابلة للتوسّع لاكتشاف الخدمات وربطها وتشغيلها ومراقبتها من مكان واحد.**

[![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/) [![CI](https://img.shields.io/badge/CI-GitHub%20Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white)](https://github.com/zkwr1081-source/bongo-platform/actions)

</div>

---

## ✨ نظرة عامة

BONGO مشروع لبناء ممرّ موحّد للحلول والخدمات، مع بنية قابلة للتوسّع تسمح باكتشاف الخدمات والتكامل معها وتشغيلها ومتابعة صحتها.

## 🧩 المكوّنات الأساسية

| المكوّن | الدور |
|---|---|
| Service Discovery | اكتشاف الخدمات المسجّلة |
| Integration Layer | ربط الخدمات وتنسيق التكامل |
| API | واجهة الوصول البرمجية |
| Client Interface | واجهة العميل |
| Authentication Session | إدارة جلسات المصادقة |
| Runtime | تشغيل الخدمات |
| Health Monitoring | مراقبة الحالة |
| Plugin-ready Architecture | قابلية التوسّع بالإضافات |

> يعرض الوصف الداخلي للمشروع 1003 خدمة و1003 قدرة مسجّلة؛ ينبغي مطابقة هذه الأرقام مع بيانات التشغيل قبل اعتمادها في تقارير الإنتاج.

## 🚀 التشغيل المحلي

- **API:** http://127.0.0.1:8092
- **Client:** http://127.0.0.1:8093

ابدأ من ملفات الإعداد وتعليمات التشغيل الموجودة في المستودع، واضبط متغيرات البيئة المطلوبة قبل تشغيل الخدمات.

## 🧪 الجودة والتحقق

يحتوي المستودع على GitHub Actions للتحقق من بناء Python وتشغيل الاختبارات.

[عرض سير العمل والنتائج](https://github.com/zkwr1081-source/bongo-platform/actions)

## 🛡️ مبادئ المشروع

- الحفاظ على حدود واضحة بين الخدمات.
- جعل التكامل قابلاً للتوسّع والاختبار.
- عدم وضع كلمات المرور أو مفاتيح API داخل Git.
- التحقق من الصحة والاختبارات قبل النشر.

## تشغيل الوكلاء فعلياً

يتطلب التنفيذ اتصالاً بمزوّد متوافق مع واجهة OpenAI Chat Completions. اضبط القيم التالية في بيئة الخادم (ولا تحفظ المفتاح في Git):

```bash
export NEXORA_BASE_URL="https://api.openai.com/v1"
export NEXORA_API_KEY="YOUR_KEY"
export NEXORA_MODEL="YOUR_ENABLED_MODEL"
python server.py
```

افتح `http://127.0.0.1:8080` ثم انتقل إلى **الوكلاء** وأرسل مهمة. نقطة التنفيذ البرمجية هي `POST /api/agents/run`، وقائمة الوكلاء عبر `GET /api/agents`. افتراضياً تُرسل المهمة إلى وكيلي التنسيق والجودة، ويمكن تحديد حتى 10 معرّفات في الطلب. التنفيذ متزامن محدود بمهلة، وليس تشغيل وكلاء دائمين في الخلفية.

للتحقق من إعدادات المزوّد نفّذ:

```bash
python nexora_model_adapter.py
python -m unittest discover -s tests -p 'test_nexora*.py'
```

**الأمان:** الخادم يستمع افتراضياً على `127.0.0.1`. لا تعرّضه للإنترنت مباشرة. عند تشغيله خلف شبكة أو وكيل عكسي، عيّن `NEXORA_EXECUTION_TOKEN` ومرّر الرمز كـ Bearer Token إلى واجهة التنفيذ، واستخدم HTTPS وحدود معدل الطلبات. لوحة المتصفح المحلية لا ترسل هذا الرمز تلقائياً؛ لذلك اترك الخادم محلياً أو أضف طبقة مصادقة مناسبة قبل النشر الخارجي.

## 🤝 المساهمة

افتح Issue لوصف المشكلة أو الاقتراح، ثم قدّم Pull Request صغيراً يوضح التغيير وطريقة اختباره.

<div align="center">

**BONGO · Build. Connect. Orchestrate.**

</div>
