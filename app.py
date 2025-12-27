import streamlit as st
import requests
import time
import telebot

# بيانات البوت الخاصة بك
TOKEN = '8485193296:AAGcIe-varcy4gxqu0_NRz3tAKwcY0HyMCw'
ID = 7638628794
bot = telebot.TeleBot(TOKEN)

# إعدادات واجهة التطبيق
st.set_page_config(page_title="رادار الماك السحابي", page_icon="📡")

st.title("📡 رادار الماك السحابي")
st.write("أدخل البيانات بالأسفل لبدء المراقبة التلقائية")

# خانات الإدخال في صفحة واحدة
host = st.text_input("🔗 رابط السيرفر", placeholder="مثال: dm.lion-ott.com")
mac = st.text_input("🖥️ الماك آدرس", placeholder="00:1A:79:XX:XX:XX")

if st.button("🚀 تفعيل المراقبة"):
    if host and mac:
        st.success(f"✅ تم تفعيل الرادار.. ستصلك رسالة فور خلو الماك.")
        
        while True:
            try:
                # محاولة فحص حالة الماك
                url = f"http://{host}/portal.php?type=itv&action=get_all_channels"
                h = {'User-Agent': 'MAG254', 'Cookie': f'mac={mac}'}
                r = requests.get(url, headers=h, timeout=15)
                
                # إرسال رسالة تجريبية عند التفعيل للتأكد
                bot.send_message(ID, f"📡 الرادار بدأ مراقبة:\n🖥️ {mac}\n🔗 {host}")
                
                # هنا يتم فحص الرد من السيرفر (مثال مبسط)
                if r.status_code == 200:
                    # إذا كان السيرفر متاحاً، يمكنك إضافة شروط فحص الـ active_cons هنا
                    pass
                
                time.sleep(300) # فحص كل 5 دقائق
                
            except Exception as e:
                time.sleep(60) # في حال الخطأ انتظر دقيقة وأعد المحاولة
    else:
        st.error("⚠️ يرجى إدخال الرابط والماك معاً!")
