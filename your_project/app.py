import streamlit as st
import pandas as pd
import os
from pathlib import Path
from dotenv import load_dotenv
import time
import io

# Import custom modules
from inventory.filters import load_inventory, filter_products, get_recommendation_reasons
from llm.handler import parse_query

# Load environment variables
load_dotenv()

# Set page config
st.set_page_config(
    page_title="AI Product Recommender",
    page_icon="🛍️",
    layout="wide"
)

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_filters" not in st.session_state:
    st.session_state.last_filters = {}

if "inventory_df" not in st.session_state:
    st.session_state.inventory_df = None

if "using_sample_data" not in st.session_state:
    st.session_state.using_sample_data = False


def main():
    # Header
    st.title("🛍️ AI Product Recommender")
    st.markdown("### Find products with natural language")
    
    # Sidebar
    with st.sidebar:
        st.header("About")
        st.markdown("""
        This app uses AI to understand your product needs and recommend items from our inventory.
        
        Try queries like:
        - "Show me red dresses under $200"
        - "I need comfortable shoes"
        - "Find blue jackets with good ratings"
        """)
        
        # Data source selection
        st.subheader("Data Source")
        
        # File uploader for custom inventory
        uploaded_file = st.file_uploader("Upload your inventory (CSV or Excel)", type=['csv', 'xlsx'])
        
        # Handle file upload
        if uploaded_file is not None:
            try:
                # Get file extension
                file_ext = Path(uploaded_file.name).suffix.lower()
                
                if file_ext == '.csv':
                    st.session_state.inventory_df = pd.read_csv(uploaded_file)
                elif file_ext in ['.xlsx', '.xls']:
                    st.session_state.inventory_df = pd.read_excel(uploaded_file)
                
                st.session_state.using_sample_data = False
                st.success(f"✅ Inventory uploaded: {uploaded_file.name}")
            except Exception as e:
                st.error(f"❌ Error loading file: {e}")
                st.session_state.inventory_df = None
        
        # Option to use sample data
        if st.button("Use Sample Inventory Data") or (st.session_state.inventory_df is None and not st.session_state.using_sample_data):
            try:
                sample_path = "inventory/products.csv"
                if os.path.exists(sample_path):
                    st.session_state.inventory_df = load_inventory(sample_path)
                    st.session_state.using_sample_data = True
                    st.success(f"✅ Using sample inventory ({len(st.session_state.inventory_df)} products)")
                else:
                    st.warning("⚠️ Sample inventory file not found. Please upload a file.")
                    st.session_state.inventory_df = None
            except Exception as e:
                st.error(f"❌ Error loading sample inventory: {e}")
                st.session_state.inventory_df = None
        
        # Display inventory stats if available
        if st.session_state.inventory_df is not None:
            df = st.session_state.inventory_df
            st.markdown("#### Inventory Statistics")
            st.write(f"**Total Products:** {len(df)}")
            
            if 'category' in df.columns:
                categories = df['category'].unique()
                st.write(f"**Categories:** {', '.join(categories[:5])}" + ("..." if len(categories) > 5 else ""))
            
            if 'color' in df.columns:
                colors = df['color'].unique()
                st.write(f"**Colors:** {', '.join(colors[:5])}" + ("..." if len(colors) > 5 else ""))
            
            if 'price' in df.columns:
                st.write(f"**Price range:** ${df['price'].min():.2f} - ${df['price'].max():.2f}")
    
    # Display chat history
    display_chat_history()
    
    # Show a placeholder message if no inventory is loaded
    if st.session_state.inventory_df is None:
        st.info("Please upload an inventory file or use the sample inventory to get started.")
    
    # Chat input
    user_query = st.chat_input("What kind of product are you looking for?", disabled=st.session_state.inventory_df is None)
    
    # Process query when submitted
    if user_query and st.session_state.inventory_df is not None:
        process_query(user_query, st.session_state.inventory_df)


def process_query(user_query, df):
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    
    # Processing message
    with st.chat_message("assistant"):
        with st.status("Processing your request...", expanded=True) as status:
            try:
                st.write("Analyzing your query...")
                
                # Parse query using LLM
                filters = parse_query(user_query)
                st.session_state.last_filters = filters
                
                if not filters:
                    status.update(label="⚠️ Couldn't parse your query. Please try again.", state="error")
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": "I couldn't understand your request. Please try specifying product type, color, or price range more clearly."
                    })
                    return
                
                st.write(f"✅ Query understood: {filters}")
                status.update(label="Finding matching products...", state="running")
                
                # Filter products
                filtered_df = filter_products(df, filters)
                st.write(f"Found {len(filtered_df)} matching products")
                
                if len(filtered_df) == 0:
                    status.update(label="No matching products found", state="complete")
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": f"I couldn't find any products matching your criteria: {filters}. Please try a different query."
                    })
                    return
                
                status.update(label="Generating recommendations...", state="running")
                
                # Generate product card display
                product_cards = generate_product_cards(filtered_df, filters)
                
                # Add recommendations to chat history
                filter_summary = get_filter_summary(filters)
                recommendation_message = f"Here are {len(filtered_df)} products {filter_summary}:"
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": recommendation_message,
                    "products": product_cards
                })
                
                status.update(label="✅ Recommendations ready!", state="complete")
            
            except Exception as e:
                status.update(label=f"❌ Error: {str(e)}", state="error")
                st.session_state.chat_history.append({
                    "role": "assistant", 
                    "content": f"Sorry, I encountered an error: {str(e)}"
                })


def get_filter_summary(filters):
    """Generate a human-readable summary of the filters"""
    parts = []
    
    if 'category' in filters and filters['category']:
        parts.append(f"in the {filters['category']} category")
    
    if 'color' in filters and filters['color']:
        parts.append(f"in {filters['color']} color")
    
    if 'price_max' in filters and filters['price_max']:
        parts.append(f"under ${filters['price_max']}")
    
    if 'price_min' in filters and filters['price_min']:
        parts.append(f"over ${filters['price_min']}")
    
    if 'min_rating' in filters and filters['min_rating']:
        parts.append(f"with at least {filters['min_rating']} stars")
    
    if parts:
        return " ".join(parts)
    return ""


def generate_product_cards(df, filters):
    """Convert DataFrame rows to list of product cards"""
    product_cards = []
    
    for _, row in df.iterrows():
        product = row.to_dict()
        reason = get_recommendation_reasons(product, filters)
        
        product_cards.append({
            "id": product['id'] if 'id' in product else 0,
            "name": product['name'],
            "price": product['price'],
            "image_url": product.get('image_url', ''),
            "reason": reason,
            "color": product.get('color', 'N/A'),
            "category": product.get('category', 'N/A'),
            "rating": product.get('rating', 0)
        })
    
    return product_cards


def display_chat_history():
    """Display all messages in the chat history"""
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.write(message["content"])
            
            # If the message contains product recommendations, display them
            if message["role"] == "assistant" and "products" in message:
                display_product_recommendations(message["products"])


def display_product_recommendations(products):
    """Display product recommendations in a grid layout"""
    cols = st.columns(3)  # Display 3 products per row
    
    for i, product in enumerate(products):
        with cols[i % 3]:
            if product.get("image_url"):
                try:
                    st.image(product["image_url"], use_column_width=True)
                except Exception:
                    # Fallback if image can't be loaded
                    st.error("Image not available")
                    
            st.markdown(f"### {product['name']}")
            st.markdown(f"**${product['price']:.2f}** • {product.get('color', 'N/A')} • {product.get('rating', 0)} ⭐")
            st.info(f"**Why this matches**: {product['reason']}")


def export_filtered_products(df, filters):
    """Export filtered products to CSV"""
    filtered_df = filter_products(df, filters)
    return filtered_df.to_csv(index=False).encode('utf-8')


if __name__ == "__main__":
    main() 