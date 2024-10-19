import logging
import requests
import os

def send_text(msg='Test message', bot_token='', chat_id=''):
    """
    Not allowed to put in underscores
    """
    send_text = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chat_id}&parse_mode=Markdown&text={msg.replace('_',' ')}"
    try:
        response = requests.get(send_text)
        logging.info(f"Sent message: {msg.replace('_',' ').split('pararius.com/')[-1]}")
    except Exception as e:
        logging.error(e)
    return response.json()

if __name__ == "__main__":
    print(send_text())