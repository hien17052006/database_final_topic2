# import library
from db_connection import test_connection, seed_database
from crud import patient_menu, doctor_menu, department_menu, appointment_menu
from reports import invoice_menu, report_menu

def main():
    print("\n" + "="*50)
    print("  HOSPITAL MANAGEMENT SYSTEM")
    print("  NEU - DATCOM Lab")
    print("="*50)

    if not test_connection():
        print("  Cannot connect to database")
        return
    while True:
        print("\n" + "═"*50)
        print("  MAIN MENU")
        print("═"*50)
        print("  1. Patient Management")
        print("  2. Doctor Management")
        print("  3. Department Management")
        print("  4. Appointment Management")
        print("  5. Invoice Management")
        print("  6. Report & Statistic")
        print("  0. Exit")

        choice = input(" Please choose: ").strip()

        if choice == "1": patient_menu()
        elif choice == "2": doctor_menu()
        elif choice == "3": department_menu()
        elif choice == "4": appointment_menu()
        elif choice == "5": invoice_menu()
        elif choice == "6": report_menu()
        elif choice == "0": 
            print("\n See you later \n")
            break
        else: 
            print(" Invalid choice")

if __name__ == "__main__":
    main()