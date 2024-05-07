from flask import Flask, request
import telegram
import os
from dotenv import load_dotenv

load_dotenv()
bot_token = os.environ.get('BOT_TOKEN')

app = Flask(__name__)
bot = telegram.Bot(token=bot_token)

@app.route('/webhook', methods=['POST'])
def respond():
    update = telegram.Update.de_json(request.get_json(force=True), bot)
    chat_id = update.message.chat.id
    text = update.message.text.encode('utf-8').decode()
    print("got text message :", text)

    if text == '/start':
        welcome_text = 'Welcome to the bot! Type /help to see the available commands.'
        bot.sendMessage(chat_id=chat_id, text=welcome_text)
    elif text == '/help':
        help_text = 'Available commands:\n/start - Start the bot\n/help - Show the available commands'
        bot.sendMessage(chat_id=chat_id, text=help_text)
    else:
        bot.sendMessage(chat_id=chat_id, text='Invalid command. Type /help to see the available commands.')
        
    return 'ok'


@app.route('/setwebhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('https://telegram-bot-f9vw.onrender.com/webhook')
    print(s)
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"


@app.route('/')
def index():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(port=8443,threaded=True)
