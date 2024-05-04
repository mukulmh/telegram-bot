from fastapi import FastAPI, Request, HTTPException
from pydantic import BaseModel
from celery_config import send_message_to_group
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler
import json

app = FastAPI()

bot_token = 'YOUR_BOT_TOKEN'

application = Application.builder().token(bot_token).build()
application.initialize()  # Initialize the Application instance

async def start(update: Update, context):
    chat_id = update.effective_chat.id
    await context.bot.send_message(chat_id=chat_id, text="Welcome to the bot!")

start_handler = CommandHandler('start', start)
application.add_handler(start_handler)

@app.post("/webhook")
async def handle_webhook(request: Request):
    # Parse the JSON request body
    data = await request.json()

    # Convert the data into a Telegram Update
    update = Update.de_json(data, application.bot)

    # Use the application to process the update
    await application.update_queue.put(update)
    
    # Return a simple JSON response to acknowledge receipt of the update
    return {"status": "ok"}

class MessageData(BaseModel):
    api_token: str
    group_id: str
    message: str

@app.post("/send_message")
async def handle_send_message(data: MessageData):
    task = send_message_to_group.apply_async(
        args=(data.api_token, data.group_id, data.message)
    )
    return {"task_id": task.id}

@app.get("/")
async def home(request: Request):
    return {"message": "Success"}

# To run the FastAPI application, use the following command in the terminal:
# uvicorn app:app --host 0.0.0.0 --port 8000
