
## 1. Make the run_manage.sh file executable
    chmod +x /path/to/your/run_manage.sh
## 2. Open the crontab and add the cronjob
    crontab -e
    */3 * * * * /usr/bin/python3 ~/manage.py >> ~/logfile.log 2>&1


