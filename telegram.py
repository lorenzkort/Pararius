import requests

def send_text(msg='Test message', chatId = '-1001797708509'):
    """
    Not allowed to put in underscores
    """
    bot_token = '1132455575:AAFWwpwZ-qJUdabq-WbSHoK8nh7aPwMoVo4'
    send_text = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={chatId}&parse_mode=Markdown&text={msg.replace('_',' ')}"
    response = requests.get(send_text)
    print(response)
    return response.json()

# https://api.telegram.org/bot1132455575:AAFWwpwZ-qJUdabq-WbSHoK8nh7aPwMoVo4/getUpdates

if __name__ == "__main__":
    print(send_text())