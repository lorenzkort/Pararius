from datetime import datetime
from .objects import get_pararius_objects, get_object_details, enrich_details, cleanup
from .telegram import send_text
import time
from .file_handler import handler
import logging
import gc

from memory_profiler import profile

@profile
def cronjob(city='haarlem', minimum_bedrooms='1', max_price='1500', km_radius='10'):
    logging.info(f"Starting cronjob with parameters: city={city}, minimum_bedrooms={minimum_bedrooms}, max_price={max_price}, km_radius={km_radius}")
    
    try:
        # build URL from params
        city = '/' + city if city else ''
        minimum_bedrooms = '/' + minimum_bedrooms + '-bedrooms' if minimum_bedrooms else ''
        max_price = '/0-' + str(int(max_price)) if int(max_price) > 0 else ''
        km_radius = '/radius-' + km_radius if km_radius else ''
        
        url = f'https://www.pararius.com/apartments{city}{minimum_bedrooms}{max_price}{km_radius}'
        logging.info(f"Built URL: {url}")
        
        fresh_objects = get_pararius_objects(url=url)
        logging.info(f"Retrieved {len(fresh_objects)} fresh objects")
        
        # Initialize file_handler
        file_handler = handler()
        
        # Get new items by comparing with Azure Table Storage
        known_links = [entity['link'] for entity in file_handler.query_entities("PartitionKey eq 'pararius'")]
        unknown_objects = [obj for obj in fresh_objects if obj not in known_links]
        print(unknown_objects)
        
        # Notify me in a telegram channel for a new house
        for link in unknown_objects:
            msg = ''
            details = get_object_details(link)
            enriched_details = enrich_details(details)
            for k, v in enriched_details.items():
                if v:
                    msg = msg + f"{k} - {v}\n"
            msg = f"{msg}{link}".replace('_',' ')
            print(msg)
            send_text(msg)
            time.sleep(1)
            
            # Clear variables
            del msg, details, enriched_details
        
        # Insert new objects into Azure Table Storage
        for link in unknown_objects:
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            file_handler.insert_row_to_table(link, timestamp)

    except Exception as e:
        logging.error(f"An error occurred in cronjob: {str(e)}")
        raise
    finally:
        # Clean up the session
        cleanup()
    
    # Force garbage collection
    gc.collect()