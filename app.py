
import os
import time
import gc
from dotenv import load_dotenv
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from modules import manage  # Import the manage.py file
import yaml

# Read config
def read_config(path="config.yml"):
    with open(path, "r") as file:
        config = yaml.safe_load(file)
    return config

config = read_config()

# Read .ENV-file
load_dotenv()

bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
chat_id = os.getenv('TELEGRAM_CHAT_ID')

def run_job():
    manage.cronjob(
        city=config["city"].lower(),
        minimum_bedrooms=str(config["minimum_bedrooms"]),
        max_price_eur=str(config["max_price_eur"]),
        km_radius=str(config["km_radius"]),
        bot_token=bot_token,
        chat_id=chat_id
    )
    gc.collect()  # Force garbage collection
    logging.info('Job executed.')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    run_job() #initial run of job
    time.sleep(20)

    scheduler = BlockingScheduler()
    scheduler.add_job(run_job, 'interval', minutes=5)

    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass

    run_job()
