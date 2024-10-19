from datetime import datetime
from .objects import get_pararius_objects, get_object_details, enrich_details, cleanup
from .telegram import send_text
import time
from .file_handler import handler
import logging
import gc

def cronjob(city='haarlem', minimum_bedrooms='1', max_price_eur='1500', km_radius='10', bot_token='', chat_id=''):
    logging.info(f"Starting cronjob with parameters: city={city}, minimum_bedrooms={minimum_bedrooms}, max_price_eur={max_price_eur}, km_radius={km_radius}")
    
    try:
        # build URL from params
        city = '/' + city if city else ''
        minimum_bedrooms = '/' + minimum_bedrooms + '-bedrooms' if minimum_bedrooms else ''
        max_price_eur = '/0-' + str(int(max_price_eur)) if int(max_price_eur) > 0 else ''
        km_radius = '/radius-' + km_radius if km_radius else ''
        
        url = f'https://www.pararius.com/apartments{city}{minimum_bedrooms}{max_price_eur}{km_radius}'
        logging.info(f"Built URL: {url}")
        
        fresh_objects = get_pararius_objects(url=url)
        logging.info(f"Retrieved {len(fresh_objects)} objects for query: https://www.pararius.com/apartments{city}{minimum_bedrooms}{max_price_eur}{km_radius}")
        
        # Initialize file_handler
        file_handler = handler()
        
        # Get new items by comparing with Azure Table Storage
        known_links = [entity['link'] for entity in file_handler.query_entities("PartitionKey eq 'pararius'")]
        unknown_objects = [obj for obj in fresh_objects if obj not in known_links]
        logging.info(f"Found {len(unknown_objects)} new objects for query: https://www.pararius.com/apartments{city}{minimum_bedrooms}{max_price_eur}{km_radius}\n{unknown_objects}")
        
        # Insert new objects into Azure Table Storage
        try:
            for link in unknown_objects:
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                try:
                    file_handler.insert_row_to_table(link, timestamp)
                except Exception as e:
                    logging.error(f"Insert Error for '{link}': {e}")
        except Exception as e:
            logging.error(e)
        
        # Notify me in a telegram channel for a new house
        for link in unknown_objects:
            msg = ''
            details = get_object_details(link)
            enriched_details = enrich_details(details)
            for k, v in enriched_details.items():
                if v:
                    msg = msg + f"{k} - {v}\n"
            msg = f"{msg}{link}".replace('_',' ')
            send_text(msg, bot_token=bot_token, chat_id=chat_id)
            time.sleep(1)
            
            # Clear variables
            del msg, details, enriched_details

    except Exception as e:
        logging.error(f"An error occurred in cronjob: {str(e)}")
        raise
    finally:
        # Clean up the session
        cleanup()
    
    # Force garbage collection
    gc.collect()