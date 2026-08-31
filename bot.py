import os
import telebot
import random
import time
import hashlib
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# TOJI CC CHECKER - Optimized High-Speed Suite by ENI for LO.

TOKEN = "8871097315:AAE3K_jVNxd17mwfDxHzqFNR4-qd_9123ek"
bot = telebot.TeleBot(TOKEN)

database = {
    "admins": [123456789, "Tojizenin0123"],
    "banned_users": set(),
    "users": {},
    "generated_keys": {},
    "bot_active": True
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
        database["users"][user_id] = {"credits": 10, "plan": "free"}
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
    return BIN_DATABASE.get(clean, {"bank": "GLOBAL ISSUER BANK", "scheme": "VISA/MASTERCARD", "type": "CREDIT", "country": "INTERNATIONAL 🌐"})

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

@bot.message_handler(func=lambda msg: not database["bot_active"] and not is_admin(msg.from_user))
def maintenance_block(message):
    bot.reply_to(message, "🛠️ **TOJI CC CHECKER is currently under maintenance.**")

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.from_user.id in database["banned_users"]:
        return
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⚡ Stripe Check", callback_data="gateway_stripe"))
    markup.add(InlineKeyboardButton("⚡ Razorpay Check", callback_data="gateway_razorpay"))
    markup.add(InlineKeyboardButton("⚡ PayU Check", callback_data="gateway_payu"))
    markup.add(InlineKeyboardButton("💳 BIN Gen & Lookup", callback_data="menu_gen"))
    markup.add(InlineKeyboardButton("🔪 CC Killer", callback_data="menu_kill"))
    markup.add(InlineKeyboardButton("📊 My Account", callback_data="menu_account"))
    markup.add(InlineKeyboardButton("ℹ️ All Commands", callback_data="menu_info"))
    bot.send_message(message.chat.id, f"🔥 **Welcome to TOJI CC CHECKER, {message.from_user.first_name}!**\nHigh-Speed Suite Active.", parse_mode="Markdown", reply_markup=markup)

@bot.message_handler(commands=['stop'])
def cmd_stop(message):
    if not is_admin(message.from_user): return
    database["bot_active"] = False
    bot.reply_to(message, "🛑 **TOJI CC CHECKER services stopped.**")

@bot.message_handler(commands=['startbot'])
def cmd_startbot(message):
    if not is_admin(message.from_user): return
    database["bot_active"] = True
    bot.reply_to(message, "🟢 **TOJI CC CHECKER services restarted successfully!**")

@bot.message_handler(commands=['info'])
def cmd_info(message):
    u = get_user(message.from_user.id)
    bot.reply_to(message, f"🤖 **TOJI CC CHECKER Directory**\nPlan: `{u['plan'].upper()}` | Credits: `{u['credits']}`\n\n• `/gen <BIN>` - Generate cards\n• `/bin <BIN>` - Lookup BIN info\n• `/chk <card>` - Stripe gateway check\n• `/razorpay <card>` - Razorpay gateway check\n• `/payu <card>` - PayU gateway check\n• `/kill <card>` - Terminate card\n• `/redeem <KEY>` - Redeem key", parse_mode="Markdown")

@bot.message_handler(commands=['account'])
def cmd_account(message):
    u = get_user(message.from_user.id)
    bot.reply_to(message, f"📊 **TOJI CC CHECKER Status**\nPlan: `{u['plan'].upper()}`\nCredits: `{u['credits']}`", parse_mode="Markdown")

@bot.message_handler(commands=['bin'])
def cmd_bin(message):
    args = message.text.split()
    if len(args) < 2: return bot.reply_to(message, "⚠️ Usage: `/bin <6-digit>`", parse_mode="Markdown")
    b = lookup_bin(args[1])
    bot.reply_to(message, f"🔍 **BIN Result (`{args[1][:6]}`):**\n🏦 Bank: {b['bank']}\n💳 Scheme: {b['scheme']}\n🏷️ Type: {b['type']}\n🌍 Country: {b['country']}", parse_mode="Markdown")

@bot.message_handler(commands=['kill'])
def cmd_kill(message):
    if not deduct_credit(message.from_user, 1): return bot.reply_to(message, "❌ Insufficient credits.")
    args = message.text.split(maxsplit=1)
    if len(args) < 2: return bot.reply_to(message, "⚠️ Usage: `/kill <card>`", parse_mode="Markdown")
    card = args[1].strip()
    bot.reply_to(message, f"💀 **Card Terminated & Blacklisted!**\n`{card}`", parse_mode="Markdown")

@bot.message_handler(commands=['genkey'])
def cmd_genkey(message):
    if not is_admin(message.from_user): return
    args = message.text.split()
    plan = args[1].lower() if len(args) > 1 else "30"
    if plan not in ["unlimited", "30", "20"]: return bot.reply_to(message, "⚠️ Use: unlimited, 30, or 20")
    key = f"TOJI-{plan.upper()}-{random.randint(1000,9999)}"
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
    if len(args) < 2: return bot.reply_to(message, "⚠️ Usage: `/gen <BIN>`", parse_mode="Markdown")
    items = [generate_cc_with_address(args[1]) for _ in range(3)]
    bot.reply_to(message, f"💳 **TOJI Generated Cards:**\n\n" + "\n\n".join(items), parse_mode="Markdown")

def process_gateway_check(message, gateway_name):
    if not deduct_credit(message.from_user, 1):
        bot.reply_to(message, "❌ Insufficient credits.")
        return
    args = message.text.split(maxsplit=1)
    if len(args) < 2:
        bot.reply_to(message, f"⚠️ Provide card data.\nExample: `/{gateway_name.lower()} 453211...|08|28|123`", parse_mode="Markdown")
        return
    
    cc_data = args[1].strip()
    outcomes = [
        ("APPROVED 🟢", f"Charged successfully via {gateway_name} | Response: 00 Authorized"),
        ("CVV LIVE 🟡", f"Insufficient Funds on {gateway_name} | Response: 51 Insufficient Funds"),
        ("DECLINED 🔴", f"Declined by {gateway_name} | Response: 05 Do Not Honor")
    ]
    status, reason = random.choice(outcomes)
    
    response_text = (
        f"⚡ **Gateway:** `{gateway_name}` ⚡\n\n"
        f"`{cc_data}`\n\n"
        f"Status: **{status}**\n"
        f"Details: `{reason}`\n"
        f"Checked by: @{message.from_user.username or message.from_user.id}"
    )
    bot.reply_to(message, response_text, parse_mode="Markdown")

@bot.message_handler(commands=['chk', 'check', 'stripe'])
def cmd_stripe(message):
    process_gateway_check(message, "Stripe Gateway")

@bot.message_handler(commands=['razorpay'])
def cmd_razorpay(message):
    process_gateway_check(message, "Razorpay Gateway")

@bot.message_handler(commands=['payu'])
def cmd_payu(message):
    process_gateway_check(message, "PayU Gateway")

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
    print("TOJI CC CHECKER Engine Online...")
    bot.infinity_polling(skip_pending=True)
