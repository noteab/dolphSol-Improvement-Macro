import tkinter as tk
from tkinter import messagebox

def save_to_env(token, channel_id, user_id):
    """Saves the Discord details to a .env file."""
    try:
        with open(".env", "w") as file:
            file.write(f"DISCORD_BOT_TOKEN='{token}'\n")
            file.write(f"DISCORD_CHANNEL_ID='{channel_id}'\n")
            file.write(f"YOUR_DISCORD_USER_ID='{user_id}'\n")
        messagebox.showinfo("Success", "Details saved to .env file successfully!")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save to .env file: {e}")

def submit():
    """Handles the submit button click event."""
    token = entry_token.get()
    channel_id = entry_channel_id.get()
    user_id = entry_user_id.get()

    if not token or not channel_id or not user_id:
        messagebox.showerror("Error", "All fields must be filled out!")
    else:
        save_to_env(token, channel_id, user_id)

# Create the main window
root = tk.Tk()
root.title("Discord Configuration")

# Discord Bot Token
label_token = tk.Label(root, text="Discord Bot Token:")
label_token.grid(row=0, column=0, padx=10, pady=10)
entry_token = tk.Entry(root, width=50)
entry_token.grid(row=0, column=1, padx=10, pady=10)

# Discord Channel ID
label_channel_id = tk.Label(root, text="Discord Channel ID:")
label_channel_id.grid(row=1, column=0, padx=10, pady=10)
entry_channel_id = tk.Entry(root, width=50)
entry_channel_id.grid(row=1, column=1, padx=10, pady=10)

# Your Discord User ID
label_user_id = tk.Label(root, text="Your Discord User ID:")
label_user_id.grid(row=2, column=0, padx=10, pady=10)
entry_user_id = tk.Entry(root, width=50)
entry_user_id.grid(row=2, column=1, padx=10, pady=10)

# Submit button
submit_button = tk.Button(root, text="Save", command=submit)
submit_button.grid(row=3, column=1, padx=10, pady=10)

# Run the Tkinter main loop
root.mainloop()
