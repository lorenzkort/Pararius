import unittest
from unittest.mock import patch, MagicMock
from datetime import datetime
from modules.manage import cronjob

class TestManage(unittest.TestCase):

    @patch('modules.manage.get_pararius_objects')
    @patch('modules.manage.get_object_details')
    @patch('modules.manage.enrich_details')
    @patch('modules.manage.send_text')
    @patch('modules.manage.handler')
    def test_cronjob(self, mock_handler, mock_send_text, mock_enrich_details, mock_get_object_details, mock_get_pararius_objects):
        # Set up mock returns
        mock_get_pararius_objects.return_value = ['https://www.pararius.com/apartment-for-rent/haarlem/1', 'https://www.pararius.com/apartment-for-rent/haarlem/2']
        mock_get_object_details.return_value = {'key': 'value'}
        mock_enrich_details.return_value = {'enriched_key': 'enriched_value'}
        
        mock_table_client = MagicMock()
        mock_table_client.query_entities.return_value = [{'link': 'https://www.pararius.com/apartment-for-rent/haarlem/1'}]
        mock_handler.return_value.table_client = mock_table_client

        # Call the function
        cronjob()

        # Assertions
        mock_get_pararius_objects.assert_called_once_with(url='https://www.pararius.com/apartments/haarlem/1-bedrooms/0-1500/radius-10')
        mock_get_object_details.assert_called_once_with('https://www.pararius.com/apartment-for-rent/haarlem/2')
        mock_enrich_details.assert_called_once_with({'key': 'value'})
        mock_send_text.assert_called_once()
        mock_handler.return_value.insert_row_to_table.assert_called_once()

    @patch('modules.manage.get_pararius_objects')
    @patch('modules.manage.handler')
    def test_cronjob_no_new_objects(self, mock_handler, mock_get_pararius_objects):
        # Set up mock returns
        mock_get_pararius_objects.return_value = ['https://www.pararius.com/apartment-for-rent/haarlem/1']
        
        mock_table_client = MagicMock()
        mock_table_client.query_entities.return_value = [{'link': 'https://www.pararius.com/apartment-for-rent/haarlem/1'}]
        mock_handler.return_value.table_client = mock_table_client

        # Call the function
        cronjob()

        # Assertions
        mock_get_pararius_objects.assert_called_once()
        mock_handler.return_value.insert_row_to_table.assert_not_called()

    @patch('modules.manage.get_pararius_objects')
    def test_cronjob_exception(self, mock_get_pararius_objects):
        # Set up mock to raise an exception
        mock_get_pararius_objects.side_effect = Exception("Test exception")

        # Call the function
        cronjob()

        # Assertion
        mock_get_pararius_objects.assert_called_once()
        # You might want to add additional assertions here to check how the exception is handled

if __name__ == '__main__':
    unittest.main()