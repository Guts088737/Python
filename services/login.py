# handles all login related function and user interface 

import pandas as pd
from model.user import User  
from model.admin import handle_admin_menu
from model.mhwp import handle_mhwp_menu
from model.patient import handle_patient_menu


def login_user():
   """Authenticate and login user.
   Args:
       file_path: Path to user data CSV file
   Returns:
       User object if login successful, None otherwise
   """
   username = input("Enter username: ").strip()
   password = input("Enter password: ").strip()
   
   # Create user object with temporary role
   user = User(username, password, "temp")
   
   # Verify credentials
   if user.load_from_csv():
       hashed_password = user.hash_password(password) 
       if user.password == hashed_password:
           print(f"Login successful! Welcome, {user.username}!")
           return user
       else:
           print("Incorrect password.")
   else:
       print("User does not exist.")
   return None

def verify_staff(role):
    """Verify staff members with role-specific code"""
    verification_code = input(f"Enter {role} verification code: ")
    if verification_code == "0000":
        print("Verification successful!")
        return True
    else:
        print("Verification failed. Access denied.")
        return False

def handle_login():
    user = login_user()
    if user:
        print(f"You are logged in as {user.role}.")
        match user.role:
            case "admin":
                if not verify_staff("admin"):
                    return False
                handle_admin_menu(user)
            case "mhwp":
                if not verify_staff("mhwp"):
                    return False
                handle_mhwp_menu(user)
            case "patient":
                handle_patient_menu(user)
    return True

    