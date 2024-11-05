from azure.data.tables import TableServiceClient, TableEntity
from contextlib import contextmanager
import os
from dotenv import load_dotenv
import logging
from typing import List, Dict, Any, Generator, Optional
import gc
from datetime import datetime

class AzureTableHandler:
    """Handles Azure Table Storage operations with proper resource management"""

    def __init__(self, connection_string: Optional[str] = None):
        """Initialize handler with connection string"""
        self.connection_string = connection_string
        if not self.connection_string:
            raise ValueError(
                "Azure Tables connection string not found. "
                "Please set the AZURE_TABLES_CONNECTION_STRING environment variable "
                "or provide it when initializing AzureTableHandler."
            )

        self.table_name = "links"
        self._service_client = None

    @contextmanager
    def _get_table_service(self):
        """Context manager for table service client"""
        if self._service_client is None:
            self._service_client = TableServiceClient.from_connection_string(
                conn_str=self.connection_string
            )
        try:
            yield self._service_client
        finally:
            if self._service_client:
                self._service_client.close()
                self._service_client = None

    @contextmanager
    def _get_table_client(self):
        """Context manager for table client with proper resource handling"""
        table_client = None
        try:
            with self._get_table_service() as service_client:
                table_client = service_client.get_table_client(table_name=self.table_name)
                yield table_client
        finally:
            if table_client:
                table_client.close()
            gc.collect()  # Force garbage collection after client usage

    def _create_entity(self, link: str, timestamp: str) -> TableEntity:
        """Create table entity with minimal memory usage"""
        entity = TableEntity()
        # Extract RowKey efficiently
        row_key = link.split('/')[-2] if '/' in link else link

        entity.update({
            'PartitionKey': 'pararius',
            'RowKey': row_key,
            'link': link,
            'timestamp': timestamp
        })

        return entity

    def insert_row_to_table(self, link: str, timestamp: str) -> bool:
        """
        Insert a new row into the table

        Args:
            link: The link to store
            timestamp: The timestamp for the entry

        Returns:
            bool: True if insertion was successful, False otherwise
        """
        try:
            with self._get_table_client() as table_client:
                entity = self._create_entity(link, timestamp)
                table_client.create_entity(entity=entity)

                logging.info(f"Inserted row with RowKey: {entity['RowKey']}")
                return True

        except Exception as e:
            logging.error(f"Error inserting row: {str(e)}")
            return False

        finally:
            # Clear any references
            del entity
            gc.collect()

    def query_entities(self, filter_query: str, batch_size: int = 100) -> Generator[Dict[str, Any], None, None]:
        """
        Query entities with batched processing

        Args:
            filter_query: The filter query to apply
            batch_size: Number of entities to process at once

        Yields:
            Dict[str, Any]: Entity data
        """
        try:
            with self._get_table_client() as table_client:
                entities = table_client.query_entities(
                    filter_query,
                    results_per_page=batch_size
                )

                for entity in entities:
                    # Convert entity to dict and yield only necessary data
                    yield {
                        'link': entity.get('link', ''),
                        'timestamp': entity.get('timestamp', ''),
                        'RowKey': entity.get('RowKey', '')
                    }

                    # Clear entity reference
                    del entity

        except Exception as e:
            logging.error(f"Error querying entities: {str(e)}")
            raise

        finally:
            gc.collect()

    def cleanup(self) -> None:
        """Cleanup resources"""
        try:
            if self._service_client:
                self._service_client.close()
                self._service_client = None
            gc.collect()
        except Exception as e:
            logging.error(f"Error during cleanup: {str(e)}")
