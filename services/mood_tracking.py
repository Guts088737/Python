import pandas as pd
from datetime import datetime
from config import MOOD_DATA_PATH

class MoodEntry:
    def __init__(self, username, color_code, comments, timestamp=None):
        self.username = username
        self.color_code = color_code
        self.comments = comments
        self.timestamp = timestamp or datetime.now()
        
        # Color code mapping
        self.color_mapping = {
            "1": "Green",
            "2": "Blue", 
            "3": "Yellow",
            "4": "Orange",
            "5": "Red"
        }

    def save_mood_entry(self):
        """Save mood entry to CSV file"""
        try:
            # Create DataFrame with the new entry
            new_entry = pd.DataFrame({
                'username': [self.username],
                'color_code': [self.color_mapping.get(self.color_code, "Unknown")],
                'comments': [self.comments],
                'timestamp': [self.timestamp]
            })

            # Append to existing file or create new one
            try:
                df = pd.read_csv(MOOD_DATA_PATH)
                df = pd.concat([df, new_entry], ignore_index=True)
            except FileNotFoundError:
                df = new_entry

            df.to_csv(MOOD_DATA_PATH, index=False)
            print("Mood entry saved successfully!")
            return True

        except Exception as e:
            print(f"Error saving mood entry: {e}")
            return False

    @staticmethod
    def get_user_mood_history(username):
        """Retrieve mood history for a specific user"""
        try:
            df = pd.read_csv(MOOD_DATA_PATH)
            user_moods = df[df['username'] == username]
            return user_moods.sort_values('timestamp', ascending=False)
        except FileNotFoundError:
            return pd.DataFrame()
