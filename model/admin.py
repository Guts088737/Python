import os
import csv
from tabulate import tabulate


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



def display_assignments(assignments_path="data/assignments.csv", user_data_path="data/user_data.csv"):
    """
    Display all current assignments and unassigned users in a table format.
    """
    # 检查文件是否存在
    if not os.path.exists(assignments_path):
        print("\nNo assignments found.")
        return

    try:
        # 加载当前分配的用户
        with open(assignments_path, "r", encoding="utf-8") as file:
            reader = csv.DictReader(file)
            assignments = list(reader)

        # 显示已分配用户
        if assignments:
            print("\nCurrent Assignments:")
            print(tabulate(assignments, headers="keys", tablefmt="grid"))
        else:
            print("\nNo assignments found.")

        # 加载所有用户
        all_patients = set(get_users_by_role("patient", user_data_path))
        all_mhwps = set(get_users_by_role("mhwp", user_data_path))

        # 获取已分配的病人和 MHWPs
        assigned_patients = {row["patient_username"] for row in assignments}
        assigned_mhwps = {row["mhwp_username"] for row in assignments}

        # 计算未分配的病人和 MHWPs
        unassigned_patients = all_patients - assigned_patients
        unassigned_mhwps = all_mhwps - assigned_mhwps

        #  Prepare data for table display
        print("\nCurrent Assignments:")
        if assignments:
            print(tabulate(assignments, headers="keys", tablefmt="grid"))
        else:
            print("No assignments found.")

        # Step 5: Display unassigned patients and MHWPs in table format
        unassigned_table = []
        for patient in unassigned_patients:
            unassigned_table.append({"name": patient, "role": "patient", "status": "Unassigned"})
        for mhwp in unassigned_mhwps:
            unassigned_table.append({"name": mhwp, "role": "mhwp", "status": "Unassigned"})

        if unassigned_table:
            print("\nUnassigned Patients and MHWPs:")
            print(tabulate(unassigned_table, headers="keys", tablefmt="grid"))
        else:
            print("\nAll patients and MHWPs are assigned.")

    except Exception as e:
        print(f"Error reading assignments: {str(e)}")



def modify_assignments(assignments_path="data/assignments.csv", user_data_path="data/user_data.csv"):
    """
    Modify the existing assignments in the assignments file or assign unassigned users.
    """
    # 检查文件是否存在
    if not os.path.exists(assignments_path):
        print("\nNo assignments found. Please assign patients to MHWPs first.")
        return

    # 显示当前分配和未分配用户
    display_assignments(assignments_path, user_data_path)

    # 加载现有分配
    assignments = []
    with open(assignments_path, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        assignments = list(reader)

    if not assignments:
        print("\nNo assignments found. Please assign patients to MHWPs first.")
        return

    # 显示选项
    print("\nModify Assignments Options:")
    print("1. Modify an existing assignment")
    print("2. Assign unassigned patients and MHWPs")
    choice = input("\nEnter your choice (1-2): ").strip()

    if choice == '1':
        # 修改现有分配
        patients = [row["patient_username"] for row in assignments]
        mhwps = list(set(row["mhwp_username"] for row in assignments))

        print("\nAvailable Patients and MHWPs:")
        print("Patients:", ", ".join(patients))
        print("MHWPs:", ", ".join(mhwps))

        # 获取需要修改的病人
        patient_to_modify = input("\nEnter the patient username to modify assignment: ").strip()
        if patient_to_modify not in patients:
            print(f"\nError: Patient '{patient_to_modify}' not found in current assignments.")
            return

        # 获取新分配的 MHWP
        new_mhwp = input(f"Enter the new MHWP username for {patient_to_modify}: ").strip()
        if new_mhwp not in mhwps:
            print(f"\nError: MHWP '{new_mhwp}' not found.")
            return

        # 更新分配
        for row in assignments:
            if row["patient_username"] == patient_to_modify:
                row["mhwp_username"] = new_mhwp

        print(f"\nAssignment updated: {patient_to_modify} -> {new_mhwp}")

    elif choice == '2':
        all_patients = set(get_users_by_role("patient", user_data_path))
        all_mhwps = set(get_users_by_role("mhwp", user_data_path))

        # 获取已分配的病人和 MHWPs
        assigned_patients = {row["patient_username"] for row in assignments}
        assigned_mhwps = {row["mhwp_username"] for row in assignments}

        # 计算未分配的病人和 MHWPs
        unassigned_patients = all_patients - assigned_patients
        unassigned_mhwps = all_mhwps - assigned_mhwps

        # 为未分配的病人分配 MHWP
        for patient in unassigned_patients:
            if unassigned_mhwps:
                mhwp = unassigned_mhwps.pop()  # 从未分配的 MHWPs 中取出一个
                assignments.append({"patient_username": patient, "mhwp_username": mhwp})
                print(f"Assigned: {patient} -> {mhwp}")
            else:
                # 如果没有未分配的 MHWP，则分配给当前拥有最少病人的 MHWP
                mhwp_with_least_patients = min(assignments, key=lambda x: len(x["mhwp_username"]))
                assignments.append({"patient_username": patient, "mhwp_username": mhwp_with_least_patients})

    else:
        print("\nInvalid choice. Returning to menu.")
        return

    # save file
    with open(assignments_path, "w", newline='', encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=["patient_username", "mhwp_username"])
        writer.writeheader()
        writer.writerows(assignments)

    print("\nUpdated Assignments:")
    print(tabulate(assignments, headers="keys", tablefmt="grid"))



def display_unassigned_users(user_data_path="data/user_data.csv", assignments_path="data/assignments.csv"):
    """
    Display unassigned patients and MHWPs in a table format.
    """
    # Get all patients and MHWPs from user data
    all_patients = set(get_users_by_role("patient", user_data_path))
    all_mhwps = set(get_users_by_role("mhwp", user_data_path))

    # Get already assigned patients and MHWPs
    current_assignments = get_current_assignments(assignments_path)
    assigned_patients = set()
    assigned_mhwps = set(current_assignments.keys())

    for assigned_list in current_assignments.values():
        assigned_patients.update(assigned_list)

    # Calculate unassigned patients and MHWPs
    unassigned_patients = all_patients - assigned_patients
    unassigned_mhwps = all_mhwps - assigned_mhwps

    # Prepare table data
    table_data = []
    for patient in unassigned_patients:
        table_data.append([patient, "patient", "Unassigned"])
    for mhwp in unassigned_mhwps:
        table_data.append([mhwp, "mhwp", "Unassigned"])

    # Print table using tabulate
    if table_data:
        print("\nUnassigned Patients and MHWPs:")
        print(tabulate(table_data, headers=["Name", "Role", "Status"], tablefmt="grid"))
    else:
        print("\nAll patients and MHWPs are assigned.")


def balanced_assign_patients_and_mhwps(user_data_path="data/user_data.csv",
                                       assignments_path="data/assignments.csv",
                                       schedule_path="data/mhwp_schedule.csv"):
    """
    Assign patients to MHWPs in a balanced way, prioritizing MHWPs with a schedule.
    Only MHWPs listed in mhwp_schedule.csv are considered for assignment.
    """
    if not os.path.exists(assignments_path):
        with open(assignments_path, "w", newline='', encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["patient_username", "mhwp_username"])

    # obtain all patient and mhwp
    all_patients = get_users_by_role("patient", user_data_path)
    all_mhwps = get_users_by_role("mhwp", user_data_path)

    # obtain available schedule
    mhwps_with_schedule = get_mhwps_with_schedule(schedule_path)
    eligible_mhwps = set(all_mhwps) & mhwps_with_schedule

    if not eligible_mhwps:
        print("\nNo eligible MHWPs with a schedule found. Please ensure MHWPs have set their availability.")
        return

    # load current assignments
    current_assignments = get_current_assignments(assignments_path)
    assigned_patients = {patient for patients in current_assignments.values() for patient in patients}
    assigned_mhwps = set(current_assignments.keys())

    # unassigned_patients
    unassigned_patients = set(all_patients) - assigned_patients
    unassigned_mhwps = eligible_mhwps - assigned_mhwps

    assignments = {mhwp: patients.copy() for mhwp, patients in current_assignments.items()}
    for mhwp in unassigned_mhwps:
        assignments[mhwp] = []

    # priority to assign unassigned patient
    for patient in list(unassigned_patients):
        if unassigned_mhwps:
            mhwp = unassigned_mhwps.pop()
            assignments[mhwp].append(patient)
            unassigned_patients.remove(patient)

    # make sure to unassigned patients to unassigned mhwp or mhwps who have at least patients
    for patient in unassigned_patients:
        # assign unassigned patients to mhwps who have at least patients if no unassigned mhwp
        mhwp_with_least_patients = min(assignments, key=lambda mhwp: len(assignments[mhwp]))
        assignments[mhwp_with_least_patients].append(patient)
        print(f"Assigned: {patient} -> {mhwp_with_least_patients}")

    table_data = []
    seen_patients = set()
    for mhwp, patients in assignments.items():
        for patient in patients:
            if patient not in seen_patients:
                table_data.append([patient, mhwp])
                seen_patients.add(patient)

    # save file
    with open(assignments_path, "w", newline='', encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["patient_username", "mhwp_username"])
        for patient, mhwp in table_data:
            writer.writerow([patient, mhwp])

    print("\nUpdated assignments have been saved successfully.")




def handle_admin_menu(user):
    while True:
        print("\nAdmin Options:")
        print("1. Update Another User's Info")
        print("2. Delete Another User")
        print("3. View System Statistics")
        print("4. View All Assignments")
        print("5. Assign Patients to MHWPs")
        print("6. Modify Assignments")
        print("7. Initialize Assignments")  # New option for initializing assignments
        print("8. Display Unassigned Patients and MHWPs")
        print("9. Logout")

        admin_choice = input("Select an option (1-8): ").strip()

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
            display_assignments("data/assignments.csv")

        elif admin_choice == '5':  # Assign patients to MHWPs
            balanced_assign_patients_and_mhwps("data/user_data.csv", "data/assignments.csv")

        elif admin_choice == '6':  # Modify Assignments
            modify_assignments("data/assignments.csv", "data/user_data.csv")

        elif admin_choice == '7':  # Initialize Assignments
            initialize_assignments("data/assignments.csv")

        elif admin_choice == '8':
            display_unassigned_users("data/user_data.csv", "data/assignments.csv")

        elif admin_choice == '9':  # Logout
            print("Logging out of admin session.")
            break

        else:
            print("Invalid choice, please try again.")