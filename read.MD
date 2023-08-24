
## 1. Make the run_manage.sh file executable
    chmod +x /path/to/your/run_manage.sh
## 2. Open the crontab and add the cronjob
    crontab -e
    */1 * * * * /usr/bin/python3 /home/lorenz/Pararius/manage.py >> /home/lorenz/Pararius/logfile.log 2>&1


