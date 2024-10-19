import gc
import logging
from apscheduler.schedulers.blocking import BlockingScheduler
from modules import manage  # Import the manage.py file

def run_job():
    manage.cronjob()  # Your existing function to run the job
    gc.collect()  # Force garbage collection
    logging.info('Job executed.')

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    scheduler = BlockingScheduler()
    scheduler.add_job(run_job, 'interval', minutes=5)
    
    try:
        scheduler.start()
    except (KeyboardInterrupt, SystemExit):
        pass
    run_job()