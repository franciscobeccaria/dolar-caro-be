import json
import os
from datetime import datetime
from typing import Dict, Any

# Create a data directory if it doesn't exist
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def save_historical_data(endpoint: str, data: Dict[str, Any]) -> None:
    """
    Save historical data for an endpoint to a JSON file
    
    Args:
        endpoint: The name of the endpoint (e.g., 'nike', 'adidas-jersey')
        data: The data to save
    """
    # Create endpoint directory if it doesn't exist
    endpoint_dir = os.path.join(DATA_DIR, endpoint)
    os.makedirs(endpoint_dir, exist_ok=True)
    
    # Create a filename with the current timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"{timestamp}.json"
    file_path = os.path.join(endpoint_dir, filename)
    
    # Add timestamp to the data
    data_with_timestamp = data.copy()
    data_with_timestamp['timestamp'] = datetime.now().isoformat()
    
    # Save the data to a JSON file
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data_with_timestamp, f, ensure_ascii=False, indent=2)
    
    # Also update the latest.json file for quick access to the most recent data
    latest_path = os.path.join(endpoint_dir, 'latest.json')
    with open(latest_path, 'w', encoding='utf-8') as f:
        json.dump(data_with_timestamp, f, ensure_ascii=False, indent=2)
    
    print(f"Historical data saved to {file_path}")

def get_historical_data(endpoint: str, limit: int = 10) -> list:
    """
    Get historical data for an endpoint
    
    Args:
        endpoint: The name of the endpoint (e.g., 'nike', 'adidas-jersey')
        limit: Maximum number of historical entries to return
        
    Returns:
        A list of historical data entries, sorted by timestamp (newest first)
    """
    endpoint_dir = os.path.join(DATA_DIR, endpoint)
    
    if not os.path.exists(endpoint_dir):
        return []
    
    # Get all JSON files except latest.json
    files = [f for f in os.listdir(endpoint_dir) if f.endswith('.json') and f != 'latest.json']
    
    # Sort files by name (which includes timestamp) in descending order
    files.sort(reverse=True)
    
    # Load data from each file
    result = []
    for i, file in enumerate(files):
        if i >= limit:
            break
            
        file_path = os.path.join(endpoint_dir, file)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                result.append(data)
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
    
    return result
