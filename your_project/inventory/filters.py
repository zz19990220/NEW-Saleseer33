import pandas as pd
import os
from typing import Dict, List, Any, Optional

def load_inventory(file_path: str) -> pd.DataFrame:
    """
    Load product inventory from CSV or Excel file
    """
    _, ext = os.path.splitext(file_path)
    
    if ext.lower() == '.csv':
        return pd.read_csv(file_path)
    elif ext.lower() in ['.xlsx', '.xls']:
        return pd.read_excel(file_path)
    else:
        raise ValueError(f"Unsupported file format: {ext}")

def filter_products(df: pd.DataFrame, filters: Dict[str, Any]) -> pd.DataFrame:
    """
    Filter products based on specified criteria
    
    Parameters:
    - df: DataFrame containing product data
    - filters: Dictionary of filter conditions
      - category: str or list - product category
      - color: str or list - product color
      - price_min: float - minimum price
      - price_max: float - maximum price
      - min_rating: float - minimum rating score
    
    Returns:
    - Filtered DataFrame
    """
    filtered_df = df.copy()
    
    # Filter by category
    if 'category' in filters and filters['category']:
        categories = filters['category'] if isinstance(filters['category'], list) else [filters['category']]
        filtered_df = filtered_df[filtered_df['category'].str.lower().isin([c.lower() for c in categories])]
    
    # Filter by color
    if 'color' in filters and filters['color']:
        colors = filters['color'] if isinstance(filters['color'], list) else [filters['color']]
        filtered_df = filtered_df[filtered_df['color'].str.lower().isin([c.lower() for c in colors])]
    
    # Filter by price range
    if 'price_min' in filters and filters['price_min'] is not None:
        filtered_df = filtered_df[filtered_df['price'] >= filters['price_min']]
    
    if 'price_max' in filters and filters['price_max'] is not None:
        filtered_df = filtered_df[filtered_df['price'] <= filters['price_max']]
    
    # Filter by minimum rating
    if 'min_rating' in filters and filters['min_rating'] is not None:
        filtered_df = filtered_df[filtered_df['rating'] >= filters['min_rating']]
    
    return filtered_df

def get_recommendation_reasons(product: Dict, filters: Dict[str, Any]) -> str:
    """
    Generate recommendation explanations based on filters and product attributes
    """
    reasons = []
    
    # Price-based reasons
    if 'price_max' in filters and filters['price_max']:
        if product['price'] <= filters['price_max'] * 0.8:
            reasons.append("well under your budget")
        elif product['price'] <= filters['price_max']:
            reasons.append("fits your budget")
    
    # Rating-based reasons
    if product['rating'] >= 4.5:
        reasons.append("highly rated")
    elif product['rating'] >= 4.0:
        reasons.append("well-rated")
    
    # Color match
    if 'color' in filters and filters['color'] and product['color'].lower() in [c.lower() for c in (filters['color'] if isinstance(filters['color'], list) else [filters['color']])]:
        reasons.append(f"matches your {product['color']} color preference")
    
    # Category match
    if 'category' in filters and filters['category'] and product['category'].lower() in [c.lower() for c in (filters['category'] if isinstance(filters['category'], list) else [filters['category']])]:
        reasons.append(f"in your requested {product['category']} category")
    
    if not reasons:
        return "matches your search criteria"
    
    if len(reasons) == 1:
        return reasons[0]
    elif len(reasons) == 2:
        return f"{reasons[0]} and {reasons[1]}"
    else:
        return f"{', '.join(reasons[:-1])}, and {reasons[-1]}" 