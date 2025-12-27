import streamlit as st
import requests
import time
import telebot

# بياناتك الصحيحة
TOKEN = '8485193296:AAGcIe-varcy4gxqu0_NRz3tAKwcY0HyMCw'
ID = 7638628794
bot = telebot.TeleBot(TOKEN)

st.set_page_config(page_title="رادار الماك السحابي", page_icon="📡")
st.title("📡 رادار الماك السحابي")

host = st.text_input("🔗 رابط السيرفر", placeholder="مثال: bes5.alphatx.me")
mac = st.text_input("🖥️ الماك آدرس", placeholder="00:1A:79:XX:XX:XX")

if st.button("🚀 تفعيل المراقبة"):
    if host and mac:
        try:
            # تنظيف الرابط من أي زوائد
            clean_host = host.replace("http://", "").replace("https://", "").strip("/")
            
            # رسالة اختبار فورية (ستصلك الآن)
            bot.send_message(ID, f"✅ تم تفعيل الرادار بنجاح!\n🖥️ الماك: {mac}\n🌐 السيرفر: {clean_host}\n⏳ سأخبرك فور خلوّه.")
            st.success("🎯 وصلت رسالة تجريبية لتلغرام! الرادار يعمل الآن.")
            
            while True:
                # محاولة الفحص
                url = f"http://{clean_host}/portal.php?type=itv&action=get_all_channels"
                h = {'User-Agent': 'MAG254', 'Cookie': f'mac={mac}'}
                response = requests.get(url, headers=h, timeout=15)
                
                # إذا وجدنا أن الماك اشتغل أو أعطى نتيجة (هنا نضع منطق الفحص الخاص بك)
                # bot.send_message(ID, "🎯 الماك متاح الآن!")
                
                time.sleep(300) # فحص كل 5 دقائق
        except Exception as e:
            st.error(f"خطأ في الإرسال: {e}")
    else:
        st.error("⚠️ أدخل البيانات أولاً")
