from fastapi import FastAPI, Request
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio, uvicorn
import os
from dotenv import load_dotenv

app = FastAPI()
load_dotenv()
bot_token = os.getenv("BOT_TOKEN")

application = Application.builder().token(bot_token).build()

async def initialize_app():
    await application.initialize()  # Initialize the Application instance
    print("Webhook app initialized")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    print(chat_id)
    # Send a welcome message back to the user
    await context.bot.send_message(chat_id=chat_id, text="Welcome to the bot!")

start_handler = CommandHandler('start', start)
application.add_handler(start_handler)


@app.post("/webhook")
async def handle_webhook(request: Request):
    # Parse the JSON request body
    data = await request.json()
    print(data)
    # Convert the data into a Telegram Update
    update = Update.de_json(data, application.bot)
    print(update)

    # Use the application to process the update
    await application.update_queue.put(update)
    
    # Return a simple JSON response to acknowledge receipt of the update
    return {"status": 200, "message": "App is running"}


@app.get("/")
async def home(request: Request):
    return {"message": "Success"}

# Main function to start both FastAPI and Telegram bot
def main():
    # Run the FastAPI server using uvicorn.run
    uvicorn.run(app, host="0.0.0.0", port=8000)

# Start the application
if __name__ == "__main__":
    # Run the async function to initialize the Telegram bot
    asyncio.run(initialize_app())
    # Start the FastAPI server and Telegram bot
    main()

