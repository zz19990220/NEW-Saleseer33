import streamlit as st
import pandas as pd
import os
from pathlib import Path
from dotenv import load_dotenv
import io

# Import custom modules
from inventory.filters import load_inventory, filter_products, get_recommendation_reasons
from llm.handler import parse_query

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="Saleseer AI Product Recommendations",
    page_icon="🛍️",
    layout="wide"
)

# Initialize session state
if "search_history" not in st.session_state:
    st.session_state.search_history = []

if "last_filters" not in st.session_state:
    st.session_state.last_filters = {}

if "inventory_df" not in st.session_state:
    st.session_state.inventory_df = None

if "search_results" not in st.session_state:
    st.session_state.search_results = None


def load_default_inventory():
    """Load the built-in product inventory"""
    try:
        sample_path = "inventory/products.csv"
        if os.path.exists(sample_path):
            df = load_inventory(sample_path)
            
            # Supplement with more demo data if needed
            if len(df) < 30:
                # Add more products with different categories for a richer demo experience
                additional_data = {
                    'id': list(range(len(df) + 1, len(df) + 48)),
                    'name': [
                        'Silver Necklace', 'Gold Bracelet', 'Diamond Earrings', 
                        'Leather Handbag', 'Canvas Tote Bag', 'Designer Clutch',
                        'Navy Blazer', 'Striped Blazer', 'Velvet Blazer',
                        'Silk Blouse', 'Cotton Blouse', 'Linen Blouse',
                        'Wool Cardigan', 'Cotton Cardigan', 'Cashmere Cardigan',
                        'Trench Coat', 'Winter Coat', 'Rain Coat',
                        'Evening Dress', 'Summer Dress', 'Casual Dress',
                        'Cotton Hoodie', 'Zip-up Hoodie', 'Athletic Hoodie',
                        'Leather Jacket', 'Denim Jacket', 'Bomber Jacket',
                        'Wool Sweater', 'Cotton Sweater', 'Cashmere Sweater',
                        'Graphic T-shirt', 'Basic T-shirt', 'Long Sleeve T-shirt',
                        'Skinny Jeans', 'Bootcut Jeans', 'Mom Jeans', 'Boyfriend Jeans',
                        'Mini Skirt', 'Midi Skirt', 'Pleated Skirt', 'A-line Skirt',
                        'Running Shoes', 'Dress Shoes', 'Sandals', 'High Heels', 'Boots', 'Sneakers'
                    ],
                    'description': ['Quality ' + name for name in [
                        'Silver Necklace', 'Gold Bracelet', 'Diamond Earrings', 
                        'Leather Handbag', 'Canvas Tote Bag', 'Designer Clutch',
                        'Navy Blazer', 'Striped Blazer', 'Velvet Blazer',
                        'Silk Blouse', 'Cotton Blouse', 'Linen Blouse',
                        'Wool Cardigan', 'Cotton Cardigan', 'Cashmere Cardigan',
                        'Trench Coat', 'Winter Coat', 'Rain Coat',
                        'Evening Dress', 'Summer Dress', 'Casual Dress',
                        'Cotton Hoodie', 'Zip-up Hoodie', 'Athletic Hoodie',
                        'Leather Jacket', 'Denim Jacket', 'Bomber Jacket',
                        'Wool Sweater', 'Cotton Sweater', 'Cashmere Sweater',
                        'Graphic T-shirt', 'Basic T-shirt', 'Long Sleeve T-shirt',
                        'Skinny Jeans', 'Bootcut Jeans', 'Mom Jeans', 'Boyfriend Jeans',
                        'Mini Skirt', 'Midi Skirt', 'Pleated Skirt', 'A-line Skirt',
                        'Running Shoes', 'Dress Shoes', 'Sandals', 'High Heels', 'Boots', 'Sneakers'
                    ]],
                    'price': [
                        45.99, 89.99, 199.99, 
                        149.99, 39.99, 99.99,
                        129.99, 119.99, 159.99,
                        79.99, 49.99, 69.99,
                        89.99, 59.99, 149.99,
                        159.99, 199.99, 129.99,
                        189.99, 79.99, 59.99,
                        49.99, 59.99, 69.99,
                        199.99, 89.99, 99.99,
                        89.99, 49.99, 179.99,
                        29.99, 25.99, 34.99,
                        79.99, 69.99, 89.99, 74.99,
                        49.99, 59.99, 69.99, 54.99,
                        89.99, 129.99, 49.99, 79.99, 139.99, 99.99
                    ],
                    'color': [
                        'silver', 'gold', 'silver', 
                        'black', 'beige', 'red',
                        'blue', 'blue', 'black',
                        'white', 'blue', 'white',
                        'gray', 'green', 'beige',
                        'beige', 'black', 'blue',
                        'black', 'red', 'blue',
                        'black', 'gray', 'blue',
                        'brown', 'blue', 'black',
                        'gray', 'white', 'beige',
                        'black', 'white', 'gray',
                        'blue', 'blue', 'blue', 'blue',
                        'black', 'blue', 'gray', 'red',
                        'white', 'black', 'brown', 'red', 'black', 'white'
                    ],
                    'category': [
                        'accessory', 'accessory', 'accessory',
                        'bag', 'bag', 'bag',
                        'blazer', 'blazer', 'blazer',
                        'blouse', 'blouse', 'blouse',
                        'cardigan', 'cardigan', 'cardigan',
                        'coat', 'coat', 'coat',
                        'dress', 'dress', 'dress',
                        'hoodie', 'hoodie', 'hoodie',
                        'jacket', 'jacket', 'jacket',
                        'sweater', 'sweater', 'sweater',
                        'tshirt', 'tshirt', 'tshirt',
                        'jeans', 'jeans', 'jeans', 'jeans',
                        'skirt', 'skirt', 'skirt', 'skirt',
                        'shoes', 'shoes', 'shoes', 'shoes', 'shoes', 'shoes'
                    ],
                    'rating': [
                        4.2, 4.5, 4.8,
                        4.6, 4.2, 4.5,
                        4.3, 4.1, 4.7,
                        4.4, 4.0, 4.2,
                        4.4, 4.1, 4.8,
                        4.5, 4.7, 4.3,
                        4.8, 4.4, 4.2,
                        4.1, 4.3, 4.5,
                        4.6, 4.2, 4.4,
                        4.3, 4.1, 4.9,
                        4.0, 4.1, 4.2,
                        4.5, 4.3, 4.6, 4.4,
                        4.2, 4.5, 4.3, 4.6,
                        4.7, 4.5, 4.2, 4.6, 4.8, 4.3
                    ],
                    'image_url': ['https://images.unsplash.com/photo-1551298118-6c4d1a86e257'] * 47
                }
                additional_df = pd.DataFrame(additional_data)
                df = pd.concat([df, additional_df], ignore_index=True)
            
            return df
    except Exception as e:
        st.error(f"Error loading inventory: {e}")
    
    return None


def show_inventory_overview():
    """Display inventory statistics in the sidebar"""
    if st.session_state.inventory_df is not None:
        df = st.session_state.inventory_df
        
        st.sidebar.markdown("# 📊 Inventory Overview")
        
        # Total Products
        st.sidebar.markdown("### Total Products")
        st.sidebar.markdown(f"## {len(df)}")
        
        # Average Rating
        if 'rating' in df.columns:
            avg_rating = df['rating'].mean()
            st.sidebar.markdown("### Average Rating")
            st.sidebar.markdown(f"## {avg_rating:.1f}/5")
        
        # Price Range
        if 'price' in df.columns:
            min_price = df['price'].min()
            max_price = df['price'].max()
            st.sidebar.markdown("### Price Range")
            st.sidebar.markdown(f"## ${min_price:.0f} - ${max_price:.0f}")
        
        # Available Categories
        if 'category' in df.columns:
            categories = sorted(df['category'].unique())
            st.sidebar.markdown("### Available Categories")
            for cat in categories:
                st.sidebar.markdown(f"• {cat.title()}")


def process_search_query(query):
    """Process the search query and return filtered results"""
    if st.session_state.inventory_df is None:
        st.error("Inventory data not loaded. Please try again.")
        return None
    
    try:
        # Parse query using LLM
        filters = parse_query(query)
        
        if not filters:
            st.warning("I couldn't understand your request. Please try specifying product type, color, or price range more clearly.")
            return None
        
        st.session_state.last_filters = filters
        
        # Filter products
        filtered_df = filter_products(st.session_state.inventory_df, filters)
        
        if len(filtered_df) == 0:
            st.warning(f"No products found matching your criteria: {filters}")
            return None
        
        # Generate product cards for display
        product_cards = []
        for _, row in filtered_df.iterrows():
            product = row.to_dict()
            reason = get_recommendation_reasons(product, filters)
            
            product_cards.append({
                "id": product.get('id', 0),
                "name": product.get('name', 'Unknown Product'),
                "price": product.get('price', 0),
                "image_url": product.get('image_url', ''),
                "reason": reason,
                "color": product.get('color', 'N/A'),
                "category": product.get('category', 'N/A'),
                "rating": product.get('rating', 0)
            })
        
        return product_cards
    
    except Exception as e:
        st.error(f"Error processing your search: {e}")
        return None


def display_search_results(products):
    """Display product search results in a grid layout"""
    if not products:
        return
    
    # Display results in a 3-column grid
    cols = st.columns(3)
    
    for i, product in enumerate(products):
        with cols[i % 3]:
            # Container for each product
            with st.container():
                # Image
                if product.get("image_url"):
                    try:
                        st.image(product["image_url"], use_column_width=True)
                    except:
                        st.error("Image not available")
                
                # Product details
                st.markdown(f"### {product['name']}")
                st.markdown(f"**${product['price']:.2f}** • {product.get('color', 'N/A').title()} • {product.get('rating', 0)} ⭐")
                st.info(f"**Why this matches**: {product['reason']}")


def main():
    # Load inventory if not already loaded
    if st.session_state.inventory_df is None:
        st.session_state.inventory_df = load_default_inventory()
    
    # Show inventory overview in sidebar
    show_inventory_overview()
    
    # Main content area
    st.markdown("# 🛍️ Saleseer AI Product Recommendations")
    st.markdown("## Find products using natural language!")
    st.markdown("Try queries like: 'Show me red dresses under $200' or 'I want blue jeans'")
    
    # Search interface
    st.markdown("## 🔍 Search Products")
    
    # Create a search form
    col1, col2 = st.columns([5, 1])
    
    with col1:
        search_query = st.text_input(
            "What are you looking for?", 
            placeholder="e.g., Show me red dresses under $200"
        )
    
    with col2:
        search_button = st.button("🔍 Search", type="primary")
    
    # Process search when button clicked
    if search_button and search_query:
        with st.spinner("Searching products..."):
            results = process_search_query(search_query)
            if results:
                st.session_state.search_results = results
                # Save to search history
                st.session_state.search_history.append({
                    "query": search_query,
                    "filters": st.session_state.last_filters,
                    "results_count": len(results)
                })
    
    # Display search results
    if st.session_state.search_results:
        st.markdown(f"### Found {len(st.session_state.search_results)} matching products")
        display_search_results(st.session_state.search_results)


if __name__ == "__main__":
    main() 