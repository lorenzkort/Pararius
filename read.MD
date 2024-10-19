# Pararius Housing Notifier

## Scrapes Pararius, stores links in Azure Table Store and sends a Telegram Message to a Group chat for new properties

### When using on Windows or Mac
1. Install requirements: `pip install -r requirements.txt`
2. Create an Azure Table Store and add the connection string as environment variable `AZURE_TABLES_CONNNECTION_STRING` in /modules/.ENV
3. Create a Telegram Bot and add the token as environment variable `TELEGRAM_BOT_TOKEN` in /modules/.ENV
4. Add the Telegram Bot to a Group chat and get the group chat ID (starts with a '-' sign)
5. Add the Chat ID to `TELEGRAM_CHAT_ID` environment variable in /modules/.ENV
6. Run `python app.py`

### When using on a raspberry pi
1. sudo apt install chromium-browser
2. Install requirements: `pip install -r requirements.txt`
3. Create an Azure Table Store and add the connection string as environment variable `AZURE_TABLES_CONNNECTION_STRING` in /modules/.ENV
4. Create a Telegram Bot and add the token as environment variable `TELEGRAM_BOT_TOKEN` in /modules/.ENV
5. Add the Telegram Bot to a Group chat and get the group chat ID (starts with a '-' sign)
6. Add the Chat ID to `TELEGRAM_CHAT_ID` environment variable in /modules/.ENV
7. Run `python app.py`

### When using with Docker
1. Create an Azure Table Store and add the connection string as environment variable `AZURE_TABLES_CONNNECTION_STRING` in /modules/.ENV
2. Create a Telegram Bot and add the token as environment variable `TELEGRAM_BOT_TOKEN` in /modules/.ENV
3. Add the Telegram Bot to a Group chat and get the group chat ID (starts with a '-' sign). Find it using https://api.telegram.org/bot<YourBOTToken>/getUpdates
4. Add the Chat ID to `TELEGRAM_CHAT_ID` environment variable in /modules/.ENV
5. `docker built -t pararius:latest .`
6. `docker run pararius:latest`