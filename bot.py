# FlowtuBot - Fixed Version for GitHub Codespaces
import os
import logging
import asyncio
import sys
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# ================== CONFIG ==================
TOKEN = "8599299717:AAFK7GiV_ZeF-mtrZx7j7V-vSXd-KcI2whY"          # ← CHANGE THIS
ADMIN_ID = 5848498487
# ============================================

def create_data_files():
    os.makedirs("data", exist_ok=True)
    
    if not os.path.exists("data/instructions.txt"):
        with open("data/instructions.txt", "w", encoding="utf-8") as f:
            f.write("""How to use SOCKS proxies on Android:

1. Download a SOCKS5-compatible proxy client app from your app store.

2. Open the proxy app and add a new configuration.

3. Enter the proxy details:
   - Protocol: SOCKS5
   - IP Address / Host: [from the proxy list]
   - Port: [from the proxy list]
   - (Optional) Username and Password if provided

4. Enable the proxy for your Wi-Fi or mobile data.

5. Test by checking your IP address.

Notes:
- Free proxies can be slow or die quickly.
- Rotate them often.
""")

    # Dummy proxies (replace with real ones)
    if not os.path.exists("data/socks1.txt"):
        with open("data/socks1.txt", "w", encoding="utf-8") as f:
            for i in range(1, 31):
                f.write(f"185.XX.XX.{i}:1080\n")
    
    if not os.path.exists("data/socks2.txt"):
        with open("data/socks2.txt", "w", encoding="utf-8") as f:
            for i in range(1, 31):
                f.write(f"194.XX.XX.{i}:9150\n")

create_data_files()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📄 Instructions", callback_data="instructions")],
        [InlineKeyboardButton("🔌 SOCKS List 1", callback_data="socks1")],
        [InlineKeyboardButton("🔌 SOCKS List 2", callback_data="socks2")],
        [InlineKeyboardButton("💬 Feedback", callback_data="feedback")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("👋 Welcome to **FlowtuBot**!\nChoose an option:", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "instructions":
        with open("data/instructions.txt", "r", encoding="utf-8") as f:
            await query.edit_message_text(f.read())

    elif query.data in ["socks1", "socks2"]:
        filename = "data/socks1.txt" if query.data == "socks1" else "data/socks2.txt"
        caption = "SOCKS List 1 - FlowtuBot" if query.data == "socks1" else "SOCKS List 2 - FlowtuBot"
        
        with open(filename, "r", encoding="utf-8") as f:
            content = f.read()
        
        if len(content) > 3500:
            await query.edit_message_text("📤 Sending as file...")
            await context.bot.send_document(chat_id=query.message.chat_id, 
                                          document=open(filename, "rb"), 
                                          caption=caption)
        else:
            await query.edit_message_text(f"🔌 **{caption}**\n\n{content}")

    elif query.data == "feedback":
        await query.edit_message_text("💬 Send your message / photo / file now.\nIt will be forwarded to the admin.")
        context.user_data['awaiting_feedback'] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get('awaiting_feedback'):
        try:
            await context.bot.forward_message(ADMIN_ID, update.message.chat_id, update.message.message_id)
            await update.message.reply_text("✅ Feedback sent to admin. Thank you!")
        except:
            await update.message.reply_text("❌ Failed to send.")
        context.user_data['awaiting_feedback'] = False

def main():
    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, handle_message))

    print("🤖 FlowtuBot is running... Press Ctrl+C to stop.")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    # Fix for GitHub Codespaces / running event loop issues
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        main()
    except KeyboardInterrupt:
        print("\nBot stopped.")
    except RuntimeError as e:
        if "event loop" in str(e).lower():
            print("Event loop error detected. Running with nest_asyncio...")
            import nest_asyncio
            nest_asyncio.apply()
            main()
        else:
            raise
