# NEXUS Master Core

محرك تنسيق دوري لوحدات استخبارات السوق، التداول، Micro-SaaS، المخزون، المحتوى، الخزينة، إعادة التوازن، الأصول الرقمية والامتثال.

## الحالة الأمنية والتشغيلية

**هذه النسخة محاكاة فقط.** لا تتصل ببورصة أو بنك أو محفظة ولا تنفذ تداولاً أو تحويلاً مالياً. نتائج السوق والخدمات والمخزون والنشر افتراضية. كل قيد مالي تجريبي يحمل الحالة `SIMULATED_ONLY`.

لا تستخدم هذه النسخة لاتخاذ قرارات مالية أو تشغيل أموال حقيقية. أي تكامل مستقبلي يحتاج مزوداً موثوقاً، صلاحيات محدودة، مفاتيح في مدير أسرار، حدود مخاطر، موافقات بشرية، idempotency، ومراجعة امتثال مستقلة.

## المتطلبات والتشغيل

Python 3.10+، دون اعتماديات خارجية:

```bash
cd nexus_master_core
python -m engine --once
python -m engine --interval 15
```

لتحديد قاعدة البيانات:

```bash
NEXUS_DB_PATH=/path/to/nexus.db python -m engine --once
```

أوقف التشغيل الدوري بـ Ctrl+C. افتراضياً تُنشأ قاعدة `nexus_master_core.db` في مجلد التشغيل.

## قاعدة البيانات

- `agent_cycles`: سجل كل دورة ونتيجتها.
- `financial_ledger`: سجل توضيحي غير قابل للالتباس مع التحويل الحقيقي، بحالة `SIMULATED_ONLY`.
- SQLite مع WAL وbusy timeout وعمليات parameterized.

## الاختبارات

```bash
python -m pytest -q
```

## الوحدات

1. MarketIntelligenceAgent
2. AlgorithmicTradingAgent (fail-closed)
3. MicroSaaSBackend
4. InventoryManagerAgent
5. ContentGeneratorAgent
6. VaultTransferAgent (simulation ledger only)
7. PortfolioRebalancer
8. DigitalRealEstateAgent
9. SecretsVault
10. ComplianceReporter

التشغيل المستمر ليس خدمة سحابية دائمة بحد ذاته؛ استخدم مدير عمليات مناسباً بعد إعداد المراقبة والنسخ الاحتياطي.
