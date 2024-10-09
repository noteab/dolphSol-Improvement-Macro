import os
import json
import requests
from data.lib import config

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
    config = config.read()

    if config:
        webhook_url = config.get("webhook_url")
        user_id = config.get("user_id")
        
        if webhook_url and user_id:
            # Example message you want to send
            send_webhook_message(webhook_url, user_id, "Mari has been found!")
        else:
            print("Webhook URL or User ID is missing from the config file.")

