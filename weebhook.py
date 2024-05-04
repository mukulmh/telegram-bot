import requests

bot_token = 'YOUR_BOT_TOKEN'
webhook_url = 'https://telegram-bot-fs8x.onrender.com/webhook'

# API URL for setting webhook
set_webhook_url = f'https://api.telegram.org/bot{bot_token}/setWebhook'

# Set the webhook
response = requests.post(
    set_webhook_url,
    data={'url': webhook_url},
)

# Print the response
print(response.json())
