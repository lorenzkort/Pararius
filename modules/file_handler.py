from azure.data.tables import TableServiceClient, TableEntity
from contextlib import contextmanager
import os
from dotenv import load_dotenv
class handler():
    # Connect to your Table Storage account
    load_dotenv()
    azure_tables_connection_string = os.getenv('AZURE_TABLES_CONNNECTION_STRING')
    
    @contextmanager
    def table_client_context(self):
        table_service_client = TableServiceClient.from_connection_string(conn_str=self.azure_tables_connection_string)
        client = table_service_client.get_table_client(table_name="links")
        try:
            yield client
        finally:
            client.close()
            table_service_client.close()

    def insert_row_to_table(self, link, timestamp):
        with self.table_client_context() as table_client:
            new_entity = TableEntity()
            new_entity['PartitionKey'] = 'pararius'
            new_entity['RowKey'] = link.split('/')[-2]
            new_entity['link'] = link
            new_entity['timestamp'] = timestamp
            table_client.create_entity(entity=new_entity)
            print(f"Inserted row: {new_entity}")

    def query_entities(self, filter_query):
        with self.table_client_context() as table_client:
            return list(table_client.query_entities(filter_query))