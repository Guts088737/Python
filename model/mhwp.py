import os
import csv
from tabulate import tabulate
from os.path import exists
from datetime import datetime, timedelta
import calendar

def initialize_schedule_file(file_path):
    """
    Clear all data from the mhwp_schedule.csv file except the column headers.
    :param file_path: Path to the schedule file.
    """
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' does not exist.")
        return

    try:
        # Define the column headers
        headers = ["mhwp_username", "Date", "Day", "09:00-10:00 (0)", "10:00-11:00 (1)",
                   "11:00-12:00 (2)", "12:00-13:00 (3)", "13:00-14:00 (4)",
                   "14:00-15:00 (5)", "15:00-16:00 (6)"]

        # Overwrite the file with only the headers
        with open(file_path, "w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)  # Write headers only

        print(f"\nThe schedule file '{file_path}' has been successfully reset. All data has been cleared.")

    except Exception as e:
        print(f"Error resetting the file: {e}")


def list_appointments_for_mhw(mhw_username, file_path):
    """List appointments for the currently logged-in MHW"""
    appointments = []

    # Check if file exists
    if not exists(file_path):
        print(f"Error: Appointment record file '{file_path}' not found")
        return appointments

    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)

            # First read all matching appointments
            for row in reader:
                if row['mhwp_username'] == mhw_username:
                    appointments.append(row)

            # Check if any appointments were found
            if not appointments:
                print(f"\nNo appointments found for {mhw_username}")
                return appointments

            # Only print table if records exist
            print("\nAppointments for MHW:", mhw_username)
            print("------------------------------------------------------------------")
            print("ID | Patient      | Date       | Start  | End    | Status")
            print("------------------------------------------------------------------")
            for idx, row in enumerate(appointments, start=1):
                print(
                    f"{idx:2d} | {row['patient_username']:<10} | {row['date']} | {row['start_time']} | {row['end_time']} | {row['status']}")

    except Exception as e:
        print(f"Error reading appointments: {str(e)}")

    return appointments


def generate_day_from_date(date_str):
    """
    根据日期生成对应的星期几。
    :param date_str: 日期字符串，格式为 "YYYY/MM/DD"
    :return: 对应的星期几（如 "Monday"）
    """
    try:
        return datetime.strptime(date_str, "%Y/%m/%d").strftime("%A")
    except ValueError:
        return "Invalid Date"



def generate_schedule_for_month(username, weekdays):
    """
    Generate a 1-month schedule based on user availability, including day names.
    :param username: Username of the MHW
    :param weekdays: List of weekday indices (e.g., [0, 3] for Monday and Thursday)
    :return: A list of schedules containing dates and their corresponding day names
    """
    today = datetime.today()
    end_date = today + timedelta(days=30)  # 1 month later

    schedule = []
    current_date = today
    while current_date <= end_date:
        if current_date.weekday() in weekdays:
            # Include both date and corresponding weekday name
            schedule.append((current_date.strftime("%Y/%m/%d"), calendar.day_name[current_date.weekday()]))
        current_date += timedelta(days=1)

    return schedule

def generate_time_slots(start_hour=9, end_hour=16):
    """
    Generate time slots in the format '09:00-10:00 (0)', '10:00-11:00 (1)', etc.
    :param start_hour: Start of the time slots (default: 9)
    :param end_hour: End of the time slots (default: 16)
    :return: A list of formatted time slots
    """
    time_slots = []
    for i, hour in enumerate(range(start_hour, end_hour)):
        start_time = f"{hour:02d}:00"
        end_time = f"{hour + 1:02d}:00"
        time_slots.append(f"{start_time}-{end_time} ({i})")
    return time_slots


def display_current_schedule(username, file_path):
    """Display the current open schedule for the MHW"""
    if not os.path.exists(file_path):
        print(f"Error: Schedule file '{file_path}' not found.")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            headers = next(reader)  # Get headers
            user_data = [row for row in reader if row[0] == username]

            if not user_data:
                print("\nNo available schedule found for your account. Please set up your availability.")
                return

            # Print the user's schedule
            print(f"\nCurrent Open Schedule for {username}:")
            print(tabulate(user_data, headers=headers, tablefmt="grid"))

    except Exception as e:
        print(f"Error displaying schedule: {str(e)}")



def modify_mhwp_schedule(user, option, dates=None, time_slot_indices=None):
    output_file = "data/mhwp_schedule.csv"
    if not os.path.exists(output_file):
        print(f"Error: Schedule file '{output_file}' not found.")
        return

    try:
        with open(output_file, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            headers = next(reader)  # Read headers
            all_schedules = list(reader)

        # Add "Day" to headers if missing
        if "Day" not in headers:
            headers.insert(2, "Day")  # Insert after "Date"

        # Ensure all rows have a "Day" value
        for row in all_schedules:
            if len(row) < len(headers):
                date_str = row[1]  # Get "Date" column
                day_name = generate_day_from_date(date_str)
                row.insert(2, day_name)

        # Update user's schedule
        user_schedule = [row for row in all_schedules if row[0] == user.username]
        other_users = [row for row in all_schedules if row[0] != user.username]

        if option == 1:  # Take a Leave
            updated_user_schedule = [row for row in user_schedule if row[1] not in dates]

        elif option == 2:  # Change Time Slots
            updated_user_schedule = user_schedule[:]
            for date in dates:
                matching_row = next((row for row in updated_user_schedule if row[1] == date), None)
                if not matching_row:
                    print(f"No schedule found for the date: {date}")
                    continue

                # Update time slots
                for idx in range(len(headers[3:])):  # Slots start from 3rd column
                    matching_row[idx + 3] = "■" if idx in time_slot_indices else "□"

        # Combine updated user schedule with other users
        updated_schedules = other_users + updated_user_schedule

        with open(output_file, "w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(headers)  # Write headers
            writer.writerows(updated_schedules)  # Write all data

    except Exception as e:
        print(f"Error modifying schedule: {str(e)}")


def setup_mhwp_schedule(user):
    """Set up availability schedule for the Mental Health Worker with slots."""
    print("\nSetup Your Availability")

    output_file = "data/mhwp_schedule.csv"
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            headers = next(reader)  # Read headers
            if any(row[0] == user.username for row in reader):
                print("\nYou have already set up your availability.")
                print("Returning to the Mental Health Worker Options menu...\n")
                return

    print("\nDay Index Reference:")
    print("Monday (0), Tuesday (1), Wednesday (2), Thursday (3), Friday (4), Saturday (5), Sunday (6)")

    weekday_indices = input("Enter the indices of your available weekdays, separated by commas (e.g., 0,3): ").strip()
    weekday_indices = [int(idx) for idx in weekday_indices.split(",") if idx.isdigit()]

    available_dates = generate_schedule_for_month(user.username, weekday_indices)

    start_hour, end_hour = 9, 16
    time_slots = generate_time_slots(start_hour, end_hour)

    headers = ["mhwp_username", "Date", "Day"] + time_slots
    rows = []
    for date, _ in available_dates:
        day_name = generate_day_from_date(date)  # Calculate day from date
        rows.append([user.username, date, day_name] + ["□" for _ in time_slots])

    print("\nGenerated Schedule for the Next 1 Month:")
    print(tabulate(rows, headers=headers, tablefmt="grid"))

    selected_indices = input("\nEnter the indices of your available time slots, separated by commas (e.g., 0,2,4): ").strip()
    selected_indices = [int(idx) for idx in selected_indices.split(",") if idx.isdigit()]

    for row in rows:
        for idx in selected_indices:
            row[idx + 3] = "■"  # Update slots (offset by 3 for username, date, and day)

    print("\nYour updated schedule (applying changes to all selected weekdays):")
    print(tabulate(rows, headers=headers, tablefmt="grid"))

    updated_data = []
    if os.path.exists(output_file):
        with open(output_file, "r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader)  # Skip headers
            updated_data = [row for row in reader if row[0] != user.username]

    updated_data.extend(rows)

    with open(output_file, "w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(headers)
        writer.writerows(updated_data)

    print(f"\nYour schedule has been successfully saved to {output_file}.")

def handle_mhwp_menu(user):
    while True:
        print("\nMental Health Worker Options:")
        print("1. View Patient Records")
        print("2. Add Counseling Notes")
        print("3. Manage Appointments")
        print("4. Set Up Your Availability")
        print("5. View Your Current Schedule")
        print("6. Modify Your Availability")
        print("7. Reset Schedule (Clear All Data)")
        print("8. Logout")

        mhwp_choice = input("Select an option (1-7): ").strip()

        if mhwp_choice == '1':  # View Patient Records
            print("\nThis feature is coming soon...")

        elif mhwp_choice == '2':  # Add Counseling Notes
            print("\nThis feature is coming soon...")

        elif mhwp_choice == '3':  # Manage Appointments
            while True:
                print("\nManage Appointments:")
                print("1. View all appointments")
                print("2. Confirm an appointment")
                print("3. Cancel an appointment")
                print("4. Back to main menu")

                manage_choice = input("Select an option (1-4): ").strip()

                if manage_choice == "1":  # View all appointments
                    appointments = list_appointments_for_mhw(user.username, "data/appointments.csv")
                    if not appointments:
                        continue  # Return to appointment management menu

                elif manage_choice in ["2", "3"]:  # Confirm or cancel an appointment
                    appointments = list_appointments_for_mhw(user.username, "data/appointments.csv")
                    if not appointments:
                        continue  # Return to appointment management menu

                    appointment_id = input("Enter the ID of the appointment to manage: ").strip()
                    try:
                        appointment_id = int(appointment_id) - 1
                        if 0 <= appointment_id < len(appointments):
                            selected_appointment = appointments[appointment_id]
                            action = "confirm" if manage_choice == "2" else "cancel"
                            try:
                                user.manage_appointments(
                                    "data/appointments.csv",
                                    action,
                                    selected_appointment['patient_username'],
                                    selected_appointment['date'],
                                    selected_appointment['start_time']
                                )
                                print(f"Appointment successfully {action}ed!")
                            except Exception as e:
                                print(f"Error processing appointment: {str(e)}")
                        else:
                            print("Invalid ID. Please try again.")
                    except ValueError:
                        print("Invalid input. Please enter a valid appointment ID.")

                elif manage_choice == "4":  # Back to MHW Options
                    print("Returning to main menu...")
                    break

                else:
                    print("Invalid choice, please select an option between 1 and 4.")

        elif mhwp_choice == '4':  # Set up availability
            setup_mhwp_schedule(user)

        elif mhwp_choice == '5':  # View current schedule
            display_current_schedule(user.username, "data/mhwp_schedule.csv")

        elif mhwp_choice == '6':  # Modify Your Availability
            while True:
                print("\nModify Your Availability Options:")
                print("1. Take a Leave (Delete specific dates)")
                print("2. Change Time Slots for Specific Dates")
                print("3. Back to main menu")

                modify_choice = input("Select an option (1-3): ").strip()

                if modify_choice == '1':  # Take a Leave
                    leave_dates = input("\nEnter the dates you want to take leave for (YYYY/MM/DD), separated by commas: ").strip()
                    leave_dates = [date.strip() for date in leave_dates.split(",")]

                    # Process leave dates
                    file_path = "data/mhwp_schedule.csv"

                    try:
                        with open(file_path, "r", encoding="utf-8") as file:
                            reader = csv.reader(file)
                            headers = next(reader)  # Read headers
                            all_schedules = list(reader)

                        # Keep all other users' schedules
                        other_users = [row for row in all_schedules if row[0] != user.username]
                        # Filter out leave dates for the current user
                        updated_user_schedule = [row for row in all_schedules if row[0] == user.username and row[1] not in leave_dates]

                        # Combine updated user schedule with other users
                        updated_schedules = other_users + updated_user_schedule

                        # Save the updated schedule back to the file
                        with open(file_path, "w", newline='', encoding="utf-8") as file:
                            writer = csv.writer(file)
                            writer.writerow(headers)  # Write headers
                            writer.writerows(updated_schedules)  # Write updated data
                        print("\nUpdated Schedule (Remaining Dates):")
                        print(tabulate(updated_user_schedule, headers=headers, tablefmt="grid"))
                        print("\nYour leave request has been saved successfully!")
                    except Exception as e:
                        print(f"Error processing leave request: {str(e)}")
                elif modify_choice == '2':  # Change Time Slots
                    modify_dates = input(
                        "\nEnter the dates you want to modify (YYYY/MM/DD), separated by commas: ").strip()
                    if not modify_dates:  # Check if user enters nothing
                        print("\nNo dates entered. Returning to menu...")
                        continue
                    modify_dates = [date.strip() for date in modify_dates.split(",")]
                    file_path = "data/mhwp_schedule.csv"
                    try:
                        with open(file_path, "r", encoding="utf-8") as file:
                            reader = csv.reader(file)
                            headers = next(reader)  # Read headers
                            all_schedules = list(reader)

                        # Generate time slots and ensure headers match time slots
                        time_slots = generate_time_slots()  # Generates ['09:00-10:00 (0)', ..., '15:00-16:00 (6)']
                        expected_headers = ["mhwp_username", "Date", "Day"] + time_slots

                        # Expand headers if necessary
                        if len(headers) < len(expected_headers):
                            headers = expected_headers

                        # Extract current user's schedule and keep others unchanged
                        other_users = [row for row in all_schedules if row[0] != user.username]
                        updated_user_schedule = [row for row in all_schedules if row[0] == user.username]
                        num_slots = len(time_slots)
                        for date in modify_dates:
                            matching_row = next((row for row in updated_user_schedule if row[1] == date), None)
                            if not matching_row:
                                print(f"No schedule found for the date: {date}")
                                continue

                            # Extract the day name
                            day_name = matching_row[2] if len(matching_row) > 2 else "Unknown"

                            # Ensure row has enough columns for all time slots
                            while len(matching_row) < len(expected_headers):
                                matching_row.append("□")

                            # Display current time slots in horizontal table
                            row_data = matching_row[3:]  # Start from time slots
                            print(f"\nCurrent Time Slots for {date} ({day_name}):")
                            print(tabulate([["Date"] + time_slots, [date] + row_data], headers="firstrow",
                                           tablefmt="grid"))

                            # Let the user modify specific time slots
                            while True:
                                selected_indices = input(
                                    f"\nEnter the indices of time slots to mark as available for {date} (e.g., 0,1): ").strip()
                                if not selected_indices:  # If input is empty
                                    print("No indices entered. Please try again.")
                                    continue
                                try:
                                    selected_indices = [int(idx) for idx in selected_indices.split(",") if
                                                        idx.isdigit() and 0 <= int(idx) < num_slots]
                                    break  # Exit loop if input is valid
                                except ValueError:
                                    print(
                                        "Invalid input. Please enter indices as integers separated by commas (e.g., 0,1).")

                            # Update the time slots for the matching row
                            for idx in range(num_slots):
                                matching_row[idx + 3] = "■" if idx in selected_indices else "□"

                        # Combine updated user schedule with other users
                        updated_schedules = other_users + updated_user_schedule

                        # Save the updated schedule back to the file
                        with open(file_path, "w", newline='', encoding="utf-8") as file:
                            writer = csv.writer(file)
                            writer.writerow(headers)  # Write headers
                            writer.writerows(updated_schedules)  # Write updated data
                        print("\nYour updated time slots have been saved successfully!")
                        print("\nUpdated Schedule (After Modifications):")
                        print(tabulate(updated_user_schedule, headers=headers, tablefmt="grid"))
                    except Exception as e:
                        print(f"Error modifying time slots: {str(e)}")
                elif modify_choice == '3':  # Back to main menu
                    break
                else:
                    print("Invalid choice. Please select 1, 2, or 3.")
        elif mhwp_choice == '7':  # Reset schedule
            schedule_file = "data/mhwp_schedule.csv"
            initialize_schedule_file(schedule_file)
        elif mhwp_choice == '8':  # Logout
            print("Logout successful. Goodbye!")
            break
        else:
            print("Invalid choice, please select an option between 1 and 7.")







