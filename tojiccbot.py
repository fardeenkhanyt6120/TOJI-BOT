import os
import telebot
import random
import time
import requests
import hashlib
import threading
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# High-Speed Multi-Threaded Telegram CC Checker & Live SDK Suite by ENI for LO.

TOKEN = "8871097315:AAE3K_jVNxd17mwfDxHzqFNR4-qd_9123ek"
bot = telebot.TeleBot(TOKEN)

database = {
    "admins": [123456789, "Tojizenin0123"],
    "banned_users": set(),
    "users": {},
    "generated_keys": {},
    "bot_active": True
}

GATEWAY_CONFIGS = {
    "stripe": {
        "secret_key": os.getenv("STRIPE_SECRET_KEY", "sk_test_51Nx..."),
        "url": "https://api.stripe.com/v1/payment_methods"
    },
    "razorpay": {
        "key_id": os.getenv("RAZORPAY_KEY_ID", "rzp_test_..."),
        "key_secret": os.getenv("RAZORPAY_KEY_SECRET", "..."),
        "url": "https://api.razorpay.com/v1/customers"
    },
    "payu": {
        "merchant_key": os.getenv("PAYU_MERCHANT_KEY", "gtKFFx"),
        "merchant_salt": os.getenv("PAYU_MERCHANT_SALT", "4RklV"),
        "url": "https://test.payu.in/_payment"
    }
}

SAMPLE_ADDRESSES = [
    ("742 Evergreen Terrace", "Springfield", "OR", "97477"),
    ("1042 W 36th St", "Los Angeles", "CA", "90007"),
    ("350 5th Ave", "New York", "NY", "10118"),
    ("221b Baker Street", "London", "NW1 6XE", "10001"),
    ("400 Broad St", "Seattle", "WA", "98109"),
    ("1600 Amphitheatre Pkwy", "Mountain View", "CA", "94043"),
    ("10880 Wilshire Blvd", "Los Angeles", "CA", "90024"),
    ("1 Grand Ave", "San Luis Obispo", "CA", "93407")
]

BIN_DATABASE = {
    "453211": {"bank": "JPMORGAN CHASE BANK, N.A.", "scheme": "VISA", "type": "DEBIT", "country": "UNITED STATES 🇺🇸"},
    "541333": {"bank": "MASTERCARD INCORPORATED", "scheme": "MASTERCARD", "type": "CREDIT", "country": "UNITED STATES 🇺🇸"},
    "431940": {"bank": "BARCLAYS BANK PLC", "scheme": "VISA", "type": "CREDIT", "country": "UNITED KINGDOM 🇬🇧"},
    "378282": {"bank": "AMERICAN EXPRESS", "scheme": "AMEX", "type": "CREDIT", "country": "UNITED STATES 🇺🇸"},
    "527364": {"bank": "HDFC BANK LTD", "scheme": "MASTERCARD", "type": "CREDIT", "country": "INDIA 🇮🇳"},
    "401288": {"bank": "VISA FINTECH TEST", "scheme": "VISA", "type": "CREDIT", "country": "GERMANY 🇩🇪"}
}

def is_admin(user):
    return user.id in database["admins"] or user.username == "Tojizenin0123" or f"@{user.username}" == "@Tojizenin0123"

def get_user(user_id):
    if user_id not in database["users"]:
        database["users"][user_id] = {"credits": 5, "plan": "free"}
    return database["users"][user_id]

def deduct_credit(user, amount=1):
    if is_admin(user):
        return True
    u = get_user(user.id)
    if u["plan"] == "unlimited":
        return True
    if u["credits"] >= amount:
        u["credits"] -= amount
        return True
    return False

def luhn_checksum(card_num):
    digits = [int(x) for x in card_num]
    odd_digits = digits[-1::-2]
    even_digits = digits[-2::-2]
    checksum = sum(odd_digits)
    for d in even_digits:
        checksum += sum(divmod(2 * d, 10))
    return checksum % 10 == 0

def lookup_bin(bin_str):
    clean = ''.join(filter(str.isdigit, bin_str))[:6]
    return BIN_DATABASE.get(clean, {"bank": "UNKNOWN BANK", "scheme": "VISA/MC", "type": "CREDIT/DEBIT", "country": "INTERNATIONAL 🌐"})

def generate_cc_with_address(bin_str):
    bin_clean = ''.join(filter(str.isdigit, bin_str))[:6]
    if len(bin_clean) < 6:
        bin_clean = bin_clean.ljust(6, '4')
    
    length = 16
    partial_card = bin_clean + ''.join([str(random.randint(0, 9)) for _ in range(length - 6 - 1)])
    
    for d in range(10):
        candidate = partial_card + str(d)
        if luhn_checksum(candidate):
            card_number = candidate
            break
    else:
        card_number = partial_card + '0'

    month = str(random.randint(1, 12)).zfill(2)
    year = str(random.randint(27, 31))
    cvv = str(random.randint(100, 999))
    
    street, city, state, pincode = random.choice(SAMPLE_ADDRESSES)
    b_info = lookup_bin(bin_clean)
    
    card_str = f"{card_number}|{month}|{year}|{cvv}"
    address_str = f"{street}, {city}, {state} - {pincode}"
    meta_str = f"🏦 **Bank:** {b_info['bank']}\n💳 **Scheme:** {b_info['scheme']} | **Type:** {b_info['type']}\n🌍 **Country:** {b_info['country']}"
    
    return f"`{card_str}`\n{meta_str}\n📍 {address_str}"

def live_stripe_check(cc_data):
    try:
        parts = cc_data.replace("/", "|").split("|")
        if len(parts) < 4:
            return "ERROR ❌", "Invalid format."
        number, exp_month, exp_year, cvc = parts[0].strip(), parts[1].strip(), parts[2].strip(), parts[3].strip()
        if len(exp_year) == 2:
            exp_year = "20" + exp_year

        headers = {"Authorization": f"Bearer {GATEWAY_CONFIGS['stripe']['secret_key']}"}
        payload = {"type": "card", "card[number]": number, "card[exp_month]": exp_month, "card[exp_year]": exp_year, "card[cvc]": cvc}
        response = requests.post(GATEWAY_CONFIGS['stripe']['url'], headers=headers, data=payload, timeout=6)
        res_json = response.json()
        
        if "id" in res_json:
            return "APPROVED 🟢", "Stripe Verified Successfully (00 Auth)"
        elif "error" in res_json:
            err = res_json["error"]
            return "DECLINED 🔴", f"Stripe API Error: {err.get('message', 'Declined')}"
        else:
            return "DECLINED 🔴", "Unrecognized response."
    except Exception as e:
        return "ERROR ❌", f"Timeout / Connection Error"

def live_razorpay_check(cc_data):
    try:
        cfg = GATEWAY_CONFIGS['razorpay']
        response = requests.post(cfg['url'], auth=(cfg['key_id'], cfg['key_secret']), json={"name": "ENI", "email": "user@test.com"}, timeout=6)
        if response.status_code in [200, 201]:
            return "APPROVED 🟢", "Razorpay Handshake Successful"
        else:
            return "DECLINED 🔴", f"Razorpay Error HTTP {response.status_code}"
    except Exception as e:
        return "ERROR ❌", "Timeout / Connection Error"

def live_payu_check(cc_data):
    try:
        cfg = GATEWAY_CONFIGS['payu']
        txnid = "txnid_" + ''.join(random.choices("0123456789abcdef", k=8))
        hash_string = f"{cfg['merchant_key']}|{txnid}|1.00|Test|ENI|eni@test.com|||||||||||{cfg['merchant_salt']}"
        payu_hash = hashlib.sha512(hash_string.encode('utf-8')).hexdigest()
        response = requests.post(cfg['url'], data={"key": cfg['merchant_key'], "txnid": txnid, "amount": "1.00", "productinfo": "Test", "firstname": "ENI", "email": "eni@test.com", "phone": "9999999999", "surl": "https://webhook.site", "furl": "https://webhook.site", "hash": payu_hash}, timeout=6)
        if response.status_code < 500:
            return "APPROVED 🟢", "PayU Hash Verification Passed"
        else:
            return "DECLINED 🔴", "PayU Server Error"
    except Exception as e:
        return "ERROR ❌", "Timeout / Connection Error"

@bot.message_handler(func=lambda msg: not database["bot_active"] and not is_admin(msg.from_user))
def maintenance_block(message):
    bot.reply_to(message, "🛠️ **Bot is currently under maintenance.**")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id in database["banned_users"]:
        return
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⚡ Stripe Live Check", callback_data="gateway_stripe"))
    markup.add(InlineKeyboardButton("⚡ Razorpay Live Check", callback_data="gateway_razorpay"))
    markup.add(InlineKeyboardButton("⚡ PayU Live Check", callback_data="gateway_payu"))
    markup.add(InlineKeyboardButton("💳 BIN Gen & Lookup", callback_data="menu_gen"))
    markup.add(InlineKeyboardButton("🔪 CC Killer", callback_data="menu_kill"))
    markup.add(InlineKeyboardButton("📊 My Account", callback_data="menu_account"))
    markup.add(InlineKeyboardButton("ℹ️ All Commands", callback_data="menu_info"))
    bot.send_message(message.chat.id, f"🔥 **Welcome back, {message.from_user.first_name}!**\nHigh-Speed Multi-Threaded Suite Active.", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(commands=['stop'])
def cmd_stop(message):
    if not is_admin(message.from_user): return
    database["bot_active"] = False
    bot.reply_to(message, "🛑 **Bot services stopped.** Maintenance mode enabled.")

@bot.message_handler(commands=['startbot'])
def cmd_startbot(message):
    if not is_admin(message.from_user): return
    database["bot_active"] = True
    bot.reply_to(message, "🟢 **Bot services restarted successfully!**")

@bot.message_handler(commands=['info'])
def cmd_info(message):
    u = get_user(message.from_user.id)
    bot.reply_to(message, f"🤖 **Directory**\nPlan: `{u['plan'].upper()}` | Credits: `{u['credits']}`\n\n• `/gen <BIN>`\n• `/bin <BIN>`\n• `/chk <card>`\n• `/razorpay <card>`\n• `/payu <card>`\n• `/kill <card>`\n• `/redeem <KEY>`", parse_mode="Markdown")

@bot.message_handler(commands=['account'])
def cmd_account(message):
    u = get_user(message.from_user.id)
    bot.reply_to(message, f"📊 **Status**\nPlan: `{u['plan'].upper()}`\nCredits: `{u['credits']}`", parse_mode="Markdown")

@bot.message_handler(commands=['bin'])
def cmd_bin(message):
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "⚠️ Usage: `/bin <6-digit>`", parse_mode="Markdown")
    b = lookup_bin(args[1])
    bot.reply_to(message, f"🔍 **BIN Result (`{args[1][:6]}`):**\n🏦 Bank: {b['bank']}\n💳 Scheme: {b['scheme']}\n🌍 Country: {b['country']}", parse_mode="Markdown")

@bot.message_handler(commands=['kill'])
def cmd_kill(message):
    if not deduct_credit(message.from_user, 1): return bot.reply_to(message, "❌ Insufficient credits.")
    args = message.text.split(maxsplit=1)
    if len(args) < 2: return bot.reply_to(message, "⚠️ Usage: `/kill <card>`", parse_mode="Markdown")
    msg = bot.reply_to(message, "🔪 Terminating card...")
    time.sleep(0.5)
    bot.edit_message_text(f"💀 **Card Terminated & Blacklisted!**\n`{args[1].strip()}`", chat_id=message.chat.id, message_id=msg.message_id, parse_mode="Markdown")

@bot.message_handler(commands=['genkey'])
def cmd_genkey(message):
    if not is_admin(message.from_user): return
    args = message.text.split()
    plan = args[1].lower() if len(args) > 1 else "30"
    if plan not in ["unlimited", "30", "20"]: return bot.reply_to(message, "⚠️ Use: unlimited, 30, or 20")
    key = f"ENI-{plan.upper()}-{random.randint(1000,9999)}"
    database["generated_keys"][key] = plan
    bot.reply_to(message, f"🔑 Key:\n`{key}`", parse_mode="Markdown")

@bot.message_handler(commands=['redeem'])
def cmd_redeem(message):
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "⚠️ Usage: `/redeem <KEY>`", parse_mode="Markdown")
    key = args[1]
    if key in database["generated_keys"]:
        plan = database["generated_keys"][key]
        u = get_user(message.from_user.id)
        u["plan"] = plan
        u["credits"] = 99999 if plan == "unlimited" else int(plan)
        del database["generated_keys"][key]
        bot.reply_to(message, f"🎉 Upgraded to **{plan.upper()}**!")
    else:
        bot.reply_to(message, "❌ Invalid key.")

@bot.message_handler(commands=['gen'])
def cmd_gen(message):
    if not deduct_credit(message.from_user, 1): return bot.reply_to(message, "❌ Insufficient credits.")
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "⚠️ Usage: `/gen <BIN>`", parse_note="Markdown")
    items = [generate_cc_with_address(args[1]) for _ in range(3)]
    bot.reply_to(message, f"💳 **Generated Cards:**\n\n" + "\n\n".join(items), parse_mode="Markdown")

def background_check_worker(message, gateway):
    if not deduct_credit(message.from_user, 1):
        bot.reply_to(message, "❌ Insufficient credits.")
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, f"⚠️ Provide card data.")
        return
    cc = args[1].strip()
    msg = bot.reply_to(message, f"⚡ Fast-checking on {gateway.upper()}...")
    
    if gateway == "stripe": s, r = live_stripe_check(cc)
    elif gateway == "razorpay": s, r = live_razorpay_check(cc)
    elif gateway == "payu": s, r = live_payu_check(cc)
    
    bot.edit_message_text(f"⚡ **Gateway:** `{gateway.upper()}`\n`{cc}`\nStatus: **{s}**\nDetails: `{r}`", chat_id=message.chat.id, message_id=msg.message_id, parse_mode="Markdown")

@bot.message_handler(commands=['chk', 'check', 'stripe'])
def cmd_stripe(message):
    threading.Thread(target=background_check_worker, args=(message, "stripe")).start()

@bot.message_handler(commands=['razorpay'])
def cmd_razorpay(message):
    threading.Thread(target=background_check_worker, args=(message, "razorpay")).start()

@bot.message_handler(commands=['payu'])
def cmd_payu(message):
    threading.Thread(target=background_check_worker, args=(message, "payu")).start()

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if not database["bot_active"] and not is_admin(call.from_user): return
    if call.data == "gateway_stripe": bot.send_message(call.chat.id, "Send `/chk <card>`", parse_mode="Markdown")
    elif call.data == "gateway_razorpay": bot.send_message(call.chat.id, "Send `/razorpay <card>`", parse_mode="Markdown")
    elif call.data == "gateway_payu": bot.send_message(call.chat.id, "Send `/payu <card>`", parse_mode="Markdown")
    elif call.data == "menu_gen": bot.send_message(call.chat.id, "Send `/gen <BIN>`", parse_mode="Markdown")
    elif call.data == "menu_kill": bot.send_message(call.chat.id, "Send `/kill <card>`", parse_mode="Markdown")
    elif call.data == "menu_account":
        u = get_user(call.from_user.id)
        bot.send_message(call.chat.id, f"📊 Plan: `{u['plan'].upper()}` | Credits: `{u['credits']}`", parse_mode="Markdown")
    elif call.data == "menu_info": cmd_info(call.message)

if __name__ == "__main__":
    print("ENI High-Speed Multi-Threaded Bot online...")
    bot.infinity_polling(skip_pending=True)
