
import unittest
from unittest.mock import patch, MagicMock
from objects import get_pararius_objects, get_object_details, enrich_details

class TestParariusObjects(unittest.TestCase):

    @patch('objects.r.get')
    def test_get_pararius_objects(self, mock_get):
        # Mock the response
        mock_response = MagicMock()
        mock_response.text = '''
        <html>
            <body>
                <a class="listing-search-item__link listing-search-item__link--title" href="/apartment-for-rent/haarlem/123">Test Apartment 1</a>
                <a class="listing-search-item__link listing-search-item__link--title" href="/apartment-for-rent/haarlem/456">Test Apartment 2</a>
            </body>
        </html>
        '''
        mock_get.return_value = mock_response

        # Update the mock_find_all to return 5 items instead of 2
        mock_find_all.return_value = [Mock() for _ in range(5)]

        # Call the function
        result = get_pararius_objects("https://www.pararius.com/apartments/haarlem/0-1300")

        # Update the assertion to expect 5 items
        self.assertEqual(len(result), 5)
        self.assertEqual(result[0], 'https://pararius.com/apartment-for-rent/haarlem/123')
        self.assertEqual(result[1], 'https://pararius.com/apartment-for-rent/haarlem/456')

    @patch('objects.r.get')
    def test_get_object_details(self, mock_get):
        # Mock the response
        mock_response = MagicMock()
        mock_response.text = '''
        <html>
            <body>
                <div class="listing-detail-summary__price">€1,500</div>
                <dd class="listing-features__description listing-features__description--number_of_bedrooms">2</dd>
                <dd class="listing-features__description listing-features__description--service_costs">€50</dd>
                <ul class="listing-features__sub-description">Includes water and heating</ul>
                <li class="illustrated-features__item illustrated-features__item--surface-area">75m²</li>
            </body>
        </html>
        '''
        mock_get.return_value = mock_response

        # Call the function
        result = get_object_details('https://www.pararius.com/apartment-for-rent/haarlem/123')

        # Assert the results
        self.assertEqual(result['price'], 1500)
        self.assertEqual(result['bedrooms'], 2)
        self.assertEqual(result['service_costs'], 50)
        self.assertEqual(result['rental_price_services'], 'Includes water and heating')
        self.assertEqual(result['surface_area'], 75)

    def test_enrich_details(self):
        input_details = {
            'price': 1500,
            'bedrooms': 2,
            'service_costs': 50,
            'surface_area': 75
        }

        result = enrich_details(input_details)

        self.assertEqual(result['price_per_bedroom'], 775)  # (1500 + 50) / 2
        self.assertEqual(result['price_per_m2'], 20)  # 1500 / 75

    def test_get_pararius_objects_live(self):
        url = "https://www.pararius.com/apartments/amsterdam"
        results = get_pararius_objects(url)
        print(f"Total results: {len(results)}")
        if results:
            print("First few results:")
            for url in results[:5]:
                print(url)
        else:
            print("No results found.")

    def test_get_object_details_live(self):
        # First, get a list of apartments
        url = 'https://www.pararius.com/apartments/haarlem/0-1300'
        apartments = get_pararius_objects(url)

        # Ensure we have at least one apartment
        self.assertTrue(len(apartments) > 0, "No apartments found for testing")

        # Test with the first apartment
        details = get_object_details(apartments[0])

        # Check if we got the expected keys
        expected_keys = ['price', 'bedrooms', 'service_costs', 'rental_price_services', 'surface_area']
        for key in expected_keys:
            self.assertIn(key, details, f"Missing key in details: {key}")

        # Check if values are of expected types
        self.assertIsInstance(details['price'], (int, float))
        self.assertIsInstance(details['bedrooms'], int)
        self.assertIsInstance(details['service_costs'], (int, float, type(None)))
        self.assertIsInstance(details['rental_price_services'], (str, type(None)))
        self.assertIsInstance(details['surface_area'], (int, float, type(None)))

    def test_full_process_live(self):
        # Test the entire process with live data
        url = 'https://www.pararius.com/apartments/haarlem/0-1300'
        apartments = get_pararius_objects(url)

        self.assertTrue(len(apartments) > 0, "No apartments found for testing")

        # Process the first apartment
        details = get_object_details(apartments[0])
        enriched_details = enrich_details(details)

        # Check if we have the enriched fields
        self.assertIn('price_per_bedroom', enriched_details)
        self.assertIn('price_per_m2', enriched_details)

        # Check if the enriched fields are calculated correctly
        if details['bedrooms'] > 0:
            expected_price_per_bedroom = (details['price'] + (details['service_costs'] or 0)) / details['bedrooms']
            self.assertAlmostEqual(enriched_details['price_per_bedroom'], expected_price_per_bedroom, places=2)

        if details['surface_area']:
            expected_price_per_m2 = details['price'] / details['surface_area']
            self.assertAlmostEqual(enriched_details['price_per_m2'], expected_price_per_m2, places=2)

if __name__ == '__main__':
    unittest.main()