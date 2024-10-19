import requests
import os
from dotenv import load_dotenv

load_dotenv()

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

def send_text(msg='Test message'):
    """
    Not allowed to put in underscores
    """
    send_text = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={msg.replace('_',' ')}"
    response = requests.get(send_text)
    print(response)
    return response.json()

if __name__ == "__main__":
    print(send_text())