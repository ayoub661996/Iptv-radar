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

# ============ 📺 القنوات المستهدفة (بناءً على الصور) ============
CHANNELS_KEYS = {
    "BEIN AFRICA CUP 2025": ["AFRICA", "2025"], 
    "IARI BEIN SPORTS 8K": ["8K", "IARI"], 
    "IARI BEIN SPORTS 4K": ["4K", "IARI"]  
}

# ============ 🎨 واجهة التطبيق الاحترافية ============
st.set_page_config(page_title="Radar Pro STB", page_icon="📡")
st.markdown("<h1 style='text-align: center; color: #1E88E5;'>📡 رادار الماك (الحالة + المتصلين + القنوات)</h1>", unsafe_allow_html=True)

# إدارة نص الإدخال
if "input_area" not in st.session_state:
    st.session_state["input_area"] = ""

raw_data = st.text_area("🚀 أدخل الرابط والماك (نسخ ولصق عشوائي):", 
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

# ============ ⚙️ وظيفة فحص السيرفر ============
def check_server_status(host):
    """التحقق من اتصال السيرفر بالإنترنت"""
    try:
        # محاولة الوصول للبوابة الأساسية للسيرفر
        response = requests.get(f"http://{host}/", timeout=5)
        if response.status_code in [200, 404, 403]: 
            return "✅ يعمل (Online)"
    except:
        pass
    return "❌ معطل أو محظور (Offline)"

# ============ 🚀 محرك التشغيل الرئيسي ============
if btn_start:
    if raw_data:
        # استخراج الماكات والروابط باستخدام Regex
        macs = list(set(re.findall(r'(?:[0-9A-F]{2}[:]){5}[0-9A-F]{2}', raw_data.upper())))
        host_match = re.search(r'(https?://[^\s/$.?#].[^\s]*)', raw_data)
        
        if host_match and macs:
            full_url = host_match.group(0).split('/portal.php')[0].strip('/')
            clean_host = full_url.replace("http://", "").replace("https://", "").split('/')[0]
            
            # فحص حالة السيرفر
            server_status = check_server_status(clean_host)
            
            st.info(f"🔎 **تحليل البيانات:**\n\n🌐 الرابط (URL): `{full_url}`\n📊 حالة السيرفر: {server_status}")
            
            placeholder = st.empty()
            
            while True:
                for current_mac in macs:
                    placeholder.info(f"⏳ فحص الماك: {current_mac}")
                    
                    headers = {'User-Agent': 'MAG254', 'Cookie': f'mac={current_mac}'}
                    base_url = f"{full_url}/portal.php"
                    
                    try:
                        # طلب البروفايل لمعرفة المتصلين
                        url_prof = f"{base_url}?type=stb&action=get_profile&force_stb=1"
                        start_time = time.time()
                        r_prof = requests.get(url_prof, headers=headers, timeout=7)
                        latency = (time.time() - start_time) * 1000
                        
                        if r_prof.status_code == 200:
                            match = re.search(r'"active_cons"\s*:\s*"(\d+)"', r_prof.text)
                            active = match.group(1) if match else "1"

                            if active == "0": # الماك متاح للاستخدام
                                # فحص وجود القنوات المفضلة
                                url_ch = f"{base_url}?type=itv&action=get_all_channels"
                                r_ch = requests.get(url_ch, headers=headers, timeout=7)
                                ch_text = r_ch.text.upper()
                                found_channels = [f"✅ {n}" for n, k in CHANNELS_KEYS.items() if all(x in ch_text for x in k)]
                                
                                # إرسال تقرير الصيد للتليجرام (بدون اسم)
                                report = (
                                    f"📡 **تقرير الرادار المتكامل**\n\n"
                                    f"🌐 **السيرفر (URL):** {full_url}\n"
                                    f"🖥️ **الماك (MAC):** `{current_mac}`\n"
                                    f"📶 **حالة السيرفر:** {server_status}\n"
                                    f"👥 **المتصلون حالياً:** `0`\n"
                                    f"📊 **الاستقرار:** قوي (لا يقطع) ✅\n"
                                    f"📺 **القنوات المفضلة:**\n" + ("\n".join(found_channels) if found_channels else "❌ غير متوفرة")
                                )
                                bot.send_message(ID, report, parse_mode="Markdown")
                                st.success(f"🎯 تم الصيد: {current_mac}")
                                st.balloons()
                    except:
                        pass
                    time.sleep(1.2) # تأخير بسيط لحماية الـ IP
                
                placeholder.warning("🔄 دورة مكتملة.. إعادة المسح...")
                time.sleep(10)
        else:
            st.error("❌ لم يتم العثور على رابط URL أو عناوين MAC صحيحة.")
    else:
        st.warning("⚠️ يرجى لصق البيانات في الصندوق أولاً.")
