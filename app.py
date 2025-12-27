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

# القنوات المفضلة
FAVORITE_CHANNELS = ["bein sport Arabic", "bein africa cup 2025"]

# بصمات التخفي
AGENTS = ["MAG254/2.18 (Linux; GNU) WebKit/533.3", "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) Safari/604.1"]

st.set_page_config(page_title="رادار الماك الاحترافي", page_icon="📡")
st.title("📡 رادار الماك (المتصلين والاستقرار)")

input_data = st.text_area("أدخل الرابط والماك (نسخ ولصق عشوائي)")

if st.button("🚀 بدء الفحص الشامل"):
    if input_data:
        parts = input_data.split()
        host = next((p for p in parts if "." in p), None)
        mac = next((p for p in parts if ":" in p), None)

        if host and mac:
            clean_host = host.replace("http://", "").replace("https://", "").strip("/")
            st.info("🕵️ نظام التخفي نشط.. جاري تحليل المتصلين وقوة الإشارة.")
            
            try:
                # اختيار بصمة عشوائية وتأخير بسيط للتخفي
                headers = {'User-Agent': random.choice(AGENTS), 'Cookie': f'mac={mac}'}
                time.sleep(random.uniform(1, 2))
                
                # 1. فحص المتصلين (Profile)
                url_prof = f"http://{clean_host}/portal.php?type=stb&action=get_profile&force_stb=1"
                start_time = time.time()
                res_prof = requests.get(url_prof, headers=headers, timeout=15)
                end_time = time.time()
                
                # حساب سرعة الرد (الاستقرار)
                latency = round((end_time - start_time) * 1000)
                
                # استخراج عدد المتصلين
                active_cons = "0"
                if res_prof.status_code == 200:
                    match = re.search(r'"active_cons"\s*:\s*"(\d+)"', res_prof.text)
                    active_cons = match.group(1) if match else "0"

                # 2. تقييم الاستقرار (حسب سرعة الرد)
                if latency < 800:
                    stability = "🚀 قوي (ثابت جداً)"
                elif 800 <= latency < 2000:
                    stability = "🟡 متوسط (قد يقطع)"
                else:
                    stability = "🐌 ضعيف (تقطيع مستمر)"

                # 3. تقييم الحالة النهائية (متصلين + استقرار)
                if active_cons == "0" and latency < 1000:
                    final_verdict = "💎 ماك ذهبي (خالٍ وقوي)"
                elif active_cons != "0":
                    final_verdict = f"⚠️ مشغول حالياً ({active_cons} متصل)"
                else:
                    final_verdict = "⚙️ يحتاج تجربة (استجابة بطيئة)"

                # 4. فحص القنوات
                url_ch = f"http://{clean_host}/portal.php?type=itv&action=get_all_channels"
                res_ch = requests.get(url_ch, headers=headers, timeout=15)
                found = []
                for ch in FAVORITE_CHANNELS:
                    found.append(f"✅ {ch}" if ch.lower() in res_ch.text.lower() else f"❌ {ch}")

                # التقرير النهائي المنظم
                report = (
                    f"🕵️ **تقرير الرادار المتخفي**\n\n"
                    f"🖥️ الماك: `{mac}`\n"
                    f"🌐 السيرفر: {clean_host}\n"
                    f"👥 المتصلون الآن: `{active_cons}`\n"
                    f"⏱️ سرعة الرد: `{latency}ms`\n"
                    f"📊 الاستقرار: {stability}\n"
                    f"⚖️ النتيجة: **{final_verdict}**\n\n"
                    f"📺 **القنوات المفضلة:**\n" + "\n".join(found)
                )
                
                bot.send_message(ID, report, parse_mode="Markdown")
                st.success(f"🎯 تم الفحص بنجاح! الاستقرار: {stability}")
                
            except Exception as e:
                st.error(f"❌ خطأ: {e}")
    else:
        st.warning("⚠️ يرجى إدخال البيانات.")

