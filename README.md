# database_final_topic2
# HOSPITAL MANAGEMENT SYSTEM (HMS)

Final Project for the **Database Management Systems** course at National Economics University (NEU) - Faculty of Data Science and Artificial Intelligence.

## Overview
The Hospital Management System (HMS) is a robust command-line application designed to digitize and streamline clinical and administrative workflows. It seamlessly integrates a Python-based interface with a highly normalized MySQL database to manage patient records, doctor schedules, medical appointments, and financial invoices.

## Key Features
- **Core Entity Management (CRUD):** Add, update, delete, and search records for Patients, Doctors, and Medical Departments.
- **Appointment Scheduling:** Automated ID generation and real-time conflict prevention using database-level Triggers.
- **Security & Access Control:**
  - Application-Layer Role-Based Access Control (RBAC) with dynamic menu routing for System Admins, Receptionists, and Doctors.
  - Interactive authentication with masked password input (Shoulder-surfing protection).
- **Financial Tracking:** Invoice generation based on medical appointments using Stored Procedures.
- **Reporting & Analytics:** Complex SQL views to generate statistical reports with the capability to export data to CSV format.

## Technology Stack
- **Programming Language:** Python 3.x
- **Relational Database:** MySQL
- **Key Python Libraries:** `mysql-connector-python`, `getpass`, `csv`

## Project Structure
- **`/python app dev`**: Contains all Python source code (`main2.py`, `crud.py`, gen reports.py`, `db_connection.py`).
- **`/sql db setup`**: Contains SQL scripts for schema creation, Stored Procedures, Triggers, UDFs, and security roles.

## Installation & Usage
1. **Database Setup:** - Open MySQL Workbench.
   - Execute the SQL scripts located in the `/sql db setup` folder to build the schema and objects.
2. **Configuration:** - Open `python app dev/db_connection.py` and update the `host`, `user`, and `password` variables to match your local MySQL environment.
3. **Run the Application:** - Open your terminal, navigate to the `/python app dev` directory, and execute:
     ```bash
     python main.py
     ```

## Author
- **Student Name:** Lê Minh Hiển
- **Student ID:** 11247167
- **Class:** Data Science 66A
- **Institution:** National Economics University (NEU)
