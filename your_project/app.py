import streamlit as st
import pandas as pd
import os
from pathlib import Path
from dotenv import load_dotenv
import io
import logging
import re

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

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

if "search_query" not in st.session_state:
    st.session_state.search_query = None

if "search_summary" not in st.session_state:
    st.session_state.search_summary = None


def create_synthetic_inventory():
    """Create a synthetic inventory dataset when no file is available"""
    logger.info("Creating synthetic inventory data")
    
    # Create synthetic products data
    products_data = {
        'id': list(range(1, 58)),  # 57 products
        'name': [
            'Silver Necklace', 'Gold Bracelet', 'Diamond Earrings', 
            'Leather Handbag', 'Canvas Tote Bag', 'Designer Clutch',
            'Navy Blazer', 'Striped Blazer', 'Velvet Blazer',
            'Silk Blouse', 'Cotton Blouse', 'Linen Blouse',
            'Wool Cardigan', 'Cotton Cardigan', 'Cashmere Cardigan',
            'Trench Coat', 'Winter Coat', 'Rain Coat',
            'Evening Dress', 'Summer Dress', 'Casual Dress', 'Red Cocktail Dress', 'Red Summer Dress',
            'Cotton Hoodie', 'Zip-up Hoodie', 'Athletic Hoodie',
            'Leather Jacket', 'Denim Jacket', 'Bomber Jacket',
            'Wool Sweater', 'Cotton Sweater', 'Cashmere Sweater',
            'Graphic T-shirt', 'Basic T-shirt', 'Long Sleeve T-shirt',
            'Skinny Jeans', 'Bootcut Jeans', 'Mom Jeans', 'Boyfriend Jeans', 'Blue Jeans',
            'Mini Skirt', 'Midi Skirt', 'Pleated Skirt', 'A-line Skirt',
            'Running Shoes', 'Dress Shoes', 'Sandals', 'High Heels', 'Boots', 'Sneakers',
            'White Sneakers', 'Red Heels', 'Brown Leather Boots', 'Casual Loafers',
            'Athletic Socks', 'Wool Socks', 'No-Show Socks'
        ],
        'description': ['Quality ' + name for name in [
            'Silver Necklace', 'Gold Bracelet', 'Diamond Earrings', 
            'Leather Handbag', 'Canvas Tote Bag', 'Designer Clutch',
            'Navy Blazer', 'Striped Blazer', 'Velvet Blazer',
            'Silk Blouse', 'Cotton Blouse', 'Linen Blouse',
            'Wool Cardigan', 'Cotton Cardigan', 'Cashmere Cardigan',
            'Trench Coat', 'Winter Coat', 'Rain Coat',
            'Evening Dress', 'Summer Dress', 'Casual Dress', 'Red Cocktail Dress', 'Red Summer Dress',
            'Cotton Hoodie', 'Zip-up Hoodie', 'Athletic Hoodie',
            'Leather Jacket', 'Denim Jacket', 'Bomber Jacket',
            'Wool Sweater', 'Cotton Sweater', 'Cashmere Sweater',
            'Graphic T-shirt', 'Basic T-shirt', 'Long Sleeve T-shirt',
            'Skinny Jeans', 'Bootcut Jeans', 'Mom Jeans', 'Boyfriend Jeans', 'Blue Jeans',
            'Mini Skirt', 'Midi Skirt', 'Pleated Skirt', 'A-line Skirt',
            'Running Shoes', 'Dress Shoes', 'Sandals', 'High Heels', 'Boots', 'Sneakers',
            'White Sneakers', 'Red Heels', 'Brown Leather Boots', 'Casual Loafers',
            'Athletic Socks', 'Wool Socks', 'No-Show Socks'
        ]],
        'price': [
            45.99, 89.99, 199.99, 
            149.99, 39.99, 99.99,
            129.99, 119.99, 159.99,
            79.99, 49.99, 69.99,
            89.99, 59.99, 149.99,
            159.99, 199.99, 129.99,
            189.99, 79.99, 59.99, 179.99, 149.99,
            49.99, 59.99, 69.99,
            199.99, 89.99, 99.99,
            89.99, 49.99, 179.99,
            29.99, 25.99, 34.99,
            79.99, 69.99, 89.99, 74.99, 89.99,
            49.99, 59.99, 69.99, 54.99,
            89.99, 129.99, 49.99, 79.99, 139.99, 99.99,
            79.99, 189.99, 249.99, 69.99,
            12.99, 19.99, 9.99
        ],
        'color': [
            'silver', 'gold', 'silver', 
            'black', 'beige', 'red',
            'blue', 'blue', 'black',
            'white', 'blue', 'white',
            'gray', 'green', 'beige',
            'beige', 'black', 'blue',
            'black', 'red', 'blue', 'red', 'red',
            'black', 'gray', 'blue',
            'brown', 'blue', 'black',
            'gray', 'white', 'beige',
            'black', 'white', 'gray',
            'blue', 'blue', 'blue', 'blue', 'blue',
            'black', 'blue', 'gray', 'red',
            'white', 'black', 'brown', 'red', 'black', 'white',
            'white', 'red', 'brown', 'brown',
            'black', 'gray', 'white'
        ],
        'category': [
            'accessory', 'accessory', 'accessory',
            'bag', 'bag', 'bag',
            'blazer', 'blazer', 'blazer',
            'blouse', 'blouse', 'blouse',
            'cardigan', 'cardigan', 'cardigan',
            'coat', 'coat', 'coat',
            'dress', 'dress', 'dress', 'dress', 'dress',
            'hoodie', 'hoodie', 'hoodie',
            'jacket', 'jacket', 'jacket',
            'sweater', 'sweater', 'sweater',
            'tshirt', 'tshirt', 'tshirt',
            'jeans', 'jeans', 'jeans', 'jeans', 'jeans',
            'skirt', 'skirt', 'skirt', 'skirt',
            'shoes', 'shoes', 'shoes', 'shoes', 'shoes', 'shoes',
            'shoes', 'shoes', 'shoes', 'shoes',
            'accessory', 'accessory', 'accessory'
        ],
        'rating': [
            4.2, 4.5, 4.8,
            4.6, 4.2, 4.5,
            4.3, 4.1, 4.7,
            4.4, 4.0, 4.2,
            4.4, 4.1, 4.8,
            4.5, 4.7, 4.3,
            4.8, 4.4, 4.2, 4.7, 4.5,
            4.1, 4.3, 4.5,
            4.6, 4.2, 4.4,
            4.3, 4.1, 4.9,
            4.0, 4.1, 4.2,
            4.5, 4.3, 4.6, 4.4, 4.2,
            4.2, 4.5, 4.3, 4.6,
            4.7, 4.5, 4.2, 4.6, 4.8, 4.3,
            4.3, 4.7, 4.6, 4.4,
            3.9, 4.2, 4.0
        ],
        'image_url': [
            'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f',  # necklace
            'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f',  # bracelet
            'https://images.unsplash.com/photo-1599643478518-a784e5dc4c8f',  # earrings
            'https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d',  # handbag
            'https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d',  # tote
            'https://images.unsplash.com/photo-1566150905458-1bf1fc113f0d',  # clutch
            'https://images.unsplash.com/photo-1594938298603-c8148c4dae35',  # blazer
            'https://images.unsplash.com/photo-1594938298603-c8148c4dae35',  # blazer
            'https://images.unsplash.com/photo-1594938298603-c8148c4dae35',  # blazer
            'https://images.unsplash.com/photo-1564257631407-4deb1f99d992',  # blouse
            'https://images.unsplash.com/photo-1564257631407-4deb1f99d992',  # blouse
            'https://images.unsplash.com/photo-1564257631407-4deb1f99d992',  # blouse
            'https://images.unsplash.com/photo-1616677307286-b79e6b4a0983',  # cardigan
            'https://images.unsplash.com/photo-1616677307286-b79e6b4a0983',  # cardigan
            'https://images.unsplash.com/photo-1616677307286-b79e6b4a0983',  # cardigan
            'https://images.unsplash.com/photo-1551028719-00167b16eac5',  # coat
            'https://images.unsplash.com/photo-1551028719-00167b16eac5',  # coat
            'https://images.unsplash.com/photo-1551028719-00167b16eac5',  # coat
            'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1',  # dress
            'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1',  # dress
            'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1',  # dress
            'https://images.unsplash.com/photo-1562699729-c7f9a8f55064',  # dress
            'https://images.unsplash.com/photo-1572804013309-59a88b7e92f1',  # dress
            'https://images.unsplash.com/photo-1620799140188-3b2a02fd9a77',  # hoodie
            'https://images.unsplash.com/photo-1620799140188-3b2a02fd9a77',  # hoodie
            'https://images.unsplash.com/photo-1620799140188-3b2a02fd9a77',  # hoodie
            'https://images.unsplash.com/photo-1551028719-00167b16eac5',  # jacket
            'https://images.unsplash.com/photo-1551028719-00167b16eac5',  # jacket
            'https://images.unsplash.com/photo-1551028719-00167b16eac5',  # jacket
            'https://images.unsplash.com/photo-1616677307286-b79e6b4a0983',  # sweater
            'https://images.unsplash.com/photo-1616677307286-b79e6b4a0983',  # sweater
            'https://images.unsplash.com/photo-1616677307286-b79e6b4a0983',  # sweater
            'https://images.unsplash.com/photo-1576566588028-4147f3842f27',  # tshirt
            'https://images.unsplash.com/photo-1576566588028-4147f3842f27',  # tshirt
            'https://images.unsplash.com/photo-1576566588028-4147f3842f27',  # tshirt
            'https://images.unsplash.com/photo-1541099649105-f69ad21f3246',  # jeans
            'https://images.unsplash.com/photo-1541099649105-f69ad21f3246',  # jeans
            'https://images.unsplash.com/photo-1541099649105-f69ad21f3246',  # jeans
            'https://images.unsplash.com/photo-1541099649105-f69ad21f3246',  # jeans
            'https://images.unsplash.com/photo-1541099649105-f69ad21f3246',  # jeans
            'https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa',  # skirt
            'https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa',  # skirt
            'https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa',  # skirt
            'https://images.unsplash.com/photo-1583496661160-fb5886a0aaaa',  # skirt
            'https://images.unsplash.com/photo-1607522370275-f14206abe5d3',  # shoes
            'https://images.unsplash.com/photo-1607522370275-f14206abe5d3',  # shoes
            'https://images.unsplash.com/photo-1607522370275-f14206abe5d3',  # shoes
            'https://images.unsplash.com/photo-1543163521-1bf539c55dd2',  # shoes
            'https://images.unsplash.com/photo-1542838687-307f8d662565',  # shoes
            'https://images.unsplash.com/photo-1607522370275-f14206abe5d3',  # shoes
            'https://images.unsplash.com/photo-1607522370275-f14206abe5d3',  # shoes
            'https://images.unsplash.com/photo-1543163521-1bf539c55dd2',  # shoes
            'https://images.unsplash.com/photo-1542838687-307f8d662565',  # shoes
            'https://images.unsplash.com/photo-1607522370275-f14206abe5d3',  # shoes
            'https://images.unsplash.com/photo-1586350977771-2a1dc0c8ee2d',  # socks
            'https://images.unsplash.com/photo-1586350977771-2a1dc0c8ee2d',  # socks
            'https://images.unsplash.com/photo-1586350977771-2a1dc0c8ee2d'   # socks
        ],
    }
    
    return pd.DataFrame(products_data)


def load_default_inventory():
    """Load the built-in product inventory"""
    try:
        logger.info("Attempting to load inventory data")
        sample_path = "inventory/products.csv"
        
        if os.path.exists(sample_path):
            logger.info(f"Found inventory file: {sample_path}")
            df = load_inventory(sample_path)
            
            # If the loaded data is too small, supplement with synthetic data
            if len(df) < 30:
                logger.info("Sample data too small, supplementing with synthetic data")
                synthetic_df = create_synthetic_inventory()
                df = pd.concat([df, synthetic_df], ignore_index=True)
                df = df.drop_duplicates(subset=['name', 'category', 'color'], keep='first')
            
            logger.info(f"Successfully loaded inventory with {len(df)} products")
            return df
        else:
            # If no file exists, create synthetic data
            logger.warning(f"Inventory file not found: {sample_path}")
            logger.info("Creating synthetic inventory as fallback")
            return create_synthetic_inventory()
            
    except Exception as e:
        logger.error(f"Error loading inventory: {e}")
        logger.info("Falling back to synthetic inventory data")
        # Always provide data even if there's an error
        return create_synthetic_inventory()


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


def handle_simple_search(query):
    """
    Handle simple keyword searches by inferring filters from basic terms
    Returns a dictionary with inferred filters
    """
    query = query.strip().lower()
    
    # Check if the query is just a single category name
    categories = ['accessory', 'bag', 'blazer', 'blouse', 'cardigan', 'coat', 
                  'dress', 'hoodie', 'jacket', 'jeans', 'shoes', 'skirt', 
                  'sweater', 'tshirt', 'socks']
    
    # Handle plural forms by removing trailing 's'
    search_term = query.rstrip('s')
    
    # Check for exact category match
    if search_term in categories:
        logger.info(f"Simple search matched category: {search_term}")
        return {"category": search_term}
    
    # Check for partial category match
    for category in categories:
        if search_term in category or category in search_term:
            logger.info(f"Simple search partially matched category: {category}")
            return {"category": category}
    
    # Check for color matches
    colors = ['red', 'blue', 'green', 'black', 'white', 'pink', 
              'purple', 'yellow', 'orange', 'brown', 'gray', 'beige']
    
    for color in colors:
        if color in query:
            logger.info(f"Simple search matched color: {color}")
            return {"color": color}
    
    # Try to extract price information
    price_pattern = r'under\s*\$?(\d+)'
    match = re.search(price_pattern, query)
    if match:
        price = float(match.group(1))
        logger.info(f"Simple search matched price under: ${price}")
        return {"price_max": price}
    
    # If nothing matches, return None to indicate the basic search failed
    return None


def process_search_query(query):
    """Process the search query and return filtered results"""
    try:
        # Ensure inventory is loaded
        if st.session_state.inventory_df is None:
            logger.warning("Inventory data not loaded when attempting search")
            # Try to load default inventory as a fallback
            st.session_state.inventory_df = load_default_inventory()
            
            # If still None, show error and return
            if st.session_state.inventory_df is None:
                st.error("Inventory data not loaded. Please try again.")
                return None
        
        # First try to handle as a simple keyword search
        simple_filters = handle_simple_search(query)
        
        # If simple search returned filters, use those
        if simple_filters:
            filters = simple_filters
            st.session_state.search_summary = f"Searching for: Category: {filters.get('category', '')}{filters.get('color', '')}"
            logger.info(f"Using simple search filters: {filters}")
        else:
            # Otherwise try the LLM for natural language understanding
            filters = parse_query(query)
            
            if not filters:
                st.warning("I couldn't understand your request. Please try specifying product type, color, or price range more clearly.")
                return None
        
        st.session_state.last_filters = filters
        
        # Filter products
        filtered_df = filter_products(st.session_state.inventory_df, filters)
        
        if len(filtered_df) == 0:
            st.warning(f"No products found matching your criteria.")
            return None
        
        # Create search summary for display
        create_search_insight(filtered_df, filters)
        
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
        logger.exception(f"Error processing search query: {e}")
        st.error(f"Error processing your search: {e}")
        return None


def create_search_insight(filtered_df, filters):
    """Create search insight summary based on filtered results"""
    if filtered_df is None or len(filtered_df) == 0:
        return
    
    # Get the key filter used for search
    primary_filter = ""
    if 'category' in filters and filters['category']:
        primary_filter = f"in {filters['category']}s."
    elif 'color' in filters and filters['color']:
        primary_filter = f"in {filters['color']} color."
    
    # Get price range of found items
    min_price = filtered_df['price'].min()
    max_price = filtered_df['price'].max()
    price_range = f"Price range: ${min_price:.2f} - ${max_price:.2f}."
    
    # Check ratings
    avg_rating = filtered_df['rating'].mean()
    rating_text = ""
    if avg_rating >= 4.5:
        rating_text = "All items have excellent ratings."
    elif avg_rating >= 4.0:
        rating_text = "Items have very good ratings."
    else:
        rating_text = f"Average rating: {avg_rating:.1f}."
    
    # Generate the complete insight
    st.session_state.search_summary = {
        "count": len(filtered_df),
        "primary_filter": primary_filter,
        "rating_text": rating_text,
        "price_range": price_range
    }


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
        # Log inventory loading status
        if st.session_state.inventory_df is not None:
            logger.info(f"Loaded inventory with {len(st.session_state.inventory_df)} products")
        else:
            logger.error("Failed to load inventory")
    
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
            placeholder="e.g., Show me red dresses under $200",
            key="search_input"
        )
    
    with col2:
        search_button = st.button("🔍 Search", type="primary")
    
    # Process search when button clicked
    if search_button and search_query:
        with st.spinner("Searching products..."):
            st.session_state.search_query = search_query
            results = process_search_query(search_query)
            if results:
                st.session_state.search_results = results
                # Save to search history
                st.session_state.search_history.append({
                    "query": search_query,
                    "filters": st.session_state.last_filters,
                    "results_count": len(results)
                })
    
    # Display search summary if available
    if st.session_state.search_query:
        if isinstance(st.session_state.search_summary, str):
            # If it's a simple string search summary
            st.info(f"🎯 {st.session_state.search_summary}")
        elif isinstance(st.session_state.search_summary, dict):
            # If it's a detailed search insight
            with st.container():
                st.markdown("""
                <style>
                .search-insight {
                    background-color: #e8f4f9;
                    border-left: 5px solid #4e8cff;
                    padding: 15px;
                    border-radius: 5px;
                    margin: 10px 0;
                }
                </style>
                """, unsafe_allow_html=True)
                
                insight = st.session_state.search_summary
                st.markdown(f"""
                <div class="search-insight">
                <h4>🎯 Searching for: {st.session_state.last_filters}</h4>
                </div>
                """, unsafe_allow_html=True)
                
                st.markdown(f"""
                <div class="search-insight">
                <h4>💡 Recommendation Insight:</h4>
                <p>Found {insight["count"]} items {insight["primary_filter"]} {insight["rating_text"]} {insight["price_range"]}</p>
                </div>
                """, unsafe_allow_html=True)
    
    # Display search results
    if st.session_state.search_results:
        st.markdown(f"## 🎯 Found {len(st.session_state.search_results)} Products")
        display_search_results(st.session_state.search_results)


if __name__ == "__main__":
    main() 