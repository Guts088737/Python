import os
import csv
from tabulate import tabulate
import random


def initialize_assignments(assignments_path="data/assignments.csv"):
    """
    Clear all data in the assignments.csv file and keep only the column headers.
    """
    try:
        with open(assignments_path, "w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["patient_username", "mhwp_username"])  # Write headers only
        print("\nAssignments file has been initialized. All data cleared.")
    except Exception as e:
        print(f"Error initializing assignments: {str(e)}")


def get_users_by_role(role, user_data_path="data/user_data.csv"):
    """
    Get a list of usernames by role from user_data.csv.
    """
    users = []
    if not os.path.exists(user_data_path):
        print(f"Error: User data file '{user_data_path}' not found.")
        return users

    try:
        with open(user_data_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["role"] == role:
                    users.append(row["username"])
    except Exception as e:
        print(f"Error reading user data: {str(e)}")
    return users


def get_mhwps_with_schedule(schedule_path="data/mhwp_schedule.csv"):
    """
    Get a list of MHWPs that have an available schedule in mhwp_schedule.csv.
    """
    mhwps_with_schedule = set()
    if not os.path.exists(schedule_path):
        print(f"Error: Schedule file '{schedule_path}' not found.")
        return mhwps_with_schedule

    try:
        with open(schedule_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                if row["mhwp_username"] and any(value == "□" for value in row.values()):
                    mhwps_with_schedule.add(row["mhwp_username"])
    except Exception as e:
        print(f"Error reading schedule: {str(e)}")

    return mhwps_with_schedule


def get_current_assignments(assignments_path="data/assignments.csv"):
    """
    Load current assignments from assignments.csv.
    """
    assignments = {}
    if os.path.exists(assignments_path):
        with open(assignments_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            for row in reader:
                mhwp_username = row["mhwp_username"]
                patient_username = row["patient_username"]
                if mhwp_username not in assignments:
                    assignments[mhwp_username] = []
                assignments[mhwp_username].append(patient_username)
    return assignments


def save_assignments(assignments, assignments_path="data/assignments.csv"):
    """
    Save assignments to assignments.csv.
    """
    table_data = []
    for mhwp, patients in assignments.items():
        for patient in patients:
            table_data.append([patient, mhwp])

    with open(assignments_path, "w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["patient_username", "mhwp_username"])
        writer.writerows(table_data)

    print("\nUpdated Assignments:")
    print(tabulate(table_data, headers=["Patient Username", "MHWP Username"], tablefmt="grid"))


def balanced_assign_patients_and_mhwps(user_data_path="data/user_data.csv",
                                       assignments_path="data/assignments.csv",
                                       schedule_path="data/mhwp_schedule.csv"):
    """
    Assign patients to MHWPs in a balanced way, prioritizing unassigned MHWPs.
    """
    all_patients = set(get_users_by_role("patient", user_data_path))
    eligible_mhwps = get_mhwps_with_schedule(schedule_path)

    current_assignments = get_current_assignments(assignments_path)
    assigned_patients = {patient for patients in current_assignments.values() for patient in patients}
    unassigned_patients = list(all_patients - assigned_patients)
    unassigned_mhwps = list(eligible_mhwps - set(current_assignments.keys()))

    assignments = {mhwp: patients.copy() for mhwp, patients in current_assignments.items()}
    for mhwp in unassigned_mhwps:
        assignments[mhwp] = []

    # Randomly assign u7nassigned patients to unassigned MHWPs
    for patient in unassigned_patients:
        if unassigned_mhwps:
            mhwp = unassigned_mhwps.pop()
            assignments[mhwp].append(patient)
        else:
            # Assign to MHWP with the least patients
            mhwp_with_least_patients = min(assignments, key=lambda x: len(assignments[x]))
            assignments[mhwp_with_least_patients].append(patient)

    save_assignments(assignments, assignments_path)


def modify_assignments(assignments_path="data/assignments.csv", user_data_path="data/user_data.csv"):
    """
    Modify the existing assignments in the assignments file or assign unassigned users.
    """
    current_assignments = get_current_assignments(assignments_path)
    print("\nCurrent Assignments:")
    display_assignments(assignments_path, user_data_path)

    print("\nModify Assignments Options:")
    print("1. Modify an existing assignment")
    print("2. Assign unassigned patients and MHWPs")

    choice = input("\nEnter your choice (1-2): ").strip()

    if choice == '1':  # modify the existing assignment
        patient_to_modify = input("\nEnter the patient username to modify assignment: ").strip()
        # check if patients are in current_assignment or not
        if patient_to_modify not in {p for ps in current_assignments.values() for p in ps}:
            print(f"Patient '{patient_to_modify}' not found in current assignments.")
            return
        # new mhwp
        new_mhwp = input(f"Enter the new MHWP username for {patient_to_modify}: ").strip()
        # check new_mhwp
        all_mhwps = set(current_assignments.keys())
        if new_mhwp not in all_mhwps:
            print(f"MHWP '{new_mhwp}' not found in current assignments.")
            return
        # delete past assignment of patients
        for mhwp, patients in current_assignments.items():
            if patient_to_modify in patients:
                patients.remove(patient_to_modify)
                break
        # add patient to new_mhw
        current_assignments[new_mhwp].append(patient_to_modify)
        current_assignments = {mhwp: list(set(patients)) for mhwp, patients in current_assignments.items()}
        save_assignments(current_assignments, assignments_path)
        print("\nUpdated Assignments:")
        display_assignments(assignments_path, user_data_path)

    elif choice == '2':  #reassign for unassigned patients and mhwps
        print("\n--- Assigning unassigned patients and MHWPs ---")

        all_patients = set(get_users_by_role("patient", user_data_path))
        all_mhwps = set(get_users_by_role("mhwp", user_data_path))

        current_assignments = get_current_assignments(assignments_path)
        assigned_patients = {patient for patients in current_assignments.values() for patient in patients}
        assigned_mhwps = set(current_assignments.keys())

        unassigned_patients = all_patients - assigned_patients
        unassigned_mhwps = all_mhwps - assigned_mhwps

        # check if unassigned mhwps have available schedule or not
        mhwps_with_schedule = get_mhwps_with_schedule("data/mhwp_schedule.csv")
        mhwps_without_schedule = set(unassigned_mhwps) - mhwps_with_schedule

        # no new_patient and unassigned mhwps who dont have available schedule
        if not unassigned_patients and mhwps_without_schedule:
            print("\nUnassigned MHWPs don't set available schedule:")
            mhwp_table = [{"MHWP Username": mhwp, "Status": "No Schedule"} for mhwp in mhwps_without_schedule]
            print(tabulate(mhwp_table, headers="keys", tablefmt="grid"))

        # no new_patient and unassigned mhwps whp have available schedule
        elif not unassigned_patients and mhwps_with_schedule:
            unassigned_and_available_mhwps = mhwps_with_schedule - set(current_assignments.keys())
            if unassigned_and_available_mhwps:
                print("\nAll patients have been assigned. The following MHWPs are available but unassigned:")
                mhwp_table = [{"MHWP Username": mhwp} for mhwp in unassigned_and_available_mhwps]
                print(tabulate(mhwp_table, headers="keys", tablefmt="grid"))
            else:
                print("\nAll patients have been assigned, and no MHWPs are unassigned with an available schedule.")

        # new patient and unassigned mhwps who have available schedule
        elif unassigned_patients and unassigned_mhwps & mhwps_with_schedule:
            print("\nAssigning new patients to available MHWPs...")

            available_unassigned_mhwps = list(unassigned_mhwps & mhwps_with_schedule)
            print(f"Available Unassigned MHWPs: {available_unassigned_mhwps}")

            for patient in list(unassigned_patients):
                if available_unassigned_mhwps:
                    mhwp = available_unassigned_mhwps.pop()
                    current_assignments.setdefault(mhwp, []).append(patient)
                    unassigned_patients.remove(patient)
                    print(f"Assigned: {patient} -> {mhwp}")

        # new patient and assigned mhwps who have available schedule
        elif unassigned_patients and mhwps_with_schedule.issubset(set(current_assignments.keys())):
            print("\nAll MHWPs with available schedules are assigned patients.")

            # ensure mhwps who have available schedule are in current_assignement
            for mhwp in mhwps_with_schedule:
                if mhwp not in current_assignments:
                    current_assignments[mhwp] = []

            # assign new patients to mhwps who have min patients
            for patient in list(unassigned_patients):
                if current_assignments:
                    mhwp_with_least_patients = min(
                        current_assignments,
                        key=lambda mhwp: len(current_assignments[mhwp])
                    )
                    print(f"Assigning patient {patient} to MHWP {mhwp_with_least_patients}...")
                    current_assignments[mhwp_with_least_patients].append(patient)
                    unassigned_patients.remove(patient)
                else:
                    print(f"No MHWP available to assign patient {patient}. Skipping.")

            save_assignments(current_assignments, assignments_path)


    else:
        print("\nInvalid choice. Returning to menu.")
        return


def display_unassigned_users(user_data_path="data/user_data.csv", assignments_path="data/assignments.csv"):
    """
    Display unassigned patients and MHWPs in a table format.
    """
    all_patients = set(get_users_by_role("patient", user_data_path))
    all_mhwps = set(get_users_by_role("mhwp", user_data_path))

    current_assignments = get_current_assignments(assignments_path)
    assigned_patients = {patient for patients in current_assignments.values() for patient in patients}
    assigned_mhwps = set(current_assignments.keys())

    unassigned_patients = all_patients - assigned_patients
    unassigned_mhwps = all_mhwps - assigned_mhwps

    table_data = [{"Name": user, "Role": "Patient", "Status": "Unassigned"} for user in unassigned_patients]
    table_data.extend({"Name": user, "Role": "MHWP", "Status": "Unassigned"} for user in unassigned_mhwps)

    if table_data:
        print("\nUnassigned Patients and MHWPs:")
        print(tabulate(table_data, headers="keys", tablefmt="grid"))
    else:
        print("\nAll patients and MHWPs are assigned.")



def display_assignments(assignments_path="data/assignments.csv", user_data_path="data/user_data.csv"):
    """
    Display all current assignments in a table format.
    """
    current_assignments = get_current_assignments(assignments_path)
    table_data = [{"Patient Username": patient, "MHWP Username": mhwp}
                  for mhwp, patients in current_assignments.items() for patient in patients]

    print("\nCurrent Assignments:")
    if table_data:
        print(tabulate(table_data, headers="keys", tablefmt="grid"))
    else:
        print("No assignments found.")

def handle_admin_menu(user):
    """
    Admin menu to manage assignments, view unassigned users, and modify user data.
    """
    while True:
        print("\nAdmin Options:")
        print("1. Update Another User's Info")
        print("2. Delete Another User")
        print("3. View System Statistics")
        print("4. View All Assignments")
        print("5. Assign Patients to MHWPs")
        print("6. Modify Assignments")
        print("7. Initialize Assignments")  # Reset assignments
        print("8. Display Unassigned Patients and MHWPs")
        print("9. Logout")

        admin_choice = input("Select an option (1-9): ").strip()

        if admin_choice == '1':  # Update another user's info
            target_username = input("Enter the username to update: ").strip()
            new_username = input("Enter the new username (blank to keep): ").strip()
            new_password = input("Enter the new password (blank to keep): ").strip()
            new_email = input("Enter the new email (blank to keep): ").strip()
            new_emergency_email = input("Enter the new emergency email (blank to keep): ").strip()

            user.admin_update_user(
                target_username,
                new_username or None,
                new_password or None,
                new_email or None,
                new_emergency_email or None
            )

        elif admin_choice == '2':  # Delete another user
            target_username = input("Enter the username to delete: ").strip()
            user.admin_delete_user(target_username)

        elif admin_choice == '3':  # View system statistics
            print("\nSystem statistics feature coming soon...")

        elif admin_choice == '4':  # View all assignments
            print("\n--- All Assignments ---")
            display_assignments("data/assignments.csv", "data/user_data.csv")

        elif admin_choice == '5':  # Assign patients to MHWPs
            print("\n--- Assigning Patients to MHWPs ---")
            balanced_assign_patients_and_mhwps(
                user_data_path="data/user_data.csv",
                assignments_path="data/assignments.csv",
                schedule_path="data/mhwp_schedule.csv"
            )
            print("\n--- Updated Assignments ---")
            display_assignments("data/assignments.csv", "data/user_data.csv")

        elif admin_choice == '6':  # Modify Assignments
            print("\n--- Modify Assignments ---")
            modify_assignments(
                assignments_path="data/assignments.csv",
                user_data_path="data/user_data.csv"
            )

        elif admin_choice == '7':  # Initialize Assignments
            print("\n--- Initializing Assignments ---")
            initialize_assignments("data/assignments.csv")
            print("Assignments have been reset.")

        elif admin_choice == '8':  # Display unassigned users
            print("\n--- Unassigned Patients and MHWPs ---")
            display_unassigned_users(
                user_data_path="data/user_data.csv",
                assignments_path="data/assignments.csv"
            )

        elif admin_choice == '9':  # Logout
            print("Logging out of admin session.")
            break

        else:
            print("Invalid choice, please try again.")
