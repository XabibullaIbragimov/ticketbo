
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes

# Sozlamalar
ADMIN_ID = 7313947905  # Admin Telegram ID
CARD_NUMBER = "9860130176766231"  # Karta raqami
BOT_TOKEN = "8126339298:AAFPRYH7jgBfqVedMv2NZr0OHOPKuyPptTA"  # Bot token

# Foydalanuvchi xabarlari va IDlarni eslab qolish uchun lug'at
user_message_map = {}

# /start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🎉 *Mehr qo'llarini uzataylik* konsertiga xush kelibsiz!\n"
        "📅 Sana: 23-may 2025 yil\n"
        "🪑 Mavjud bilet: VIP – 150 000 so'm\n\n"
        "Bilet sotib olish uchun pastdagi tugmani bosing 👇"
    )
    button = [[InlineKeyboardButton("🎟 Bilet sotib olish", callback_data="buy_ticket")]]
    await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(button), parse_mode="Markdown")

# Tugma bosilganda javob
async def buy_ticket(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    text = (
        f"💳 Bilet narxi: *150 000 so'm*\n"
        f"⬇ Pulni quyidagi kartaga o‘tkazing:\n\n"
        f"`{CARD_NUMBER}`\n\n"
        "✅ So‘ngra to‘lov chek rasmini yoki PDF faylini shu yerga yuboring."
    )
    await query.edit_message_text(text, parse_mode="Markdown")

# Foydalanuvchi rasm yoki PDF yuborganida
async def handle_chek(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    caption = f"🧾 Yangi to‘lov chek!\n👤 @{user.username or user.first_name}\n🆔 {user.id}"

    if update.message.photo:
        msg = await context.bot.send_photo(chat_id=ADMIN_ID, photo=update.message.photo[-1].file_id, caption=caption)
        user_message_map[msg.message_id] = user.id
        await update.message.reply_text("✅ Rasm yuborildi. Admin tomonidan tez orada javob beriladi.")
    elif update.message.document:
        if update.message.document.mime_type == "application/pdf":
            msg = await context.bot.send_document(chat_id=ADMIN_ID, document=update.message.document.file_id, caption=caption)
            user_message_map[msg.message_id] = user.id
            await update.message.reply_text("✅ PDF yuborildi. Admin tomonidan tez orada javob beriladi.")
        else:
            await update.message.reply_text("❗ Faqat PDF hujjatlar qabul qilinadi.")
    else:
        await update.message.reply_text("❗ Iltimos, rasm yoki PDF fayl yuboring.")

# Admin reply berganida
async def admin_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.reply_to_message and update.effective_user.id == ADMIN_ID:
        replied_msg_id = update.message.reply_to_message.message_id
        if replied_msg_id in user_message_map:
            user_id = user_message_map[replied_msg_id]
            text = f"📩 Admindan javob:\n\n{update.message.text}"
            await context.bot.send_message(chat_id=user_id, text=text)
            await update.message.reply_text("✅ Javob foydalanuvchiga yuborildi.")
        else:
            await update.message.reply_text("❗ Bu xabarning foydalanuvchisi aniqlanmadi.")

# Noma'lum komandalar uchun
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Iltimos, /start buyrug'ini yuboring.")

# Botni ishga tushurish
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(buy_ticket, pattern="^buy_ticket$"))
    app.add_handler(MessageHandler(filters.PHOTO | filters.Document.PDF, handle_chek))
    app.add_handler(MessageHandler(filters.TEXT & filters.REPLY, admin_reply))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    print("🤖 Bot ishga tushdi...")
    app.run_polling()

if __name__ == "__main__":
    main()
