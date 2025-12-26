import streamlit as st
import requests
import time
import telebot

# بيانات البوت الخاصة بك
TOKEN = '8485193296:AAGcIe-varcy4gxqu0_NRz3tAKwcYOHyMCw'
ID = 7638628794
bot = telebot.TeleBot(TOKEN)

st.title("📡 رادار الماك السحابي")
host = st.text_input("رابط السيرفر", "dm.lion-ott.com")
mac = st.text_input("الماك آدرس", placeholder="00:1A:79:XX:XX:XX")

if st.button("تفعيل المراقبة"):
    st.success("🚀 الرادار يعمل الآن في السحاب.. ستصلك رسالة فور خلو الماك.")
    while True:
        try:
            h = {'User-Agent': 'MAG254', 'Cookie': f'mac={mac};'}
            r = requests.get(f"http://{host}/portal.php?type=stb&action=get_profile", headers=h, timeout=10).json()
            active = r['js'].get('active_cons', '1')
            if active == "0":
                bot.send_message(ID, f"🎯 صيد! الماك متاح الآن:\n`{mac}`")
                break
            time.sleep(300) # فحص كل 5 دقائق
        except:
            time.sleep(60)
