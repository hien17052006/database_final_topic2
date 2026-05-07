import getpass
from db_connection import test_connection
from crud import patient_menu, doctor_menu, department_menu, appointment_menu, press_enter
from reports import invoice_menu, report_menu

# 1. Mock User DB
USERS = {
    "admin": {"password": "1232456", "role": "1", "name": "System Admin"},
    "recep": {"password": "123", "role": "2", "name": "Receptionist Desk"},
    "doc01": {"password": "123", "role": "3", "name": "Dr. Smith"}
}

def authenticate():
    print("\n" + "="*50)
    print("  HOSPITAL MANAGEMENT SYSTEM - SECURE LOGIN")
    print("="*50)
    
    username = input("  Username: ").strip().lower()
    # hide password with getpass
    password = getpass.getpass("  Password: ") 

    if username in USERS and USERS[username]["password"] == password:
        user_info = USERS[username]
        print(f"\n  [SUCCESS] Welcome back, {user_info['name']}!")
        return user_info["role"]
    else:
        print("\n  [ERROR] Invalid username or password.")
        press_enter()
        return None

def main():
    if not test_connection():
        print("  Cannot connect to database")
        return
        
    while True:
        role = authenticate()
        if not role:
            continue # Ask to log in again if fail
            
        # Menu loop if log in Successfully
        while True:
            print("\n" + "═"*50)
            if role == "1": print("  MAIN MENU (ADMINISTRATOR)")
            elif role == "2": print("  MAIN MENU (RECEPTIONIST)")
            elif role == "3": print("  MAIN MENU (DOCTOR)")
            print("═"*50)
            
            if role == "2": # Receptionist
                print("  1. Patient Management\n  4. Appointment Management\n  5. Invoice Management\n  0. Logout")
            elif role == "3": # Doctor
                print("  1. Patient Viewer\n  6. Report & Statistic\n  0. Logout")
            else: # Admin
                print("  1. Patient Management\n  2. Doctor Management\n  3. Department Management")
                print("  4. Appointment Management\n  5. Invoice Management\n  6. Report & Statistic\n  0. Logout")

            choice = input("\n Please choose: ").strip()

            if choice == "0":
                print("  Logging out...")
                break # Exit to log in menu
                
            # Direct function
            if role == "1":
                if choice == "1": patient_menu()
                elif choice == "2": doctor_menu()
                elif choice == "3": department_menu()
                elif choice == "4": appointment_menu()
                elif choice == "5": invoice_menu()
                elif choice == "6": report_menu()
            elif role == "2":
                if choice == "1": patient_menu()
                elif choice == "4": appointment_menu()
                elif choice == "5": invoice_menu()
            elif role == "3":
                if choice == "1": patient_menu()
                elif choice == "6": report_menu()

if __name__ == "__main__":
    main()
