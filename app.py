import os
import threading
import requests
from flask import Flask, request, jsonify
from pyrogram import Client, filters

app = Flask(__name__)
botify = Client("./my_bot")

# Replace with your Telegram bot token
BOT_TOKEN = "5821748146:AAEa5mi0FMN6XoRiELUYSkjCa9dRqyQkrU8"
pcloud_auth = "MeF2iVZXtk8Zo8FNiGnn4mJ8rgTygUB0wXhXNPPV"

# Define the base URL for the Telegram Bot API
BASE_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"


# Function to send a message
def send_message(chat_id, text):
    url = f"{BASE_URL}/sendMessage"
    data = {"chat_id": chat_id, "text": text}
    response = requests.post(url, data=data)
    return response.json()


# Function to list items from pCloud
def list_items():
    session = requests.Session()
    folderid = 'YOUR_PCLOUD_FOLDER_ID'
    adata = {'auth': pcloud_auth, 'folderid': folderid}
    post = session.post('http://eapi.pcloud.com/listfolder?', data=adata)
    data = post.json()['metadata']['contents']
    return data


# Define a handler for messages containing documents
@botify.on_message(filters.document)
async def download_document(client, message):
    try:
        # Get the document object
        document = message.document

        # Download the document
        file_name = document.file_name
        await message.download(file_name)
        print("Downloading file...")

        # You can now work with the downloaded file, e.g., save it to a different location
        # or process it further.

        # Send a confirmation message
        await message.reply(f"Downloaded file: {file_name}")

    except Exception as e:
        print(f"Error downloading file: {e}")


@app.route('/')
def home():
    return "Welcome to the Max Maven Bot!"


@app.route('/webhook', methods=['POST'])
def webhook():
    data = request.get_json()

    if 'message' in data:
        message = data['message']
        chat_id = message['chat']['id']
        text = message.get('text', '')

        if text.startswith('/'):
            handle_commands(chat_id, text)

    return jsonify({'status': 'ok'})


# Define command handling
def handle_commands(chat_id, command):
    if command == "/start":
        send_message(chat_id, "Hi! This is Max Maven Bot. I am always alive.")
    elif command == "/help":
        send_message(chat_id, "Sure! Here's how you can use Max Maven Bot:\n\n"
                              "/start - Start the bot\n"
                              "/help - Get help and commands\n"
                              "/about - Learn more about Max Maven Bot")
    elif command == "/about":
        send_message(chat_id, "Max Maven Bot is a simple Telegram bot created for Magic Community Group."
                              " It is created by PK Mystic")
    elif command == "/pcloud":
        items = list_items()
        send_message(chat_id, "Here are the recent changes in pCloud:\n" + "\n".join(items))
    else:
        send_message(chat_id, "I'm not sure what you mean. Use /help to see available commands.")


if __name__ == '__main__':
    # Start the Pyrogram bot in a separate thread
    bot_thread = threading.Thread(target=botify.run)
    bot_thread.start()

    # Run the Flask app in the main thread
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
