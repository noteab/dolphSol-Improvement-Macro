import os
import json

# Path to the config file
config_relative_path = os.path.join("data", "settings", "config.json")

# Load config settings
def load_config():
    try:
        with open(config_relative_path, 'r') as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        print(f"Config file not found at: {config_relative_path}")
        return None
    except json.JSONDecodeError:
        print("Error decoding the JSON config file.")
        return None

# Mockup: Load items from config
ScheduleItems = ['Item1', 'Item2', 'Item3', 'Item4']  # Example items
biomes = ['Forest', 'Desert', 'Swamp', 'Any']  # Example biomes
ItemSchedulerEntries = []

# Add new item entry
def add_new_item_entry(item_name, quantity, frequency, time_unit='Minutes', biome='Any'):
    global ItemSchedulerEntries
    entry = {
        'Enabled': 1,
        'ItemName': item_name,
        'Quantity': quantity,
        'Frequency': frequency,
        'TimeUnit': time_unit,
        'Biome': biome,
        'Deleted': False
    }
    ItemSchedulerEntries.append(entry)
    print(f"Added new item entry: {entry}")

# Save the item scheduler settings to a list or config
def save_item_scheduler_settings():
    global ItemSchedulerEntries
    saved_entries = []

    for entry in ItemSchedulerEntries:
        if entry.get('Deleted', False):
            continue  # Skip deleted entries

        saved_entries.append(entry)
    
    # Update config.json (mock-up saving method, adapt if needed)
    try:
        with open(config_relative_path, 'w') as config_file:
            json.dump(saved_entries, config_file, indent=4)
        print(f"Scheduler settings saved to {config_relative_path}")
    except Exception as e:
        print(f"Error saving config: {e}")

# Delete an item entry by marking it as deleted
def delete_item_entry(idx):
    if 0 <= idx < len(ItemSchedulerEntries):
        ItemSchedulerEntries[idx]['Deleted'] = True
        print(f"Entry {idx} marked for deletion.")

# Load item scheduler entries from the config
def load_item_scheduler_options():
    global ItemSchedulerEntries
    config_data = load_config()
    if config_data:
        ItemSchedulerEntries.clear()
        for entry in config_data.get('ItemSchedulerEntries', []):
            ItemSchedulerEntries.append(entry)
        print("Loaded item scheduler entries from config.")
    else:
        print("Failed to load item scheduler entries from config.")

# Test function to simulate highlighting item coordinates (replace with real implementation)
def highlight_item_coordinates():
    print("Simulating highlight of item coordinates...")

# Function to mock retrieval of config data
def getINIData(configPath):
    # Replace this with actual INI parsing logic if needed
    return {}

# Example usage when imported in another module
if __name__ == "__main__":
    # Load options from the config
    load_item_scheduler_options()

    # Example: Add new entry
    add_new_item_entry('Item1', 5, 10, 'Minutes', 'Forest')

    # Example: Delete an entry
    delete_item_entry(0)

    # Save the updated settings
    save_item_scheduler_settings()
