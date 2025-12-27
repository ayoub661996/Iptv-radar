import streamlit as st
import requests
import time
import telebot
import random
import re

# بياناتك الثابتة
TOKEN = "8485193296:AAHpW18fpS74B3oaUGqNCYZjbodRPa76uLE"
ID = 7638628794
bot = telebot.TeleBot(TOKEN)

# قائمة القنوات المفضلة الدقيقة
FAV_CHANNELS = [
    "BEIN AFRICA CUP 2025",
    "IARI BEIN SPORTS 8K",
    "IARI BEIN SPORTS 4K"
]

st.set_page_config(page_title="رادار الشبح المتكامل", page_icon="📡")
st.title("📡 رادار الماك (الفحص الشامل + الحالة)")

input_data = st.text_area("أدخل البيانات (الرابط والماك)")

if st.button("🚀 تشغيل الرادار الشامل"):
    if input_data:
        parts = input_data.split()
        host = next((p for p in parts if "." in p), None)
        mac = next((p for p in parts if ":" in p), None)

        if host and mac:
            clean_host = host.replace("http://", "").replace("https://", "").strip("/")
            st.info("🕵️ جاري فحص حالة السيرفر والماك...")
            
            def perform_full_check():
                headers = {'User-Agent': 'MAG254', 'Cookie': f'mac={mac}'}
                try:
                    # 1. فحص هل السيرفر يعمل أصلاً (Server Status)
                    base_url = f"http://{clean_host}/portal.php"
                    start_time = time.time()
                    test_res = requests.get(base_url, headers=headers, timeout=10)
                    latency_ms = (time.time() - start_time) * 1000
                    
                    if test_res.status_code != 200:
                        return "❌ متوقف أو محظور", "غير معروف", "متقطع", [], False

                    server_status = "✅ يعمل (متصل)"
                    
                    # 2. فحص المتصلين والاستقرار
                    url_prof = f"{base_url}?type=stb&action=get_profile&force_stb=1"
                    r_prof = requests.get(url_prof, headers=headers, timeout=10)
                    
                    stability = "قوي (لا يقطع) ✅" if latency_ms < 1000 else "متقطع ⚠️"
                    
                    active = "0"
                    if r_prof.status_code == 200:
                        match = re.search(r'"active_cons"\s*:\s*"(\d+)"', r_prof.text)
                        active = match.group(1) if match else "0"
                    
                    # 3. فحص القنوات المفضلة
                    url_ch = f"{base_url}?type=itv&action=get_all_channels"
                    r_ch = requests.get(url_ch, headers=headers, timeout=10)
                    found = [f"✅ {c}" if c.upper() in r_ch.text.upper() else f"❌ {c}" for c in FAV_CHANNELS]
                    
                    return server_status, active, stability, found, True
                except:
                    return "❌ متوقف (لا يوجد استجابة)", "غير معروف", "متقطع", [], False

            # الفحص الأول
            s_status, active, stab, channels, success = perform_full_check()
            
            report = (
                f"📡 **تقرير الرادار الشامل**\n\n"
                f"🌐 السيرفر: {clean_host}\n"
                f"📶 حالة الخدمة: **{s_status}**\n"
                f"🖥️ الماك: `{mac}`\n"
                f"👥 المتصلون: `{active}`\n"
                f"📊 الاستقرار: **{stab}**\n\n"
                f"📺 **القنوات المطلوبة:**\n" + "\n".join(channels)
            )
            
            bot.send_message(ID, report, parse_mode="Markdown")
            st.success(f"🎯 تم الفحص! حالة السيرفر: {s_status}")

            if success and active != "0":
                st.info("🔄 الرادار سيبقى يعمل لتنبيهك فور خلو الماك...")
                placeholder = st.empty()
                while True:
                    s_status, active, stab, _ = perform_full_check()
                    placeholder.write(f"⏱️ تحديث: {time.strftime('%H:%M:%S')} | الحالة: {s_status} | المتصلون: {active}")
                    if active == "0" and s_status.startswith("✅"):
                        bot.send_message(ID, f"🔔 **تنبيه: الماك أصبح متاحاً الآن!**\nالسيرفر: {clean_host}\nالماك: `{mac}`\nالاستقرار: {stab}")
                        break
                    time.sleep(300)
        else:
            st.error("تأكد من الرابط والماك")
