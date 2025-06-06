# AI Product Recommendation System

A simple Streamlit web application that uses AI to understand natural language product queries and recommend items from an inventory.

## Features

- **Natural Language Understanding**: Parse user queries like "Show me red dresses under $200"
- **Intelligent Filtering**: Filter products by category, color, price, and more
- **Visual Recommendations**: Display matching products with images and explanations

## Setup

1. Clone the repository
2. Install dependencies:
```
pip install -r requirements.txt
```
3. Set up environment variables:
   - Create a `.env` file in the project root
   - Add your OpenRouter API key: `OPENROUTER_API_KEY=your_key_here`

## Running the Application

```
streamlit run app.py
```

The app will be available at http://localhost:8501

## Project Structure

- `app.py`: Main Streamlit application with UI and app logic
- `inventory/`: Inventory management and filtering
  - `products.csv`: Sample product data
  - `filters.py`: Functions for loading and filtering products
- `llm/`: LLM integration for query parsing
  - `handler.py`: OpenRouter API interaction

## Sample Queries

- "Show me red dresses under $200"
- "I need comfortable shoes"
- "Find blue jackets with good ratings" 