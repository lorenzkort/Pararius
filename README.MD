# Pararius Housing Notifier
Scrapes Pararius rental objects, stores links in Azure Table Store and sends a Telegram Message to a Group chat for new properties

### When using on Windows or Mac
1. Install requirements: `pip install -r requirements.txt`
2. Change modules/.ENV-example to modules/.ENV
3. Edit modules/config.yml to your likening (based on pararius.com)
4. Create an Azure Table Store and add the connection string as environment variable `AZURE_TABLES_CONNECTION_STRING` in /modules/.ENV
5. Create a Telegram Bot and add the token as environment variable `TELEGRAM_BOT_TOKEN` in /modules/.ENV
6. Add the Telegram Bot to a Group chat and get the group chat ID (starts with a '-' sign)
7. Add the Chat ID to `TELEGRAM_CHAT_ID` environment variable in /modules/.ENV
8. Run `python app.py`

### When using on a raspberry pi
1. sudo apt install chromium-browser
2. Change modules/.ENV-example to modules/.ENV
3. Edit modules/config.yml to your likening (based on pararius.com)
4. Install requirements: `pip install -r requirements.txt`
5. Create an Azure Table Store and add the connection string as environment variable `AZURE_TABLES_CONNECTION_STRING` in /modules/.ENV
6. Create a Telegram Bot and add the token as environment variable `TELEGRAM_BOT_TOKEN` in /modules/.ENV
7. Add the Telegram Bot to a Group chat and get the group chat ID (starts with a '-' sign)
8. Add the Chat ID to `TELEGRAM_CHAT_ID` environment variable in /modules/.ENV
9. Install chromium browser using `sudo apt install -y chromium-browser chromium-chromedriver`
9. Run in command line: `python app.py`

### When using with Docker
0. Install Docker
1. Change modules/.ENV-example to modules/.ENV
2. Edit modules/config.yml to your likening (based on pararius.com)
3. Create an Azure Table Store and add the connection string as environment variable `AZURE_TABLES_CONNECTION_STRING` in /modules/.ENV
4. Create a Telegram Bot and add the token as environment variable `TELEGRAM_BOT_TOKEN` in /modules/.ENV
5. Add the Telegram Bot to a Group chat and get the group chat ID (starts with a '-' sign). Find it using https://api.telegram.org/bot<YourBOTToken>/getUpdates
6. Add the Chat ID to `TELEGRAM_CHAT_ID` environment variable in /modules/.ENV
7. Run in command line: `docker built -t pararius:latest .`
8. Run in command line: `docker run pararius:latest`

# TODO
* Include environment-values in ACI using Azure KeyVault for example
* Ensure logging in every file is done correctly (also in main-example code snippet at the end of the file)
* Check if line 8 in __init__.py can be removed
* Surpress Response Header logging for Azure Tables Requests

* Update documentation
* Write documentation about pre-commit hooks
