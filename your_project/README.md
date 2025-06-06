# AI Product Recommendation System

A simple Streamlit web application that uses AI to understand natural language product queries and recommend items from an inventory.

## Features

- **Natural Language Understanding**: Parse user queries like "Show me red dresses under $200"
- **Intelligent Filtering**: Filter products by category, color, price, and more
- **Visual Recommendations**: Display matching products with images and explanations
- **Inventory Management**: Upload your own CSV/Excel inventory or use the sample data
- **Chat Interface**: Interactive chat-like experience for querying products

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

## Usage Instructions

1. **Load Inventory**: 
   - Upload your own CSV/Excel inventory file using the upload button in the sidebar
   - Or click "Use Sample Inventory Data" to use the default product list
   - The sidebar will show inventory statistics once loaded

2. **Query Products**:
   - Type natural language queries in the chat input at the bottom
   - Example: "Show me red dresses under $200"
   - The AI will process your query and display matching products

3. **View Recommendations**:
   - Products are displayed in a grid with images and details
   - Each product includes a reason why it matches your query

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