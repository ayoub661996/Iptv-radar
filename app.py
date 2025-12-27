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

# قائمة القنوات المفضلة (بحث ذكي)
CHANNELS_KEYS = {
    "BEIN AFRICA CUP 2025": ["AFRICA", "2025"],
    "IARI BEIN SPORTS 8K": ["8K", "IARI"],
    "IARI BEIN SPORTS 4K": ["4K", "IARI"]
}

st.set_page_config(page_title="رادار الشبح المتكامل", page_icon="📡")
st.title("📡 رادار الماك (الحالة + المتصلين + القنوات)")

input_data = st.text_area("أدخل الرابط والماك (نسخ ولصق عشوائي)")

if st.button("🚀 بدء الفحص والمراقبة"):
    if input_data:
        # استخراج الرابط والماك بذكاء
        parts = input_data.replace(',', ' ').split()
        host = next((p for p in parts if "." in p and ":" not in p or p.startswith("http")), None)
        mac = next((p for p in parts if ":" in p and len(p) >= 14), None)

        if host and mac:
            clean_host = host.replace("http://", "").replace("https://", "").strip("/")
            st.info(f"🔎 جاري فحص السيرفر والماك: {mac}")
            
            def perform_full_check():
                headers = {'User-Agent': 'MAG254', 'Cookie': f'mac={mac}'}
                try:
                    base_url = f"http://{clean_host}/portal.php"
                    start_time = time.time()
                    
                    # 1. فحص هل السيرفر يشتغل أو معطل
                    try:
                        test_res = requests.get(base_url, headers=headers, timeout=10)
                        server_status = "✅ يشتغل (متصل)" if test_res.status_code == 200 else "❌ معطل أو محظور"
                    except:
                        server_status = "❌ معطل (لا توجد استجابة)"
                    
                    latency_ms = (time.time() - start_time) * 1000
                    stability = "قوي (لا يقطع) ✅" if latency_ms < 1000 else "متقطع ⚠️"
                    
                    # 2. فحص المتصلين
                    url_prof = f"{base_url}?type=stb&action=get_profile&force_stb=1"
                    r_prof = requests.get(url_prof, headers=headers, timeout=10)
                    active = "0"
                    if r_prof.status_code == 200:
                        match = re.search(r'"active_cons"\s*:\s*"(\d+)"', r_prof.text)
                        active = match.group(1) if match else "0"
                    
                    # 3. فحص القنوات (البحث الذكي)
                    url_ch = f"{base_url}?type=itv&action=get_all_channels"
                    r_ch = requests.get(url_ch, headers=headers, timeout=10)
                    ch_content = r_ch.text.upper()
                    
                    found_status = []
                    for name, keys in CHANNELS_KEYS.items():
                        if all(k.upper() in ch_content for k in keys):
                            found_status.append(f"✅ {name}")
                        else:
                            found_status.append(f"❌ {name}")
                    
                    return server_status, active, stability, found_status, True
                except:
                    return "❌ معطل", "غير معروف", "متقطع", [], False

            # تنفيذ الفحص الأول
            s_status, active, stab, channels, success = perform_full_check()
            
            # تقرير شامل يذكر كل شيء بوضوح
            report = (
                f"📡 **تقرير الرادار المتكامل**\n\n"
                f"🖥️ **Mac Address:** `{mac}`\n"
                f"🌐 السيرفر: {clean_host}\n"
                f"📶 حالة السيرفر: **{s_status}**\n"
                f"👥 المتصلون حالياً: `{active}`\n"
                f"📊 الاستقرار: **{stab}**\n\n"
                f"📺 **القنوات المفضلة:**\n" + "\n".join(channels)
            )
            
            bot.send_message(ID, report, parse_mode="Markdown")
            st.success(f"🎯 تم إرسال التقرير! حالة السيرفر: {s_status}")
            
            # الرادار التلقائي في الخلفية
            if success and active != "0":
                st.warning("🔄 الماك مشغول.. الرادار يراقب الآن وسينبهك فور خلوه.")
                placeholder = st.empty()
                while True:
                    curr_status, curr_active, curr_stab, _ = perform_full_check()
                    placeholder.write(f"⏱️ تحديث الرادار: {time.strftime('%H:%M:%S')} | المتصلون: {curr_active}")
                    if curr_active == "0" and "✅" in curr_status:
                        bot.send_message(ID, f"🔔 **تنبيه: الماك أصبح متاحاً الآن!**\n🖥️ الماك: `{mac}`\n📶 السيرفر: {clean_host}\n📊 الجودة: {curr_stab}")
                        break
                    time.sleep(300) # فحص كل 5 دقائق
        else:
            st.error("يرجى التأكد من إدخال الرابط والماك بشكل صحيح.")
