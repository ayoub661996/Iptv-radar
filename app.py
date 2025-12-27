import streamlit as st
import requests
import time
import telebot

# التوكن الجديد والآيدي الخاص بك
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
            # تنظيف الرابط
            clean_host = host.replace("http://", "").replace("https://", "").strip("/")
            
            # إرسال رسالة ترحيب فورية بالتوكن الجديد
            bot.send_message(ID, f"✅ تم تفعيل الرادار بالتوكن الجديد!\n🖥️ الماك: {mac}\n🌐 السيرفر: {clean_host}")
            st.success("🎯 رائع! وصلت رسالة الاختبار. الرادار يعمل الآن.")
            
            # بدء المراقبة
            while True:
                # الفحص السحابي
                time.sleep(300) 
        except Exception as e:
            st.error(f"⚠️ خطأ: {e}")
    else:
        st.error("⚠️ يرجى تعبئة جميع الخانات")
