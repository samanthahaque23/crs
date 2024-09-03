import unittest
import json
from app import app  =

class FlaskAPITestCase(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.app = app
        cls.client = cls.app.test_client()
        cls.app.config['TESTING'] = True

    def test_get_top_loved_products(self):
        """Test the /api/top_loved_products endpoint"""
        response = self.client.get('/api/top_loved_products')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIsInstance(data, list)
        if len(data) > 0:
            self.assertIn('product_name', data[0])
            self.assertIn('image_link', data[0])
            self.assertIn('brand_name', data[0])
            self.assertIn('price_usd', data[0])
            self.assertIn('loves_count', data[0])

    def test_api_recommend_products_with_name(self):
        """Test the /api/recommend_products endpoint with a product name"""
        response = self.client.post('/api/recommend_products', json={
            'product_name': 'Some Product'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('recommendations', data)
        self.assertIsInstance(data['recommendations'], list)

    def test_api_recommend_products_with_skin_and_category(self):
        """Test the /api/recommend_products endpoint with skin type and category"""
        response = self.client.post('/api/recommend_products', json={
            'skin_type': 'Oily',
            'secondary_category': 'Face'
        })
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('recommendations', data)
        self.assertIsInstance(data['recommendations'], list)

    def test_api_recommend_products_with_missing_data(self):
        """Test the /api/recommend_products endpoint with missing data"""
        response = self.client.post('/api/recommend_products', json={})
        self.assertEqual(response.status_code, 400)
        data = json.loads(response.data)
        self.assertEqual(data['error'], "Please provide either a product name or both skin type and category.")

if __name__ == '__main__':
    unittest.main()
