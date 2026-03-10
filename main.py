import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

from config import TELEGRAM_TOKEN
from fetcher import fetch_article
from summarizer import summarize
from obsidian_writer import write_note, is_url_seen, mark_url_seen

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Send me a URL and I'll summarize the article and save it to your Obsidian vault."
    )


async def handle_url(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text.strip()

    if not url.startswith(("http://", "https://")):
        await update.message.reply_text("Please send a valid URL starting with http:// or https://")
        return

    if is_url_seen(url):
        await update.message.reply_text("⚠️ Esta URL ya está guardada en tu vault.")
        return

    await update.message.reply_text("Leyendo y resumiendo... un momento. 🔍")

    try:
        text = fetch_article(url)
    except Exception as e:
        logger.error("Fetch error for %s: %s", url, e)
        await update.message.reply_text(f"Could not fetch the article: {e}")
        return

    try:
        summary = summarize(text, url)
    except Exception as e:
        logger.error("Summarize error: %s", e)
        await update.message.reply_text(f"Could not summarize the article: {e}")
        return

    try:
        filepath = write_note(url, summary)
        logger.info("Saved note to %s", filepath)
    except Exception as e:
        logger.error("Obsidian write error: %s", e)
        await update.message.reply_text(f"Could not save note to Obsidian: {e}")
        return

    mark_url_seen(url)

    title = summary.get("title", "Untitled")
    category = summary.get("category", "Basura")
    vale = summary.get("vale_la_pena", "")
    worth = summary.get("worth_reading", True)

    if worth:
        msg = f"✅ {title} → {category}\n\n📖 Vale la pena: {vale}"
    else:
        msg = f"🗑️ {title}\n\n❌ No vale la pena: {vale}"

    await update.message.reply_text(msg)


def main() -> None:
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_url))
    logger.info("Bot started.")
    app.run_polling()


if __name__ == "__main__":
    main()
