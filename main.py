import os
import logging
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_CHAT_ID = os.getenv("ADMIN_CHAT_ID")

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)

# Conversation states
WAITING_FOR_DETAILS, WAITING_FOR_FILE = range(2)

# --- Handlers ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📦 Our Services", callback_data="services")],
        [InlineKeyboardButton("📝 Request a Quote / Order", callback_data="request_quote")],
        [InlineKeyboardButton("📞 Contact Information", callback_data="contact")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    # ✏️ EDIT YOUR WELCOME MESSAGE HERE:
    welcome_text = (
        "Welcome to Butterfly Ethiopia General Trading PLC! 🦋\n\n"
        "Your trusted partner for commercial printing, packaging, and advertising solutions in Addis Ababa.\n\n"
        "Please select an option below to explore our services or send us a direct order request."
    )
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(welcome_text, reply_markup=reply_markup)

async def handle_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles button navigation with photos, animations, and pricing."""
    query = update.callback_query
    await query.answer()

    if query.data == "services":
        keyboard = [
            [InlineKeyboardButton("🖨 Commercial Printing", callback_data="svc_printing")],
            [InlineKeyboardButton("📦 Packaging & Silk Screen", callback_data="svc_packaging")],
            [InlineKeyboardButton("🌐 Import & Distribution", callback_data="svc_import")],
            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")],
        ]
        
        if query.message.photo or query.message.animation:
            await query.message.delete()
            await query.message.reply_text("Choose a category to view items, media & pricing:", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text("Choose a category to view items, media & pricing:", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "svc_printing":
        keyboard = [
            [InlineKeyboardButton("🛒 Order Printing", callback_data="request_quote")],
            [InlineKeyboardButton("🔙 Back to Services", callback_data="services")]
        ]
        
        caption = (
            "🖨 **Commercial Printing & Advertising**\n\n"
            "💵 **Estimated Pricing:**\n"
            "• **Banners:** Starting at 450 ETB / m²\n"
            "• **Stickers:** Starting at 250 ETB / pack\n"
            "• **Business Cards:** Starting at 500 ETB / 100 pcs\n"
            "• **T-Shirts & Mugs:** Custom quotes based on volume\n\n"
            "✨ *High-quality prints with rapid turnaround!*"
        )
        
        await query.message.delete()
        await query.message.reply_photo(
            photo="https://images.unsplash.com/photo-1562654501-a0ccc0fc3fb1",
            caption=caption,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "svc_packaging":
        keyboard = [
            [InlineKeyboardButton("🛒 Order Packaging", callback_data="request_quote")],
            [InlineKeyboardButton("🔙 Back to Services", callback_data="services")]
        ]
        
        caption = (
            "📦 **Packaging & Silk Screen Printing**\n\n"
            "💵 **Estimated Pricing:**\n"
            "• **Poly Mailer Bags:** Custom bulk quotes\n"
            "• **Spice & Food Labels:** High-grade custom printing\n"
            "• **Flatbed Screen Printing:** Custom batch rates\n\n"
            "⚡ *Durable materials and professional branding.*"
        )
        
        await query.message.delete()
        await query.message.reply_animation(
            animation="https://media.giphy.com/media/3o7TKSjRrfIPjeiVyM/giphy.gif",
            caption=caption,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "svc_import":
        keyboard = [
            [InlineKeyboardButton("📞 Contact Us", callback_data="contact")],
            [InlineKeyboardButton("🔙 Back to Services", callback_data="services")]
        ]
        
        caption = (
            "🌐 **Import & Procurement Services**\n\n"
            "• Printing equipment & industrial raw materials sourcing.\n"
            "• Direct tender support & logistics in Ethiopia.\n\n"
            "💬 *Contact us directly for import consultations.*"
        )
        
        await query.message.delete()
        await query.message.reply_text(
            text=caption,
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "contact":
        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]]
        contact_info = (
            "📞 **Contact Information**\n\n"
            "🏢 **Company:** Butterfly Ethiopia General Trading PLC\n"
            "📍 **Location:** Dembel City Center, Addis Ababa\n"
            "📱 **Phone:** +251 911 000 000\n"
            "✉️ **Email:** info@butterflyethiopia.com"
        )
        if query.message.photo or query.message.animation:
            await query.message.delete()
            await query.message.reply_text(contact_info, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.edit_message_text(contact_info, parse_mode="Markdown", reply_markup=InlineKeyboardMarkup(keyboard))

    elif query.data == "main_menu":
        if query.message.photo or query.message.animation:
            await query.message.delete()
        await start(update, context)
# --- Quote & Inquiry Flow ---

async def start_quote(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Initiates guided inquiry collection."""
    query = update.callback_query
    await query.answer()
    
    await query.edit_message_text(
        "Please type the details of your request:\n\n"
        "Include quantity, specs, product type, or any specific requirements."
    )
    return WAITING_FOR_DETAILS

async def receive_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Stores text details and asks for files/artwork."""
    context.user_data["quote_details"] = update.message.text
    
    keyboard = [[InlineKeyboardButton("⏩ Skip File Upload", callback_data="skip_file")]]
    await update.message.reply_text(
        "Got it! Now, please attach any related artwork, logo, receipt, or PDF file.\n\n"
        "If you don't have a file, click 'Skip File Upload'.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return WAITING_FOR_FILE

async def receive_file_and_finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Forwards complete request + file to Admin."""
    user = update.effective_user
    details = context.user_data.get("quote_details", "N/A")
    
    summary = (
        f"🚨 **New Order / Quote Request**\n\n"
        f"👤 **From:** {user.full_name} (@{user.username or 'No Username'})\n"
        f"🆔 **User ID:** `{user.id}`\n\n"
        f"📝 **Details:**\n{details}"
    )

    # Forward to Admin
    if ADMIN_CHAT_ID:
        if update.callback_query and update.callback_query.data == "skip_file":
            await update.callback_query.answer()
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=summary, parse_mode="Markdown")
            await update.callback_query.edit_message_text("✅ Your inquiry has been sent! Our team will contact you shortly.")
        else:
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=summary, parse_mode="Markdown")
            await context.bot.copy_message(
                chat_id=ADMIN_CHAT_ID,
                from_chat_id=update.message.chat_id,
                message_id=update.message.message_id
            )
            await update.message.reply_text("✅ Your inquiry and file have been received! We will review and contact you shortly.")
    
    context.user_data.clear()
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancels conversation."""
    await update.message.reply_text("Action canceled.")
    context.user_data.clear()
    return ConversationHandler.END

# --- Main Application Builder ---

def main():
    if not BOT_TOKEN or not ADMIN_CHAT_ID:
        raise ValueError("Missing BOT_TOKEN or ADMIN_CHAT_ID in environment variables.")

    app = Application.builder().token(BOT_TOKEN).build()

    # Conversation handler for Quote Flow
    quote_conv = ConversationHandler(
        entry_points=[CallbackQueryHandler(start_quote, pattern="^request_quote$")],
        states={
            WAITING_FOR_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, receive_details)],
            WAITING_FOR_FILE: [
                MessageHandler(filters.PHOTO | filters.Document.ALL, receive_file_and_finish),
                CallbackQueryHandler(receive_file_and_finish, pattern="^skip_file$")
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    # Register handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(quote_conv)
    app.add_handler(CallbackQueryHandler(handle_button))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()