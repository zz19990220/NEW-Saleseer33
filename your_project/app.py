import streamlit as st
import pandas as pd
import os
from pathlib import Path
from dotenv import load_dotenv
import time

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

# Initialize session state for history
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "last_filters" not in st.session_state:
    st.session_state.last_filters = {}


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
        data_path = "inventory/products.csv"
        
        # Display inventory stats
        try:
            df = load_inventory(data_path)
            st.success(f"✅ Loaded {len(df)} products")
            st.text(f"Categories: {', '.join(df['category'].unique())}")
            st.text(f"Colors: {', '.join(df['color'].unique())}")
            st.text(f"Price range: ${df['price'].min():.2f} - ${df['price'].max():.2f}")
        except Exception as e:
            st.error(f"❌ Error loading inventory: {e}")
            return
    
    # Chat input
    user_query = st.chat_input("What kind of product are you looking for?")
    
    # Process query when submitted
    if user_query:
        process_query(user_query, df)
    
    # Display chat history
    display_chat_history()


def process_query(user_query, df):
    # Add user message to chat history
    st.session_state.chat_history.append({"role": "user", "content": user_query})
    
    # Processing message
    with st.chat_message("assistant"):
        with st.status("Processing your request...", expanded=True) as status:
            st.write("Analyzing your query...")
            
            # Parse query using LLM
            try:
                filters = parse_query(user_query)
                st.session_state.last_filters = filters
                st.write("✅ Query understood")
                
                status.update(label="Finding matching products...", state="running")
                
                if not filters:
                    status.update(label="⚠️ Couldn't parse your query. Please try again.", state="error")
                    st.session_state.chat_history.append({
                        "role": "assistant", 
                        "content": "I couldn't understand your request. Please try specifying product type, color, or price range more clearly."
                    })
                    return
                
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
    
    if 'category' in filters:
        parts.append(f"in the {filters['category']} category")
    
    if 'color' in filters:
        parts.append(f"in {filters['color']} color")
    
    if 'price_max' in filters:
        parts.append(f"under ${filters['price_max']}")
    
    if 'price_min' in filters:
        parts.append(f"over ${filters['price_min']}")
    
    if 'min_rating' in filters:
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
            "id": product['id'],
            "name": product['name'],
            "price": product['price'],
            "image_url": product['image_url'],
            "reason": reason,
            "color": product['color'],
            "category": product['category'],
            "rating": product['rating']
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
            st.image(product["image_url"], use_column_width=True)
            st.markdown(f"### {product['name']}")
            st.markdown(f"**${product['price']:.2f}** • {product['color']} • {product['rating']} ⭐")
            st.info(f"**Why this matches**: {product['reason']}")


if __name__ == "__main__":
    main() 