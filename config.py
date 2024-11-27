import os

# Create data directory if it doesn't exist
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# Global file paths
USER_DATA_PATH = os.path.join(DATA_DIR, 'user_data.csv')
MOOD_DATA_PATH = os.path.join(DATA_DIR, 'mood_data.csv')
# OTHER_DATA_PATH = os.path.join(DATA_DIR, '#place your csv file name here')
