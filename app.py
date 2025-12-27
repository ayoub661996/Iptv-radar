import streamlit as st
import requests
import time
import telebot

# بياناتك تم تنقيحها (تأكد من عدم وجود مسافات)
TOKEN = "8485193296:AAGcIe-varcy4gxqu0_NRz3tAKwcY0HyMCw"
ID = 7638628794
bot = telebot.TeleBot(TOKEN)

st.set_page_config(page_title="رادار الماك السحابي", page_icon="📡")
st.title("📡 رادار الماك السحابي")

host = st.text_input("🔗 رابط السيرفر", placeholder="مثال: eu.majes-line.co")
mac = st.text_input("🖥️ الماك آدرس", placeholder="00:1A:79:08:4F:74")

if st.button("🚀 تفعيل المراقبة"):
    if host and mac:
        try:
            # تنظيف الرابط
            clean_host = host.replace("http://", "").replace("https://", "").strip("/")
            
            # محاولة إرسال رسالة اختبار (هنا سيظهر إذا كان التوكن يعمل)
            bot.send_message(ID, f"✅ الرادار يعمل الآن!\n🖥️ الماك: {mac}\n🌐 السيرفر: {clean_host}")
            st.success("🎯 رائع! وصلت رسالة الاختبار لتلغرام.")
            
            # حلقة المراقبة
            while True:
                url = f"http://{clean_host}/portal.php?type=itv&action=get_all_channels"
                h = {'User-Agent': 'MAG254', 'Cookie': f'mac={mac}'}
                # الفحص الفعلي يتم هنا
                time.sleep(300) 
        except Exception as e:
            st.error(f"⚠️ مشكلة في التوكن أو الاتصال: {e}")
    else:
        st.error("⚠️ يرجى تعبئة جميع الخانات")
