import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from telegram.error import RetryAfter, TimedOut, NetworkError

# 1. ضع التوكن الخاص ببوتك هنا
BOT_TOKEN = "8956367665:AAG21WFhOOakESWHrPQhiZtkrIZuzySHXyQ"

TOPICS_LIST = [
    {"name": "Chatting", "emojis": ["💬", "💭", "🗣️"]},
    {"name": "chunks", "emojis": ["🧳", "💼", "🎒"]},
    {"name": "Vocabulary", "emojis": ["🗳️", "📥", "📦"]},
    {"name": "Reading", "emojis": ["📰", "📖", "📚"]},
    {"name": "Tasks", "emojis": ["📝", "✏️", "✅"]},
    {"name": "Meetings", "emojis": ["📆", "🗓️", "📅"]},
    {"name": "Videos", "emojis": ["🎬", "📹", "📺"]},
    {"name": "Requests", "emojis": ["📣", "📢", "🙋"]},
    {"name": "Tongue Twisters", "emojis": ["👅", "🗣️", "🎙️"]},
    {"name": "Topics", "emojis": ["📁", "📂", "🗂️"]},
    {"name": "Exams", "emojis": ["📈", "📊", "💯"]},
    {"name": "Expressions", "emojis": ["💡", "✨", "🌟"]}
]

EMOJI_MAP = {}

async def load_emojis(bot):
    global EMOJI_MAP
    if EMOJI_MAP:
        return
    try:
        stickers = await bot.get_forum_topic_icon_stickers()
        for s in stickers:
            clean_emoji = s.emoji.replace("\ufe0f", "")
            EMOJI_MAP[clean_emoji] = s.custom_emoji_id
            EMOJI_MAP[s.emoji] = s.custom_emoji_id
    except Exception as e:
        print(f"خطأ في جلب الأيقونات: {e}")

async def setup_group(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    if chat.type not in ["group", "supergroup"]:
        await update.message.reply_text("هذا الأمر يعمل داخل الجروبات فقط.")
        return

    if not chat.is_forum:
        await update.message.reply_text("⚠️ يرجى تفعيل خيار الـ Topics من إعدادات الجروب أولاً ثم أعد إرسال /setup")
        return

    status_msg = await update.message.reply_text("جاري تجهيز الجروب وإنشاء الـ Topics... ⏳")
    await load_emojis(context.bot)

    try:
        await context.bot.edit_general_forum_topic(chat_id=chat.id, name="📚 Materials")
        await asyncio.sleep(1)
    except Exception as e:
        print(f"ملحوظة أثناء تعديل General: {e}")

    created_count = 0
    for item in TOPICS_LIST:
        topic_name = item["name"]
        custom_id = None
        for em in item["emojis"]:
            clean_em = em.replace("\ufe0f", "")
            if em in EMOJI_MAP:
                custom_id = EMOJI_MAP[em]
                break
            elif clean_em in EMOJI_MAP:
                custom_id = EMOJI_MAP[clean_em]
                break

        for attempt in range(3):
            try:
                await context.bot.create_forum_topic(
                    chat_id=chat.id,
                    name=topic_name,
                    icon_custom_emoji_id=custom_id
                )
                created_count += 1
                await asyncio.sleep(1.2)
                break
            except RetryAfter as e:
                await asyncio.sleep(e.retry_after + 1)
            except (TimedOut, NetworkError):
                await asyncio.sleep(2)
            except Exception:
                break

    try:
        await status_msg.edit_text(f"تم تعديل الـ General وإنشاء {created_count} Topics بنجاح! جاهز لشغل الطالب ✅")
    except Exception:
        pass

    await asyncio.sleep(3)
    try:
        await update.message.delete()
        await status_msg.delete()
    except Exception:
        pass

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("setup", setup_group))
    print("البوت يعمل الآن...")
    app.run_polling(drop_pending_updates=True)