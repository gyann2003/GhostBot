import telebot
from telebot import types
import time
import re
import os
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from flask import Flask
from threading import Thread

# --- DUMMY SERVER (Render ko bewakoof banane ke liye) ---
app = Flask(__name__)
@app.route('/')
def home():
    return "Ghost Bot is ALIVE 24/7!"
def run_server():
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
Thread(target=run_server, daemon=True).start()

# --- ORIGINAL GHOST TRACKER CODE ---
API_TOKEN = '8704791692:AAGJ1orzC-OZYwfo9yTidjVXDrcyiuLwg_U'
bot = telebot.TeleBot(API_TOKEN)
tracker_status = {}

print("=======================================================")
print("👻 GHOST TRACKER - CLOUD RENDER MODE ⚡")
print("=======================================================")

LOCATIONS = {
    "Ganjam - Buguda": {"dist_id": "11", "off_id": "62"},
    "Ganjam - Polasara": {"dist_id": "11", "off_id": "185"},
}

def get_main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2) 
    for loc in LOCATIONS.keys():
        markup.add(types.KeyboardButton(f"📍 Track: {loc}"))
    markup.add(types.KeyboardButton("🛑 Stop Tracker"))
    return markup

@bot.message_handler(commands=['start'])
def send_welcome(message):
    bot.reply_to(message, "⚡ **CLOUD GHOST READY!**\n\nNiche se apna Office chunein 👇", reply_markup=get_main_menu(), parse_mode='Markdown')

@bot.message_handler(func=lambda message: message.text == '🛑 Stop Tracker')
def stop_process(message):
    tracker_status[message.chat.id] = False
    bot.send_message(message.chat.id, "🚫 Tracker Stop Kar Diya Gaya Hai.", reply_markup=get_main_menu())

@bot.message_handler(func=lambda message: message.text.startswith('📍 Track:'))
def start_ghost_tracking(message):
    tracker_status[message.chat.id] = False 
    time.sleep(1) 

    loc_name = message.text.replace('📍 Track: ', '')
    if loc_name not in LOCATIONS:
        return

    dist_id = LOCATIONS[loc_name]["dist_id"]
    off_id = LOCATIONS[loc_name]["off_id"]
    tracker_status[message.chat.id] = True
    first_scan = True 

    bot.send_message(message.chat.id, f"⚡ **CLOUD MODE ON:** {loc_name}\n\n🕵️‍♂️ 24/7 Tracking shuru...", parse_mode='Markdown', reply_markup=types.ReplyKeyboardMarkup(resize_keyboard=True).add("🛑 Stop Tracker"))

    url = "https://www.igrodisha.gov.in/SlotBookingAllNew.aspx"
    
    while tracker_status.get(message.chat.id, True):
        driver = None
        try:
            options = Options()
            options.add_argument("--headless=new") 
            options.add_argument("--disable-gpu")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage") # Render ke 512MB RAM ke liye zaroori
            options.add_argument("--log-level=3") 
            options.page_load_strategy = 'eager' 
            prefs = {"profile.managed_default_content_settings.images": 2, "profile.managed_default_content_settings.stylesheets": 2}
            options.add_experimental_option("prefs", prefs)

            driver = webdriver.Chrome(options=options)
            driver.set_script_timeout(10)
            driver.get(url)
            time.sleep(1) 

            Select(driver.find_element(By.ID, "ddlDistName")).select_by_value(dist_id)
            time.sleep(1) 

            Select(driver.find_element(By.ID, "ddlRegOff")).select_by_value(off_id)
            time.sleep(1.5) 

            start_el = driver.find_element(By.ID, "hdfStartDt")
            end_el = driver.find_element(By.ID, "hdfEndDt")
            holidays_raw = driver.find_element(By.ID, "hdfHoliDayDays").get_attribute("value")

            start_dt_str = start_el.get_attribute("value")
            end_dt_str = end_el.get_attribute("value")

            valid_dates = []
            if start_dt_str and end_dt_str:
                holidays_list = [h.strip("'") for h in holidays_raw.split(',')] if holidays_raw else []
                start_dt = datetime.strptime(start_dt_str, "%d/%b/%Y")
                end_dt = datetime.strptime(end_dt_str, "%d/%b/%Y")
                curr = start_dt
                while curr <= end_dt:
                    if curr.strftime("%d/%b/%Y") not in holidays_list:
                        valid_dates.append(curr.strftime("%d-%b-%Y")) 
                    curr += timedelta(days=1)
            else:
                curr = datetime.now()
                for _ in range(10):
                    if curr.weekday() != 6:
                        valid_dates.append(curr.strftime("%d-%b-%Y"))
                    curr += timedelta(days=1)

            total_slots_found = 0

            for date_str in valid_dates:
                if not tracker_status.get(message.chat.id, True):
                    break

                ajax_script = """
                    var dateStr = arguments[0];
                    var callback = arguments[1];
                    var fd = new URLSearchParams(new FormData(document.forms[0]));
                    fd.set('txtId', dateStr);
                    fd.set('btnView', 'View Available Slots');
                    fd.set('__EVENTTARGET', '');
                    fd.set('__EVENTARGUMENT', '');
                    fd.set('hdfCheck1', 'N');
                    fd.set('hdfCheck2', 'N');

                    fetch(window.location.href, { method: 'POST', body: fd.toString(), headers: {'Content-Type': 'application/x-www-form-urlencoded'} })
                    .then(r => r.text()).then(html => callback(html)).catch(e => callback('ERROR'));
                """

                page_source = driver.execute_async_script(ajax_script, date_str)

                if page_source == 'ERROR':
                    continue

                slots = re.findall(r'Available[\s\S]{0,15}?\(\s*(\d+)\s*\)', page_source, re.IGNORECASE)
                
                if slots:
                    slots_qty = sum(int(s) for s in slots)
                    if slots_qty > 0:
                        total_slots_found += slots_qty
                        live_alert = f"🚨 **LIVE SLOT MILA!** 🚨\n📍 **Office:** {loc_name}\n✅ **Date:** `{date_str}`\n🔥 **Slots:** `{slots_qty}`"
                        bot.send_message(message.chat.id, live_alert, parse_mode='Markdown')

            if total_slots_found > 0:
                bot.send_message(message.chat.id, f"⚡ *Saari dates check ho gayi! Tracker ruk gaya hai.*", reply_markup=get_main_menu(), parse_mode='Markdown')
                tracker_status[message.chat.id] = False
            else:
                if first_scan:
                    bot.send_message(message.chat.id, f"🔄 **Pehla Scan Pura Hua!** (0 Slots).\nMain cloud par lagatar check kar raha hoon! ⚡", parse_mode='Markdown')
                    first_scan = False

            if driver:
                driver.quit()
            time.sleep(2) 

        except Exception as e:
            if driver:
                try: driver.quit()
                except: pass
            time.sleep(3) 

bot.polling(none_stop=True)
