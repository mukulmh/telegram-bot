from telegram import Bot
from telegram.error import TelegramError
from celery_config import celery_app

@celery_app.task
async def send_message_to_group(api_token, group_id, message):
    # Create a bot instance using the provided API token
    bot = Bot(token=api_token)
    
    try:
        # Send the message to the specified group using the bot
        await bot.send_message(chat_id=group_id, text=message)
        return {"status": "success", "message": f"Message sent to group: {message}"}
    except TelegramError as e:
        return {"status": "error", "message": f"Error sending message: {e}"}
