from datetime import datetime
from objects import get_pararius_objects, get_object_details, enrich_details
from telegram import send_text
import time

def cronjob(city='haarlem', minimum_bedrooms='1', max_price='1500', km_radius='10'):
    
    # build URL from params
    city = '/' + city if city else ''
    minimum_bedrooms = '/' + minimum_bedrooms + '-bedrooms' if minimum_bedrooms else ''
    max_price = '/0-' + str(int(max_price)) if int(max_price) > 0 else ''
    km_radius = '/radius-' + km_radius if km_radius else ''
    
    
    url = f'https://www.pararius.com/apartments{city}{minimum_bedrooms}{max_price}{km_radius}'

    fresh_objects = get_pararius_objects(url=url)
    
    # Get new items
    unkown_objects = [obj for obj in fresh_objects if obj not in open('link_file.csv', 'r').read()]
    print(unkown_objects)
    
    # Notify me in a telegram channel for a new house
    for link in unkown_objects:
        msg = ''
        for k, v in enrich_details(get_object_details(link)).items():
            if v:
                msg = msg + f"{k} - {v}\n"
        msg = f"{msg}{link}".replace('_',' ')
        print(msg)
        send_text(msg)
        time.sleep(0.3)
        

    # Append new objects to file
    unkown_objects = [f'{o}, {datetime.now().strftime("%d/%m/%Y %H:%M:%S")}\n' for o in unkown_objects]
    with open('link_file.csv', 'a') as f:
        for o in unkown_objects:
            f.write(o)

cronjob()