import os
import json
import requests

# Get the absolute path to the config.json file
def get_config_path():
    # Base directory is defined explicitly or relative to the current script's location
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Path to the config.json relative to the script location
    config_relative_path = os.path.join("dolphSol-Improvement-Macro-2.0-dev", "data", "settings", "config.json")
    
    # Absolute path constructed from base_dir and the relative path
    config_path = os.path.join(base_dir, config_relative_path)
    
    # Print for debugging purposes to see the full path
    print(f"Attempting to load config from: {config_path}")
    
    # Check if the path exists to provide clear error messages
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found at: {config_path}")
    
    return config_path

# Load the config file
def load_config():
    config_path = get_config_path()
    
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        return config
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None
    except json.JSONDecodeError:
        print("Error decoding the JSON config file.")
        return None

# Send a message via the webhook
def send_webhook_message(webhook_url, user_id, message="Hello from Webhook!"):
    data = {
        "content": f"<@{user_id}> {message}",
        "username": "Webhook System",
    }
    
    response = requests.post(webhook_url, json=data)
    
    if response.status_code == 204:
        print("Message sent successfully!")
    else:
        print(f"Failed to send message. Status code: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    config = load_config()

    if config:
        webhook_url = config.get("webhook_url")
        user_id = config.get("user_id")
        
        if webhook_url and user_id:
            # Example message you want to send
            send_webhook_message(webhook_url, user_id, "Mari has been found!")
        else:
            print("Webhook URL or User ID is missing from the config file.")

