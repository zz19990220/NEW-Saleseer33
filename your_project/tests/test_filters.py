import unittest
import pandas as pd
import sys
import os
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.append(str(project_root))

# Import the functions to test
from inventory.filters import filter_products, get_recommendation_reasons


class TestFilters(unittest.TestCase):
    
    def setUp(self):
        # Create a sample DataFrame for testing
        self.df = pd.DataFrame({
            'id': [1, 2, 3, 4],
            'name': ['Red Dress', 'Blue Jeans', 'Black Jacket', 'Green Shirt'],
            'description': ['A beautiful dress', 'Classic jeans', 'Stylish jacket', 'Casual shirt'],
            'price': [150.0, 80.0, 250.0, 30.0],
            'color': ['red', 'blue', 'black', 'green'],
            'category': ['dress', 'pants', 'jacket', 'shirt'],
            'rating': [4.5, 4.2, 4.8, 3.9]
        })
    
    def test_filter_by_category(self):
        filters = {'category': 'dress'}
        filtered = filter_products(self.df, filters)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered.iloc[0]['name'], 'Red Dress')
    
    def test_filter_by_color(self):
        filters = {'color': 'blue'}
        filtered = filter_products(self.df, filters)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered.iloc[0]['name'], 'Blue Jeans')
    
    def test_filter_by_price_range(self):
        filters = {'price_min': 75.0, 'price_max': 200.0}
        filtered = filter_products(self.df, filters)
        self.assertEqual(len(filtered), 2)
        self.assertTrue('Red Dress' in filtered['name'].values)
        self.assertTrue('Blue Jeans' in filtered['name'].values)
    
    def test_filter_by_rating(self):
        filters = {'min_rating': 4.5}
        filtered = filter_products(self.df, filters)
        self.assertEqual(len(filtered), 2)
        self.assertTrue('Red Dress' in filtered['name'].values)
        self.assertTrue('Black Jacket' in filtered['name'].values)
    
    def test_multiple_filters(self):
        filters = {'color': 'red', 'price_max': 200.0}
        filtered = filter_products(self.df, filters)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered.iloc[0]['name'], 'Red Dress')
    
    def test_recommendation_reasons(self):
        product = {
            'price': 150.0, 
            'color': 'red', 
            'category': 'dress', 
            'rating': 4.5
        }
        
        # Test price reason
        filters = {'price_max': 200.0}
        reason = get_recommendation_reasons(product, filters)
        self.assertIn('under your budget', reason)
        
        # Test rating reason
        filters = {}
        reason = get_recommendation_reasons(product, filters)
        self.assertIn('highly rated', reason)
        
        # Test multiple reasons
        filters = {'price_max': 200.0, 'color': 'red'}
        reason = get_recommendation_reasons(product, filters)
        self.assertIn('budget', reason)
        self.assertIn('color preference', reason)


if __name__ == '__main__':
    unittest.main() 