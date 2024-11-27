from services.registration import register_user
from services.login import handle_login
import os
from utils.display_banner import display_banner

# # Create data directory if it doesn't exist
# DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
# if not os.path.exists(DATA_DIR):
#     os.makedirs(DATA_DIR)

# # CSV file directory
# USER_FILE_PATH = os.path.join(DATA_DIR, 'user_data.csv')

def handle_exit():
    print("Exiting the system now.")
    return False

def handle_invalid():
    print("Invalid choice, please try again.")
    return True

def show_menu():
    print("\nChoose an option:")
    print("1. Register")
    print("2. Login")
    print("3. Exit")
    return input("Select an option (1/2/3): ")

def main():
    
    display_banner() # Display welcome banner with original ASCII art 
    choice = show_menu() # show original login choice.
    
    menu_actions = {
        '1': lambda: register_user(),
        '2': lambda: handle_login(),
        '3': lambda: handle_exit(),
    }
    #@mikrostiff: break on false
    #@mikrostiff: ")()" is not a tyoo. the () executes the result of menu_actions      
    while menu_actions.get(choice, handle_invalid)():
        choice = show_menu()

 
if __name__ == "__main__":
    main()
   