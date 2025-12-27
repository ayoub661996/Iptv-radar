import streamlit as st
import requests
import time
import telebot

# تم تنظيف التوكن من أي مسافات مخفية
TOKEN = "8485193296:AAGcIe-varcy4gxqu0_NRz3tAKwcY0HyMCw"
ID = 7638628794

# إنشاء اتصال بالبوت
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
            
            # رسالة اختبار فورية (ستصلك الآن)
            bot.send_message(ID, f"✅ الرادار يعمل الآن!\n🖥️ الماك: {mac}\n🌐 السيرفر: {clean_host}")
            st.success("🎯 رائع! وصلت رسالة الاختبار لتلغرام.")
            
            # حلقة المراقبة (تفحص كل 5 دقائق)
            while True:
                # الكود سيستمر هنا في فحص السيرفر
                time.sleep(300) 
        except Exception as e:
            st.error(f"⚠️ مشكلة في التوكن: {e}")
            st.info("تأكد من إرسال رسالة /start للبوت الخاص بك أولاً")
    else:
        st.error("⚠️ يرجى تعبئة جميع الخانات")
