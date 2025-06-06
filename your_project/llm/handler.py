import os
import json
import requests
from typing import Dict, Any, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def parse_query(user_query: str) -> Dict[str, Any]:
    """
    Send user query to OpenRouter API and parse the response into structured filters
    
    Parameters:
    - user_query: Natural language query from user
    
    Returns:
    - Dictionary with parsed filter parameters
    """
    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        raise ValueError("OpenRouter API key not found. Please set OPENROUTER_API_KEY in .env file")
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    prompt = f"""
    Parse the following product query into structured parameters for filtering an e-commerce inventory.
    Query: "{user_query}"
    
    Extract the following information if present:
    - category: The type of product (e.g., dress, shoe, pants)
    - color: Color preference
    - price_min: Minimum price (numeric value only)
    - price_max: Maximum price (numeric value only)
    - min_rating: Minimum rating score (if mentioned)
    
    Return ONLY a valid JSON object with these fields. If information for a field is not provided, exclude that field.
    For example:
    {{
      "category": "dress",
      "color": "red", 
      "price_max": 200
    }}
    """
    
    try:
        response = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers=headers,
            json={
                "model": "openai/gpt-3.5-turbo",  # Using a simpler model to save costs
                "messages": [
                    {"role": "system", "content": "You are a helpful assistant that parses product queries into structured data."},
                    {"role": "user", "content": prompt}
                ],
                "max_tokens": 150
            },
        )
        
        response.raise_for_status()
        result = response.json()
        
        # Extract the content from the response
        content = result["choices"][0]["message"]["content"].strip()
        
        # Sometimes the model wraps the JSON in code blocks or adds extra text
        # Let's try to extract just the JSON part
        if "```json" in content:
            # Extract content between ```json and ```
            content = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            # Extract content between ``` and ```
            content = content.split("```")[1].strip()
        
        parsed_filters = json.loads(content)
        
        # Validate numeric fields
        if "price_min" in parsed_filters and parsed_filters["price_min"] is not None:
            parsed_filters["price_min"] = float(parsed_filters["price_min"])
        
        if "price_max" in parsed_filters and parsed_filters["price_max"] is not None:
            parsed_filters["price_max"] = float(parsed_filters["price_max"])
        
        if "min_rating" in parsed_filters and parsed_filters["min_rating"] is not None:
            parsed_filters["min_rating"] = float(parsed_filters["min_rating"])
            
        return parsed_filters
    
    except requests.exceptions.RequestException as e:
        logger.error(f"API request failed: {e}")
        return {}
    
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse JSON response: {e}, Content: {content}")
        return {}
    
    except Exception as e:
        logger.error(f"Error parsing query: {e}")
        return {} 