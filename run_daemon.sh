#!/data/data/com.termux/files/usr/bin/env bash

# 1. تحديث جيثب وسحب أي أفكار/تطويرات جديدة تلقائياً
if [ -d ".git" ]; then
    echo "[*] جاري فحص وسحب التحديثات من GitHub..."
    git pull origin main --quiet 2>/dev/null
fi

# 2. تشغيل خادم نكسورا الأولي في الخلفية مع ضمان الاستمرارية
echo "[*] تشغيل خادم NEXORA OMNI في الخلفية عبر nohup..."
nohup python3 nexora_ultimate.py > nexora.log 2>&1 &

# 3. الانتظار للحظات حتى يتأكد النظام من إقلاع الخدمة
sleep 2

# 4. فتح الواجهة تلقائياً في المتصفح الافتراضي للجهاز
echo "[+] فتح واجهة العميل السيبرانية تلقائياً..."
termux-open-url http://127.0.0.1:8080 2>/dev/null || am start -a android.intent.action.VIEW -d "http://127.0.0.1:8080" 2>/dev/null

echo "[✓] تم التجميع والتشغيل بنجاح! المنظومة تعمل الآن في الخلفية بشكل دائم."
