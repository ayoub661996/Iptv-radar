import streamlit as st
import telebot
import time

# التوكن الجديد الذي استخرجته من BotFather الآن
TOKEN = "8485193296:AAHpW18fpS74B3oaUGqNCYZjbodRPa76uLE"
ID = 7638628794
bot = telebot.TeleBot(TOKEN)

st.set_page_config(page_title="رادار الماك السحابي", page_icon="📡")
st.title("📡 رادار الماك السحابي")

host = st.text_input("🔗 رابط السيرفر", placeholder="مثال: eu.majes-line.co")
mac = st.text_input("🖥️ الماك آدرس", placeholder="00:1A:79:XX:XX:XX")

if st.button("🚀 تفعيل المراقبة"):
    if host and mac:
        try:
            # اختبار إرسال رسالة فورية لتأكد من التوكن الجديد
            bot.send_message(ID, f"✅ نجح الاتصال بالتوكن الجديد!\n🖥️ الماك: {mac}\n🌐 السيرفر: {host}")
            st.success("🎯 مبروك! وصلت الرسالة لتلغرام. الرادار يعمل الآن.")
            
            # هنا تبدأ حلقة المراقبة
            while True:
                time.sleep(300)
        except Exception as e:
            st.error(f"❌ خطأ: {e}")
            st.info("تأكد من الضغط على START في بوت تلغرام أولاً.")
    else:
        st.error("⚠️ يرجى إدخال البيانات")

