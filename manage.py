from datetime import datetime
from objects import get_pararius_objects
from telegram import send_text

def cronjob(city='haarlem', minimum_bedrooms='1', max_price='1500', km_radius='10'):
    
    # build URL from params
    city = '/' + city if city else ''
    minimum_bedrooms = '/' + minimum_bedrooms if minimum_bedrooms else ''
    max_price = '/' + max_price if max_price else ''
    km_radius = '/' + km_radius if km_radius else ''
    
    
    url = f'https://www.pararius.com/apartments{city}{minimum_bedrooms}{max_price}{km_radius}'
    
    
    fresh_objects = get_pararius_objects(url=url)
    
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