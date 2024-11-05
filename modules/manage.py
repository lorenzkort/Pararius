from datetime import datetime
from .objects import get_pararius_objects, get_object_details, enrich_details
from .telegram import send_text
from .file_handler import AzureTableHandler
from dotenv import load_dotenv
import logging
import gc
from contextlib import contextmanager
from typing import List, Dict, Any
import time
import os

@contextmanager
def file_handler_context(azure_table_connection_string: str = ''):
    """Context manager for file handler to ensure proper cleanup"""
    load_dotenv()
    file_handler_instance = AzureTableHandler(azure_table_connection_string)
    try:
        yield file_handler_instance
    finally:
        # Add cleanup
        file_handler_instance.cleanup()

def process_property_batch(links: List[str],
                         file_handler_instance: Any,
                         bot_token: str,
                         chat_id: str,
                         batch_size: int = 5) -> None:
    """Process properties in smaller batches to manage memory"""
    for i in range(0, len(links), batch_size):
        batch = links[i:i + batch_size]

        for link in batch:
            try:
                # Process timestamp and storage
                timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
                file_handler_instance.insert_row_to_table(link, timestamp)

                # Get and process details
                details = get_object_details(link)
                enriched_details = enrich_details(details)

                # Prepare and send message
                msg_parts = [f"{k} - {v}" for k, v in enriched_details.items() if v]
                msg = "\n".join(msg_parts) + f"\n{link}".replace('_', ' ')
                send_text(msg, bot_token=bot_token, chat_id=chat_id)

                # Clear variables explicitly
                del details, enriched_details, msg_parts, msg

                time.sleep(1)  # Rate limiting

            except Exception as e:
                logging.error(f"Error processing link {link}: {str(e)}")
                continue

        # Force garbage collection after each batch
        gc.collect()

def cronjob(city: str = 'haarlem',
            minimum_bedrooms: str = '1',
            max_price_eur: str = '1500',
            km_radius: str = '10',
            bot_token: str = '',
            chat_id: str = '',
            azure_table_connection_string: str = '',
            batch_size: int = 5) -> None:
    """
    Optimized cronjob function with better memory management and error handling
    """
    logging.info(f"Starting cronjob with parameters: city={city}, "
                f"minimum_bedrooms={minimum_bedrooms}, max_price_eur={max_price_eur}, "
                f"km_radius={km_radius}")

    try:
        # Build URL with parameters
        url_params = {
            'city': f"/{city}" if city else '',
            'bedrooms': f"/{minimum_bedrooms}-bedrooms" if minimum_bedrooms else '',
            'price': f"/0-{int(max_price_eur)}" if int(max_price_eur) > 0 else '',
            'radius': f"/radius-{km_radius}" if km_radius else ''
        }

        url = f"https://www.pararius.com/apartments{''.join(url_params.values())}"
        logging.info(f"Built URL: {url}")

        # Get fresh objects
        fresh_objects = get_pararius_objects(url=url)
        if not fresh_objects:
            logging.warning("No objects retrieved from Pararius")
            return

        logging.info(f"Retrieved {len(fresh_objects)} objects")

        # Use context manager for file handler
        with file_handler_context(azure_table_connection_string) as file_handler_instance:
            # Query known links
            known_links = set(entity['link'] for entity in
                            file_handler_instance.query_entities("PartitionKey eq 'pararius'"))

            # Find new objects
            unknown_objects = list(set(fresh_objects) - known_links)
            logging.info(f"Found {len(unknown_objects)} new objects")

            if unknown_objects:
                # Process properties in batches
                process_property_batch(
                    links=unknown_objects,
                    file_handler_instance=file_handler_instance,
                    bot_token=bot_token,
                    chat_id=chat_id,
                    batch_size=batch_size
                )

        # Clear main variables
        del fresh_objects, known_links, unknown_objects

    except Exception as e:
        logging.error(f"Critical error in cronjob: {str(e)}")
        raise
    finally:
        # Cleanup and force garbage collection
        gc.collect()

if __name__ == "__main__":
    # Example usage with logging configuration
    logging.basicConfig(level=logging.INFO)
    cronjob(batch_size=3)  # Process 3 properties at a time
