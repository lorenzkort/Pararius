from datetime import datetime
import pandas as pd
from objects import get_pararius_objects
from telegram import send_text

fresh_objects = get_pararius_objects(url='https://www.pararius.com/apartments/haarlem/0-1300')

def init_file(fresh_objects):
    objs = [f'{o}, {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}\n' for o in fresh_objects]
    with open('link_file.csv', 'w+') as f:
        f.write('link,timestamp\n')
        for o in objs:
            f.write(o)
    return

def cronjob():
    # Get new items
    unkown_objects = [obj for obj in fresh_objects if obj not in open('link_file.csv', 'r').read()]
    
    # Notify me in a telegram channel for a new house
    [send_text(f'New House!\n{link}') for link in unkown_objects] 

    # Append new objects to file
    unkown_objects = [f'{o}, {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}\n' for o in unkown_objects]
    with open('link_file.csv', 'a') as f:
        for o in unkown_objects:
            f.write(o)

cronjob()