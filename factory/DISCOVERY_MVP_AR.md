# تشغيل محرك اكتشاف الاحتياجات — BONGO

## المتطلبات
Python 3.10+ وFastAPI وUvicorn. لا يحتاج المحرك الأساسي إلى اتصال بالإنترنت أو مكتبات خارجية.

## التشغيل محلياً
من جذر المستودع:

```bash
python -m pip install -r requirements.txt
uvicorn factory.discovery_app:app --host 127.0.0.1 --port 8094
```

افتح http://127.0.0.1:8094 من المتصفح على الجهاز نفسه. توثيق نقاط API في /docs.

## اختبار المحرك
```bash
python -m unittest discover -s tests -v
```

## استيراد الأدلة
جهّز ملف JSON محلياً يحتوي قائمة سجلات، أو كائناً بمفتاح evidence. الحقول المطلوبة: title, source_name, source_url, excerpt, domain, claim_type, geography. الترخيص غير المعروف يسجل باسم unspecified ولا يُفترض.

```bash
python -c "from factory.discovery_engine import *; print(import_json(DiscoveryStore(), 'evidence.json'))"
```

## حدود النسخة
- لا توجد موصلات إنترنت أو جمع تلقائي حتى الآن؛ الإدخال يدوي أو من ملف محلي.
- لا يوجد نموذج لغوي أو ادعاء باكتشاف اختراعات غير مسبوقة.
- الترتيب أداة فرز أولية فقط، وليس تحققاً ميدانياً أو تجارياً.
- كل شيء يبقى محلياً ما دمت تشغّل الخدمة على 127.0.0.1 ولا ترفع ملف قاعدة البيانات.
