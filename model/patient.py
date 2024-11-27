import os
from services.mood_tracking import MoodEntry
import csv
from os.path import exists
from tabulate import tabulate

def get_assigned_mhwp(patient_username, assignments_file="data/assignments.csv"):
    """
    Get the assigned MHW's username for a given patient.

    :param patient_username: The username of the patient
    :param assignments_file: Path to the assignments CSV file
    :return: The assigned MHW's username or None if not found
    """
    if not exists(assignments_file):
        print(f"Error: Assignments file '{assignments_file}' not found.")
        return None

    try:
        with open(assignments_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["patient_username"] == patient_username:
                    return row["mhwp_username"]
    except Exception as e:
        print(f"Error reading assignments file: {str(e)}")

    return None


def load_mhwp_schedule(mhwp_username, schedule_file="data/mhwp_schedule.csv"):
    """
    Load the schedule of a specific MHWP, excluding already booked slots.
    """
    if not exists(schedule_file):
        print(f"Error: Schedule file '{schedule_file}' not found.")
        return []

    booked_slots = set()
    if exists("data/appointments.csv"):
        with open("data/appointments.csv", "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            booked_slots = {(row["Date"], row["time_slot"]) for row in reader if row["mhwp_username"] == mhwp_username}

    with open(schedule_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        return [row for row in reader if (row["Date"], row["time_slot"]) not in booked_slots]


def extract_available_slots(date_schedule):
    """
    Extract available slots (⬜) from the provided schedule.

    :param date_schedule: List of dictionaries representing the schedule for a specific date
    :return: List of tuples (index, slot_key) where slot_key is the time slot column name
    """
    available_slots = []
    if not date_schedule:
        print("Debug: No schedule data available.")
        return available_slots

    # Get all time slot columns (keys starting from the 3rd column onward)
    slot_columns = list(date_schedule[0].keys())[3:]
    print(f"Debug: Slot columns found - {slot_columns}")

    # Check each slot for availability (⬜)
    for idx, slot_key in enumerate(slot_columns):
        if date_schedule[0][slot_key].strip() == "⬜":
            available_slots.append((idx, slot_key))
            print(f"Debug: Available slot found - {slot_key} at index {idx}")
        else:
            print(f"Debug: Slot {slot_key} is not available.")

    return available_slots



def patient_select_slots(patient_username, mhwp_username, schedule_file, appointments_file):
    """
    Allow a patient to select up to two time slots from a specific mhwp's availability.
    """
    if not exists(schedule_file):
        print(f"Error: Schedule file '{schedule_file}' not found.")
        return

    try:
        # Load MHW's schedule
        with open(schedule_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            all_schedules = [row for row in reader if row["mhwp_username"] == mhwp_username]

        if not all_schedules:
            print(f"No schedule found for MHW {mhwp_username}.")
            return

        # Display all available dates
        print("\nAvailable Dates for MHW:")
        print(tabulate(all_schedules, headers="keys", tablefmt="grid"))

        # Patient selects a date
        selected_date = input("\nEnter a date (YYYY/MM/DD) from the schedule: ").strip()
        date_schedule = [row for row in all_schedules if row["Date"] == selected_date]

        if not date_schedule:
            print(f"No schedule found for {selected_date}. Please select a valid date.")
            return

        # Display the schedule for the selected date
        print(f"\nSchedule for {selected_date}:")
        print(tabulate(date_schedule, headers="keys", tablefmt="grid"))

        # Extract available slots (⬜)
        available_slots = extract_available_slots(date_schedule)

        if not available_slots:
            print("No available slots for the selected date. Please try another date.")
            return

        # Display available slots
        print("\nAvailable Slots (Indices with ⬜):")
        print(", ".join([f"{idx} ({slot_key})" for idx, slot_key in available_slots]))

        # Patient selects up to two slots
        while True:
            selected_indices = input("\nSelect up to two time slots by entering their indices (separated by commas): ").strip().split(",")
            try:
                selected_indices = [int(idx.strip()) for idx in selected_indices if idx.strip().isdigit()]
                if all(idx in [slot[0] for slot in available_slots] for idx in selected_indices) and len(selected_indices) <= 2:
                    break
                else:
                    print(f"Invalid input. Please enter valid indices from {[slot[0] for slot in available_slots]}.")
            except ValueError:
                print(f"Invalid input. Please enter valid indices from {[slot[0] for slot in available_slots]}.")

        # Update the schedule and save it
        for idx in selected_indices:
            slot_key = available_slots[idx][1]  # Get the slot column name
            date_schedule[0][slot_key] = "⬛"  # Mark slot as booked

        # Save the updated schedule
        with open(schedule_file, "w", newline='', encoding="utf-8") as file:
            fieldnames = list(date_schedule[0].keys())
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_schedules)

        # Log appointments in appointments file
        with open(appointments_file, "a", newline='', encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["patient_username", "mhwp_username", "Date", "Slot"])
            for idx in selected_indices:
                slot_key = available_slots[idx][1]
                writer.writerow({
                    "patient_username": patient_username,
                    "mhwp_username": mhwp_username,
                    "Date": selected_date,
                    "Slot": slot_key
                })

        print("\nAppointment(s) booked successfully.")

    except Exception as e:
        print(f"Error: {e}")



def save_appointments(booked_slots, patient_username, mhwp_username, appointments_file="data/appointments.csv"):
    """
    Save the booked appointments into the appointments file.
    """
    with open(appointments_file, "a", newline='', encoding="utf-8") as file:
        fieldnames = ["patient_username", "mhwp_username", "Date", "time_slot"]
        writer = csv.DictWriter(file, fieldnames=fieldnames)

        if file.tell() == 0:
            writer.writeheader()

        for slot in booked_slots:
            writer.writerow({
                "patient_username": patient_username,
                "mhwp_username": mhwp_username,
                "Date": slot["Date"],
                "time_slot": slot["time_slot"]
            })

def patient_select_slots(patient_username, mhwp_username, schedule_file, appointments_file):
    """
    Allow a patient to select up to two time slots from a specific mhwp's availability.
    """
    if not exists(schedule_file):
        print(f"Error: Schedule file '{schedule_file}' not found.")
        return

    try:
        # Load MHW's schedule
        with open(schedule_file, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            all_schedules = [row for row in reader if row["mhwp_username"] == mhwp_username]

        if not all_schedules:
            print(f"No schedule found for MHW {mhwp_username}.")
            return

        # Display all available dates
        print("\nAvailable Dates for MHW:")
        print(tabulate(all_schedules, headers="keys", tablefmt="grid"))

        # Patient selects a date
        selected_date = input("\nEnter a date (YYYY/MM/DD) from the schedule: ").strip()
        date_schedule = [row for row in all_schedules if row["Date"] == selected_date]

        if not date_schedule:
            print(f"No schedule found for {selected_date}. Please select a valid date.")
            return

        # Display the schedule for the selected date
        print(f"\nSchedule for {selected_date}:")
        print(tabulate(date_schedule, headers="keys", tablefmt="grid"))

        # Extract available slots (⬜)
        available_slots = extract_available_slots(date_schedule)

        if not available_slots:
            print("No available slots for the selected date. Please try another date.")
            return

        # Display available slots
        print("\nAvailable Slots (Indices with ⬜):")
        print(", ".join([f"{idx} ({slot_key})" for idx, slot_key in available_slots]))

        # Patient selects up to two slots
        while True:
            selected_indices = input("\nSelect up to two time slots by entering their indices (separated by commas): ").strip().split(",")
            try:
                selected_indices = [int(idx.strip()) for idx in selected_indices if idx.strip().isdigit()]
                if all(idx in [slot[0] for slot in available_slots] for idx in selected_indices) and len(selected_indices) <= 2:
                    break
                else:
                    print(f"Invalid input. Please enter valid indices from {[slot[0] for slot in available_slots]}.")
            except ValueError:
                print(f"Invalid input. Please enter valid indices from {[slot[0] for slot in available_slots]}.")

        # Update the schedule and save it
        for idx in selected_indices:
            slot_key = available_slots[idx][1]  # Get the slot column name
            date_schedule[0][slot_key] = "⬛"  # Mark slot as booked

        # Save the updated schedule
        with open(schedule_file, "w", newline='', encoding="utf-8") as file:
            fieldnames = list(date_schedule[0].keys())
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(all_schedules)

        # Log appointments in appointments file
        with open(appointments_file, "a", newline='', encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["patient_username", "mhwp_username", "Date", "Slot"])
            for idx in selected_indices:
                slot_key = available_slots[idx][1]
                writer.writerow({
                    "patient_username": patient_username,
                    "mhwp_username": mhwp_username,
                    "Date": selected_date,
                    "Slot": slot_key
                })

        print("\nAppointment(s) booked successfully.")

    except Exception as e:
        print(f"Error: {e}")




def handle_patient_menu(user):
    while True:
        print("\nPatient Options:")
        print("1. Update Personal Info")
        print("2. Change Password")
        print("3. Change email")
        print("4. Change emergency email")
        print("5. View Medical Records")
        print("6. Book/Cancel Appointment")
        print("7. Delete Account")
        print("8. Track Mood")
        print("9. Logout")

        patient_choice = input("Select an option (1-9): ").strip()
        if patient_choice == '1':
            new_username = input("Enter new username: ").strip()
            user.update_info(new_username=new_username)
        elif patient_choice == '2':
            new_password = input("Enter new password: ").strip()
            user.update_password(new_password)
        elif patient_choice == '3':  # Change email
            new_email = input("Enter new email: ").strip()
            if user.update_info(new_email=new_email):
                print("Email updated successfully!")
            else:
                print("Failed to update email. Try again.")
        elif patient_choice == '4':  # Change emergency email
            new_emergency_email = input("Enter new emergency email: ").strip()
            if user.update_info(new_emergency_email=new_emergency_email):
                print("Emergency email updated successfully!")
            else:
                print("Failed to update emergency email. Try again.")
        elif patient_choice == '5':
            print("Medical records feature coming soon...")
        elif patient_choice == '6':  # Book/Cancel Appointment
            print("\nBook/Cancel Appointment:")
            print("1. Book an appointment by selecting time slots")
            print("2. Cancel an appointment")
            print("3. View your booked appointments")  # New option

            appointment_choice = input("Select an option (1/2/3): ").strip()

            if appointment_choice == "1":  # Book an appointment by selecting slots
                # Automatically get the assigned MHW's username
                mhwp_username = get_assigned_mhwp(user.username, "data/assignments.csv")

                if not mhwp_username:
                    print("No MHW assigned to you. Please contact support.")
                else:
                    print(f"Your assigned MHW: {mhwp_username}")
                    patient_select_slots(user.username, mhwp_username, "data/mhwp_schedule.csv",
                                         "data/appointments.csv")

            elif appointment_choice == "2":  # Cancel an appointment
                date = input("Enter appointment date (YYYY-MM-DD): ").strip()
                time_slot = input("Enter appointment time slot: ").strip()

                # Load and modify the appointments file
                if exists("data/appointments.csv"):
                    with open("data/appointments.csv", "r", encoding="utf-8") as file:
                        appointments = list(csv.DictReader(file))

                    updated_appointments = [
                        appt for appt in appointments
                        if not (appt["patient_username"] == user.username and appt["Date"] == date and appt["time_slot"] == time_slot)
                    ]

                    if len(updated_appointments) < len(appointments):
                        with open("data/appointments.csv", "w", newline='', encoding="utf-8") as file:
                            writer = csv.DictWriter(file, fieldnames=["patient_username", "mhwp_username", "Date", "time_slot"])
                            writer.writeheader()
                            writer.writerows(updated_appointments)
                        print("Appointment cancelled successfully!")
                    else:
                        print("No matching appointment found.")
                else:
                    print("No appointments found.")

            elif appointment_choice == "3":  # View booked appointments
                if exists("data/appointments.csv"):
                    with open("data/appointments.csv", "r", encoding="utf-8") as file:
                        reader = csv.DictReader(file)
                        appointments = [row for row in reader if row["patient_username"] == user.username]

                    if appointments:
                        print("\nYour Appointments:")
                        print(tabulate(appointments, headers="keys", tablefmt="grid"))
                    else:
                        print("\nNo appointments found.")
                else:
                    print("No appointments found.")
            else:
                print("Invalid choice.")
        elif patient_choice == '7':
            confirm = input("Confirm delete account? (yes/no): ").strip()
            if confirm.lower() == "yes":
                user.delete_from_csv()
                print("Account deleted successfully.")
                break
        elif patient_choice == '8':
            handle_mood_tracking(user)
        elif patient_choice == '9':
            print("Logging out.")
            break
        else:
            print("Invalid choice, please try again.")



def handle_mood_tracking(user):
    print("\nMood Tracking")
    print("How are you feeling today?")
    print("1. Green - Very Good (Feeling great, energetic, positive)")
    print("2. Blue - Good (Calm, content, peaceful)")
    print("3. Yellow - Neutral (OK, balanced)")
    print("4. Orange - Not Great (Worried, uneasy)")
    print("5. Red - Poor (Distressed, anxious, depressed)")

    color_choice = input("Select your mood (1-5): ").strip()
    if color_choice in ["1", "2", "3", "4", "5"]:
        comments = input("Would you like to add any comments about your mood? ").strip()
        mood_entry = MoodEntry(user.username, color_choice, comments)
        mood_entry.save_mood_entry()

        display_mood_history(user.username)
    else:
        print("Invalid mood selection.")


def display_mood_history(username):
    print("\nYour recent mood history:")
    history = MoodEntry.get_user_mood_history(username)
    if not history.empty:
        print(history[['timestamp', 'color_code', 'comments']].head())

