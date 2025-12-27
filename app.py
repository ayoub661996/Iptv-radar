import streamlit as st
import requests
import time
import telebot
import random

# بياناتك الثابتة
TOKEN = "8485193296:AAHpW18fpS74B3oaUGqNCYZjbodRPa76uLE"
ID = 7638628794
bot = telebot.TeleBot(TOKEN)

# قائمة القنوات المفضلة
FAVORITE_CHANNELS = ["bein sport Arabic", "bein africa cup 2025"]

# قائمة بصمات أجهزة MAG ومتصفحات مختلفة للتمويه (التخفي)
USER_AGENTS = [
    "Mozilla/5.0 (QtEmbedded; U; Linux; C) AppleWebKit/533.3 (KHTML, like Gecko) MAG200 stbapp ver: 2 rev: 250 Safari/533.3",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "MAG254/2.18 (Linux; GNU) WebKit/533.3",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Mobile/15E148 Safari/604.1"
]

st.set_page_config(page_title="رادار الماك الشبح", page_icon="🕵️")
st.title("🕵️ رادار الماك السحابي (Stealth Mode)")

st.subheader("📝 إدخال البيانات الذكي")
input_data = st.text_area("أدخل الرابط والماك بأي شكل عشوائي (نسخ/لصق)", 
                         placeholder="مثال:\nhttp://server.com\n00:1A:79:XX:XX:XX")

if st.button("🏁 بدء الفحص المتخفي"):
    if input_data:
        # استخراج الرابط والماك
        lines = input_data.split()
        host = next((l for l in lines if "." in l), None)
        mac = next((l for l in lines if ":" in l), None)

        if host and mac:
            clean_host = host.replace("http://", "").replace("https://", "").strip("/")
            st.success("🕵️ تم تفعيل نظام التخفي.. جاري الفحص بصمت.")
            
            try:
                # اختيار بصمة عشوائية لكل طلب لعدم كشف البوت
                selected_ua = random.choice(USER_AGENTS)
                
                # إعداد الطلب المموه
                url = f"http://{clean_host}/portal.php?type=itv&action=get_all_channels"
                headers = {
                    'User-Agent': selected_ua,
                    'Cookie': f'mac={mac}',
                    'Accept-Language': 'en-US,en;q=0.9',
                    'Referer': f'http://{clean_host}/c/'
                }

                start_time = time.time()
                # إضافة تأخير عشوائي بسيط لتبدو كإنسان
                time.sleep(random.uniform(1.5, 3.0)) 
                
                response = requests.get(url, headers=headers, timeout=15)
                end_time = time.time()
                
                # فحص الحالة والقوة
                status = "🟢 يعمل" if response.status_code == 200 else "🔴 متوقف/محظور"
                latency = round((end_time - start_time) * 1000, 2)
                stability = "💎 ثابت" if latency < 600 else "⚠️ تقطيع محتمل"
                
                # فحص القنوات
                found_channels = []
                content = response.text.lower()
                for ch in FAVORITE_CHANNELS:
                    found_channels.append(f"✅ {ch}" if ch.lower() in content else f"❌ {ch}")

                # إرسال التقرير الشامل
                report = (
                    f"🕵️ **تقرير الرادار المتخفي**\n\n"
                    f"🖥️ الماك: `{mac}`\n"
                    f"🌐 السيرفر: {clean_host}\n"
                    f"⚡ الحالة: {status}\n"
                    f"⏱️ الاستجابة: {latency}ms\n"
                    f"🛡️ الاستقرار: {stability}\n"
                    f"👤 البصمة المستخدمة: `MAG-Stealth`\n\n"
                    f"📺 **القنوات المفضلة:**\n" + "\n".join(found_channels)
                )
                
                bot.send_message(ID, report, parse_mode="Markdown")
                st.info("✅ انتهى الفحص وأُرسل التقرير لتلغرام.")
                
            except Exception as e:
                st.error(f"❌ فشل الفحص: {e}")
        else:
            st.warning("⚠️ يرجى التأكد من وجود الرابط والماك.")
    else:
        st.error("⚠️ الصندوق فارغ!")
