from flask import Flask, request
import telegram
import os
from dotenv import load_dotenv
import asyncio

load_dotenv()
bot_token = os.environ.get('BOT_TOKEN')
app = Flask(__name__)
bot = telegram.Bot(token=bot_token)


def run_coroutine_sync(coro):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


@app.route('/webhook', methods=['POST'])
def respond():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    text = update.message.text.encode('utf-8').decode()
    print("got text message :", text)

    if text == '/start':
        print("start command received")
        welcome_text = 'Welcome to the bot! Type /help to see the available commands.'
        run_coroutine_sync(bot.send_message(chat_id=chat_id, text=welcome_text))
    elif text == '/help':
        print("help command received")
        help_text = 'Available commands:\n/start - Start the bot\n/help - Show the available commands'
        run_coroutine_sync(bot.send_message(chat_id=chat_id, text=help_text))
    else:
        print("invalid command received")
        run_coroutine_sync(bot.send_message(chat_id=chat_id, text='Invalid command. Type /help to see the available commands.'))
        
    return 'ok'


@app.route('/')
def index():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(port=8443,threaded=True)
