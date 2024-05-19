from flask import Flask, request
import telegram
import os
from dotenv import load_dotenv
import asyncio
import re
import mysql.connector
from mysql.connector import Error

load_dotenv()
bot_token = os.environ.get('BOT_TOKEN')
app = Flask(__name__)
bot = telegram.Bot(token=bot_token)


# Database connection configuration
db_config = {
    'host': 'pytgbot2.mysql.pythonanywhere-services.com',
    'user': 'pytgbot2',
    'password': 'py.Muku1',
    'database': 'pytgbot2$tgbot'
}

# Dictionary to keep track of user state
user_state = {}

def run_coroutine_sync(coro):
    loop = asyncio.get_event_loop()
    return loop.run_until_complete(coro)


# Function to validate Bangladeshi mobile number
def is_valid_mobile_number(number):
    # Regex pattern for Bangladeshi mobile numbers
    # pattern = re.compile(r'^(?:\+88|88)?01[3-9]\d{8}$')
    pattern = re.compile(r'^01[3-9]\d{8}$')
    return pattern.match(number)


# Function to connect to MySQL database
def connect_to_db():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
        return None


def insert_user_data(chat_id, username, mobile_number):
    connection = connect_to_db()
    if connection is None:
        return "error"

    try:
        cursor = connection.cursor()
        # Query to check if the mobile number already exists
        cursor.execute("SELECT * FROM users WHERE mobile_number = %s", (mobile_number,))
        if cursor.fetchone():
            return "mobile_exists"

        # # Query to check if the chat_id or username already exists
        # cursor.execute("SELECT * FROM users WHERE chat_id = %s OR username = %s", (chat_id, username))
        # if cursor.fetchone():
        #     return "user_exists"

        # Check if the user (chat_id or username) already exists
        cursor.execute("SELECT * FROM users WHERE chat_id = %s OR username = %s", (chat_id, username))
        existing_user = cursor.fetchone()
        if existing_user:
            # User exists, update mobile number
            update_query = "UPDATE users SET mobile_number = %s WHERE chat_id = %s OR username = %s"
            cursor.execute(update_query, (mobile_number, chat_id, username))
            connection.commit()
            return "mobile_updated"

        # If no duplicates found, insert new user data
        query = """
        INSERT INTO users (chat_id, username, mobile_number)
        VALUES (%s, %s, %s)
        """
        data = (chat_id, username, mobile_number)
        cursor.execute(query, data)
        connection.commit()
        return "success"
    except Error as e:
        print(f"Error inserting user data: {e}")
        connection.rollback()
        return "error"
    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


@app.route('/webhook', methods=['POST'])
def respond():
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    # Handle callback query updates
    if update.callback_query:
        callback_query = update.callback_query
        chat_id = callback_query.message.chat.id
        callback_data = callback_query.data

        # Handle the back button action
        if callback_data == "back":
            # Send the response to start over
            run_coroutine_sync(bot.send_message(chat_id=chat_id, text='Type /start to begin. 😀'))

            # Reset the state safely
            user_state.pop(chat_id, None)

            # Answer the callback query to acknowledge it
            run_coroutine_sync(callback_query.answer())
        return 'ok'

    # Handle message updates
    elif update.message:
        chat_id = update.message.chat.id
        text = update.message.text.encode('utf-8').decode()
        username = update.message.chat.username

        # Check user state
        current_state = user_state.get(chat_id, 'start')

        if current_state == 'start':
            if text == '/start':
                welcome_text = '🤖 Welcome to Sentinel bot! Please type in your mobile number for verification.'

                # Create an inline keyboard with a "Back" button
                keyboard = [[telegram.InlineKeyboardButton("Back", callback_data="back")]]
                reply_markup = telegram.InlineKeyboardMarkup(keyboard)

                run_coroutine_sync(bot.send_message(chat_id=chat_id, text=welcome_text, reply_markup=reply_markup))
                user_state[chat_id] = 'awaiting_mobile_number'  # Change state
            else:
                run_coroutine_sync(bot.send_message(chat_id=chat_id, text='Type /start to begin.'))

        elif current_state == 'awaiting_mobile_number':
            if is_valid_mobile_number(text):
                # Insert user data into the database
                insert_status = insert_user_data(chat_id, username, text)

                if insert_status == "success":
                    text = '✅ Mobile number verified successfully!'
                elif insert_status == "mobile_exists":
                    text='⚠ Mobile number is already verified!'
                elif insert_status == "mobile_updated":
                    text='✅ Mobile number is updated & verified!'
                else:
                    text='⛔ Error saving your data.'

                run_coroutine_sync(bot.send_message(chat_id=chat_id, text=text))
                # Reset the state after success
                user_state.pop(chat_id)

            else:
                error_text = '🚫 Invalid mobile number. Please enter a valid mobile number.'

                # Create an inline keyboard with a "Back" button
                keyboard = [[telegram.InlineKeyboardButton("Back", callback_data="back")]]
                reply_markup = telegram.InlineKeyboardMarkup(keyboard)

                run_coroutine_sync(bot.send_message(chat_id=chat_id, text=error_text, reply_markup=reply_markup))
        return 'ok'

    return 'ok'  # Default return statement for other types of updates (e.g., edited messages)


@app.route('/send-message', methods=['POST'])
def send_message_personal():
    data = request.get_json()

    connection = connect_to_db()
    if connection is None:
        return "error"
    cursor = connection.cursor()
    mobile_number = data.get('mobile_number')
    message = data.get('message')

    # Check if the user (mobile_number) exists
    cursor.execute("SELECT * FROM users WHERE mobile_number = %s", (mobile_number,))
    existing_user = cursor.fetchone()
    print(existing_user)
    if existing_user:
        chat_id = existing_user[1]
        run_coroutine_sync(bot.send_message(chat_id=chat_id, text=message))
        return 'success'
    else:
        return 'user not found'


@app.route('/')
def index():
    return 'Hello World!'


if __name__ == '__main__':
    app.run(port=8443,threaded=True)
