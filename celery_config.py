from celery import Celery
from telegram import Bot
from telegram.error import TelegramError
import asyncio

celery_app = Celery(
    "telegram_bot",
    broker="redis://localhost:6379/0",  # Redis broker URL
    backend="redis://localhost:6379/0",  # Redis backend URL (optional)
)


async def async_send_message_to_group(api_token, group_id, message):
    bot = Bot(token=api_token)
    try:
        await bot.send_message(chat_id=group_id, text=message)
        return {"status": "success", "message": f"Message sent to group: {message}"}
    except TelegramError as e:
        return {"status": "error", "message": f"Error sending message: {e}"}


@celery_app.task
def send_message_to_group(api_token, group_id, message):
    loop = asyncio.get_event_loop()
    result = loop.run_until_complete(async_send_message_to_group(api_token, group_id, message))
    return result
