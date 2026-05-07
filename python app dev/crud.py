from mysql.connector import Error
from db_connection import get_connection

# ─────────────────────────────────────────────
#  DISPLAY & INPUT HELPERS
# ─────────────────────────────────────────────

def print_table(headers, rows):
    if not rows:
        print("  NO DATA\n")
        return
    col_widths = [
        max(len(str(h)), max(len(str(r[i])) for r in rows))
        for i, h in enumerate(headers)
    ]
    sep  = "+" + "+".join("-" * (w + 2) for w in col_widths) + "+"
    head = "|" + "|".join(f" {str(h):<{w}} " for h, w in zip(headers, col_widths)) + "|"
    print(f"\n  {sep}")
    print(f"  {head}")
    print(f"  {sep}")
    for row in rows:
        line = "|" + "|".join(f" {str(c):<{w}} " for c, w in zip(row, col_widths)) + "|"
        print(f"  {line}")
    print(f"  {sep}")
    print(f"  Total: {len(rows)} row(s)\n")


def inp(msg):
    return input(f"  {msg}: ").strip()


def press_enter():
    input("  Press ENTER to continue...")


def choose(prompt, options):
    """
    Display a numbered menu of options and return the chosen value.
    options: list of strings, e.g. ["Male", "Female"]
    """
    print(f"  {prompt}:")
    for i, opt in enumerate(options, 1):
        print(f"    {i}. {opt}")
    while True:
        raw = input("  Select number: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(options):
            return options[int(raw) - 1]
        print(f"  Invalid — please enter a number between 1 and {len(options)}.")


def confirm(msg):
    """Ask a yes/no question; return True only on 'y'."""
    while True:
        ans = input(f"  {msg} (y/n): ").strip().lower()
        if ans in ("y", "n"):
            return ans == "y"
        print("  Please enter 'y' or 'n'.")


# ─────────────────────────────────────────────
#  PATIENTS
# ─────────────────────────────────────────────

def patient_menu():
    while True:
        print("\n" + "═" * 50)
        print("  PATIENT MANAGEMENT")
        print("═" * 50)
        print("  1. List all patients")
        print("  2. Search patient")
        print("  3. Add patient")
        print("  4. Update patient")
        print("  0. Back")
        choice = inp("Choose")

        if   choice == "1": patient_list_all()
        elif choice == "2": patient_search()
        elif choice == "3": patient_add()
        elif choice == "4": patient_update()
        elif choice == "0": break
        else: print("  Invalid choice.")


def patient_list_all():
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    cursor.execute(
        "SELECT PatientID, PatientName, DateOfBirth, Gender, PhoneNumber "
        "FROM Patients ORDER BY PatientID"
    )
    print_table(["ID", "Full Name", "Date of Birth", "Gender", "Phone"], cursor.fetchall())
    cursor.close(); conn.close()
    press_enter()


def patient_search():
    key = inp("Search by name or phone number").title()
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    cursor.execute(
        "SELECT PatientID, PatientName, DateOfBirth, Gender, Address, PhoneNumber "
        "FROM Patients WHERE PatientName LIKE %s OR PhoneNumber LIKE %s",
        (f"%{key}%", f"%{key}%")
    )
    print_table(["ID", "Full Name", "Date of Birth", "Gender", "Address", "Phone"], cursor.fetchall())
    cursor.close(); conn.close()
    press_enter()


def patient_add():
    print("\n  --- ADD PATIENT ---")
    name   = inp("Full Name").title()
    dob    = inp("Date of Birth (YYYY-MM-DD)")
    gender = choose("Gender", ["Male", "Female"])
    addr   = inp("Address")
    phone  = inp("Phone Number")

    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    try:
        # Use UDF fn_gen_id() to get the next sequential PatientID from DB
        cursor.execute("SELECT fn_gen_id()")
        pid = cursor.fetchone()[0]

        cursor.execute(
            "INSERT INTO Patients VALUES (%s, %s, %s, %s, %s, %s)",
            (pid, name, dob, gender, addr, phone)
        )
        conn.commit()
        print(f"\n  Patient '{name}' added successfully. (ID: {pid})")
    except Error as e:
        print(f"\n  [ERROR] {e}")
    finally:
        cursor.close(); conn.close()
    press_enter()


def patient_update():
    """
    Search by name + phone to locate the patient before updating,
    which is more user-friendly than requiring the PatientID directly.
    """
    print("\n  --- UPDATE PATIENT ---")
    key   = inp("Search patient by name or phone number").title()
    conn  = get_connection()
    if not conn: return
    cursor = conn.cursor()

    # Step 1: find candidates
    cursor.execute(
        "SELECT PatientID, PatientName, PhoneNumber, Address "
        "FROM Patients WHERE PatientName LIKE %s OR PhoneNumber LIKE %s",
        (f"%{key}%", f"%{key}%")
    )
    rows = cursor.fetchall()
    if not rows:
        print("  No patient found.")
        cursor.close(); conn.close()
        press_enter(); return

    print_table(["ID", "Full Name", "Phone", "Address"], rows)

    # Step 2: confirm which patient to update
    pid = inp("Enter PatientID to update").upper()
    if not any(str(r[0]) == pid for r in rows):
        print("  PatientID not in search results. Operation cancelled.")
        cursor.close(); conn.close()
        press_enter(); return

    print("  (Leave blank to keep current value)")
    name  = inp("New Name")
    phone = inp("New Phone Number")
    addr  = inp("New Address")

    fields, values = [], []
    if name:  fields.append("PatientName=%s");  values.append(name)
    if phone: fields.append("PhoneNumber=%s");  values.append(phone)
    if addr:  fields.append("Address=%s");      values.append(addr)

    if not fields:
        print("  No changes applied.")
        cursor.close(); conn.close()
        press_enter(); return

    values.append(pid)
    try:
        cursor.execute(
            f"UPDATE Patients SET {', '.join(fields)} WHERE PatientID=%s", values
        )
        conn.commit()
        print(f"\n  Updated {cursor.rowcount} row(s).")
    except Error as e:
        print(f"\n  [ERROR] {e}")
    finally:
        cursor.close(); conn.close()
    press_enter()


# ─────────────────────────────────────────────
#  DOCTORS
# ─────────────────────────────────────────────

def doctor_menu():
    while True:
        print("\n" + "═" * 50)
        print("  DOCTOR MANAGEMENT")
        print("═" * 50)
        print("  1. List all doctors")
        print("  2. Search doctor")
        print("  3. Add doctor")
        print("  4. Update doctor")
        print("  0. Back")
        choice = inp("Choose")

        if   choice == "1": doctor_list_all()
        elif choice == "2": doctor_search()
        elif choice == "3": doctor_add()
        elif choice == "4": doctor_update()
        elif choice == "0": break
        else: print("  Invalid choice.")


def doctor_list_all():
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    cursor.execute(
        "SELECT d.DoctorID, d.DoctorName, d.Specialty, de.DepartmentName "
        "FROM Doctors d LEFT JOIN Departments de ON d.DepartmentID = de.DepartmentID "
        "ORDER BY d.DoctorID"
    )
    print_table(["ID", "Full Name", "Specialty", "Department"], cursor.fetchall())
    cursor.close(); conn.close()
    press_enter()


def doctor_search():
    keyword = inp("Search by name or specialty").title()
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    cursor.execute(
        "SELECT d.DoctorID, d.DoctorName, d.Specialty, de.DepartmentName "
        "FROM Doctors d LEFT JOIN Departments de ON d.DepartmentID = de.DepartmentID "
        "WHERE d.DoctorName LIKE %s OR d.Specialty LIKE %s",
        (f"%{keyword}%", f"%{keyword}%")
    )
    print_table(["ID", "Full Name", "Specialty", "Department"], cursor.fetchall())
    cursor.close(); conn.close()
    press_enter()


def _pick_department(conn):
    """Display department list and let the user pick one; returns DepartmentID."""
    cursor = conn.cursor()
    cursor.execute("SELECT DepartmentID, DepartmentName FROM Departments ORDER BY DepartmentID")
    rows = cursor.fetchall()
    cursor.close()
    if not rows:
        print("  No departments found. Please add a department first.")
        return None
    print("\n  Available Departments:")
    for i, (did, dname) in enumerate(rows, 1):
        print(f"    {i}. [{did}] {dname}")
    while True:
        raw = input("  Select department number: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(rows):
            return rows[int(raw) - 1][0]
        print(f"  Invalid — please enter a number between 1 and {len(rows)}.")


def doctor_add():
    print("\n  --- ADD DOCTOR ---")
    name      = inp("Full Name").title()
    specialty = inp("Specialty").title()

    conn = get_connection()
    if not conn: return

    dept_id = _pick_department(conn)
    if not dept_id:
        conn.close(); press_enter(); return

    cursor = conn.cursor()
    try:
        # Auto-generate DoctorID: DOC + next sequential number
        cursor.execute(
            "SELECT CONCAT('DOC', LPAD(IFNULL(MAX(CAST(SUBSTRING(DoctorID,4) AS UNSIGNED)),0)+1,3,'0')) "
            "FROM Doctors"
        )
        did = cursor.fetchone()[0]

        cursor.execute(
            "INSERT INTO Doctors VALUES (%s, %s, %s, %s)",
            (did, name, specialty, dept_id)
        )
        conn.commit()
        print(f"\n  Doctor '{name}' added. (ID: {did}, Department: {dept_id})")
    except Error as e:
        print(f"\n  [ERROR] {e}")
    finally:
        cursor.close(); conn.close()
    press_enter()


def doctor_update():
    did = inp("DoctorID to update").upper()
    print("  (Leave blank to keep current value)")
    name      = inp("New Name")
    specialty = inp("New Specialty")

    fields, values = [], []
    if name:      fields.append("DoctorName=%s");  values.append(name)
    if specialty: fields.append("Specialty=%s");   values.append(specialty)

    if not fields:
        print("  No changes applied.")
        press_enter(); return

    values.append(did)
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    try:
        cursor.execute(
            f"UPDATE Doctors SET {', '.join(fields)} WHERE DoctorID=%s", values
        )
        conn.commit()
        print(f"\n  Updated {cursor.rowcount} row(s).")
    except Error as e:
        print(f"\n  [ERROR] {e}")
    finally:
        cursor.close(); conn.close()
    press_enter()


# ─────────────────────────────────────────────
#  DEPARTMENTS
# ─────────────────────────────────────────────

def department_menu():
    while True:
        print("\n" + "═" * 50)
        print("  DEPARTMENT MANAGEMENT")
        print("═" * 50)
        print("  1. List all departments")
        print("  2. Add department")
        print("  3. Rename department")
        print("  0. Back")
        choice = inp("Choose")

        if   choice == "1": dept_list_all()
        elif choice == "2": dept_add()
        elif choice == "3": dept_update()
        elif choice == "0": break
        else: print("  Invalid choice.")


def dept_list_all():
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    # Fixed: added spaces between string literals to avoid broken SQL
    cursor.execute(
        "SELECT de.DepartmentID, de.DepartmentName, COUNT(d.DoctorID) AS DoctorCount "
        "FROM Departments de LEFT JOIN Doctors d ON de.DepartmentID = d.DepartmentID "
        "GROUP BY de.DepartmentID, de.DepartmentName "
        "ORDER BY de.DepartmentID"
    )
    # Fixed: pass fetchall() result as second argument to print_table
    print_table(["ID", "Department Name", "Number of Doctors"], cursor.fetchall())
    cursor.close(); conn.close()
    press_enter()


def dept_add():
    print("\n  --- ADD DEPARTMENT ---")
    name = inp("Department Name").title()

    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    try:
        # Auto-generate DepartmentID: DEPT + next sequential number
        cursor.execute(
            "SELECT CONCAT('DEPT', LPAD(IFNULL(MAX(CAST(SUBSTRING(DepartmentID,5) AS UNSIGNED)),0)+1,3,'0')) "
            "FROM Departments"
        )
        did = cursor.fetchone()[0]

        cursor.execute("INSERT INTO Departments VALUES (%s, %s)", (did, name))
        conn.commit()
        print(f"\n  Department '{name}' added. (ID: {did})")
    except Error as e:
        print(f"\n  [ERROR] {e}")
    finally:
        cursor.close(); conn.close()
    press_enter()


def dept_update():
    """
    Rename a department. Department structure rarely changes;
    only the display name is editable here.
    """
    conn = get_connection()
    if not conn: return

    # Show list before asking for ID so the user can see what exists
    cursor = conn.cursor()
    cursor.execute("SELECT DepartmentID, DepartmentName FROM Departments ORDER BY DepartmentID")
    rows = cursor.fetchall()
    print_table(["ID", "Department Name"], rows)

    did  = inp("DepartmentID to rename").upper()
    name = inp("New Department Name").title()
    if not name:
        print("  No changes applied.")
        cursor.close(); conn.close()
        press_enter(); return

    try:
        cursor.execute(
            "UPDATE Departments SET DepartmentName=%s WHERE DepartmentID=%s", (name, did)
        )
        conn.commit()
        print(f"\n  Updated {cursor.rowcount} row(s).")
    except Error as e:
        print(f"\n  [ERROR] {e}")
    finally:
        cursor.close(); conn.close()
    press_enter()


# ─────────────────────────────────────────────
#  APPOINTMENTS
# ─────────────────────────────────────────────

def appointment_menu():
    while True:
        print("\n" + "═" * 50)
        print("  APPOINTMENT MANAGEMENT")
        print("═" * 50)
        print("  1. View appointments by date")
        print("  2. Today's appointments")
        print("  3. New appointment")
        print("  4. Cancel appointment")
        print("  0. Back")
        choice = inp("Choose")

        if   choice == "1": apt_list_by_date()
        elif choice == "2": apt_today()
        elif choice == "3": apt_add()
        elif choice == "4": apt_delete()
        elif choice == "0": break
        else: print("  Invalid choice.")


def apt_list_by_date():
    import re
    print("\n  (Leave both blank to view this week's appointments)")
    start = inp("From date (YYYY-MM-DD)")
    end   = inp("To date   (YYYY-MM-DD)")

    # Default: current week (Monday → Sunday)
    if not start and not end:
        from datetime import date, timedelta
        today = date.today()
        start = str(today - timedelta(days=today.weekday()))
        end   = str(today + timedelta(days=6 - today.weekday()))
        print(f"  Showing appointments for the week: {start} → {end}")
    elif not re.fullmatch(r"\d{4}-\d{2}-\d{2}", start) or \
         not re.fullmatch(r"\d{4}-\d{2}-\d{2}", end):
        print("  Invalid date format. Use YYYY-MM-DD.")
        press_enter(); return

    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    cursor.execute(
        "SELECT a.AppointmentID, a.AppointmentDate, a.AppointmentTime, "
        "       p.PatientName, d.DoctorName, de.DepartmentName "
        "FROM Appointments a "
        "JOIN Patients    p  ON a.PatientID    = p.PatientID "
        "JOIN Doctors     d  ON a.DoctorID     = d.DoctorID "
        "JOIN Departments de ON d.DepartmentID = de.DepartmentID "
        "WHERE a.AppointmentDate BETWEEN %s AND %s "
        "ORDER BY a.AppointmentDate, a.AppointmentTime",
        (start, end)
    )
    print_table(
        ["ID", "Date", "Time", "Patient", "Doctor", "Department"],
        cursor.fetchall()
    )
    cursor.close(); conn.close()
    press_enter()


def apt_today():
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    try:
        cursor.execute(
            "SELECT AppointmentID, AppointmentTime, PatientName, DoctorName, DepartmentName "
            "FROM vw_today_appt"
        )
        rows = cursor.fetchall()
        from datetime import date
        print(f"\n  Today's Appointments ({date.today()}):")
        print_table(["ID", "Time", "Patient", "Doctor", "Department"], rows)
    except Error as e:
        print(f"\n  [ERROR] View 'vw_today_appt' does not exist. Details: {e}")
    finally:
        cursor.close(); conn.close()
    press_enter()


def apt_add():
    """
    Create a new appointment.
    - Search patient by name/phone; allows registering a new patient on the spot.
    - Pick doctor from a displayed list (by department, then doctor).
    - Validate date and time format before submitting.
    """
    print("\n  --- NEW APPOINTMENT ---")

    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()

    # ── Step 1: locate or register patient ──────────────────────────────
    key = inp("Search patient by name or phone")
    cursor.execute(
        "SELECT PatientID, PatientName, PhoneNumber "
        "FROM Patients WHERE PatientName LIKE %s OR PhoneNumber LIKE %s",
        (f"%{key}%", f"%{key}%")
    )
    p_rows = cursor.fetchall()

    if p_rows:
        print_table(["ID", "Full Name", "Phone"], p_rows)
        if confirm("Use an existing patient from the list above?"):
            pat_id = inp("Enter PatientID")
        else:
            pat_id = None
    else:
        print("  No existing patient found.")
        pat_id = None

    if not pat_id:
        if confirm("Register as a new patient now?"):
            cursor.close(); conn.close()
            patient_add()
            # Re-open connection to continue
            conn = get_connection()
            if not conn: return
            cursor = conn.cursor()
            cursor.execute(
                "SELECT PatientID FROM Patients ORDER BY PatientID DESC LIMIT 1"
            )
            row = cursor.fetchone()
            pat_id = row[0] if row else None
            if not pat_id:
                print("  Could not retrieve new patient ID.")
                cursor.close(); conn.close()
                press_enter(); return
        else:
            print("  Appointment cancelled.")
            cursor.close(); conn.close()
            press_enter(); return

    # ── Step 2: pick doctor ──────────────────────────────────────────────
    dept_id = _pick_department(conn)
    if not dept_id:
        cursor.close(); conn.close(); press_enter(); return

    cursor.execute(
        "SELECT DoctorID, DoctorName, Specialty FROM Doctors WHERE DepartmentID=%s ORDER BY DoctorID",
        (dept_id,)
    )
    doc_rows = cursor.fetchall()
    if not doc_rows:
        print("  No doctors found in this department.")
        cursor.close(); conn.close(); press_enter(); return

    print("\n  Available Doctors:")
    for i, (did, dname, spec) in enumerate(doc_rows, 1):
        print(f"    {i}. [{did}] {dname} — {spec}")
    while True:
        raw = input("  Select doctor number: ").strip()
        if raw.isdigit() and 1 <= int(raw) <= len(doc_rows):
            doc_id = doc_rows[int(raw) - 1][0]
            break
        print(f"  Invalid — enter 1 to {len(doc_rows)}.")

    # ── Step 3: date and time with basic format validation ───────────────
    import re
    while True:
        adate = inp("Appointment Date (YYYY-MM-DD)")
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", adate):
            break
        print("  Invalid format. Use YYYY-MM-DD (e.g. 2025-06-15).")

    while True:
        atime = inp("Appointment Time (HH:MM)")
        if re.fullmatch(r"\d{2}:\d{2}", atime):
            atime += ":00"   # normalise to HH:MM:SS for TIME column
            break
        print("  Invalid format. Use HH:MM (e.g. 09:30).")

    # ── Step 4: auto-generate AppointmentID & insert ─────────────────────
    try:
        cursor.execute(
            "SELECT CONCAT('APT', LPAD(IFNULL(MAX(CAST(SUBSTRING(AppointmentID,4) AS UNSIGNED)),0)+1,3,'0')) "
            "FROM Appointments"
        )
        apt_id = cursor.fetchone()[0]

        cursor.callproc("sp_add_appt", [apt_id, doc_id, pat_id, adate, atime, ""])
        conn.commit()

        # Read OUT parameter
        cursor.execute("SELECT @_sp_add_appt_5")
        msg = cursor.fetchone()[0]
        print(f"\n  {msg}")
    except Error:
        # Fallback if stored procedure does not exist
        try:
            cursor.execute(
                "INSERT INTO Appointments (AppointmentID, AppointmentDate, AppointmentTime, DoctorID, PatientID) "
                "VALUES (%s, %s, %s, %s, %s)",
                (apt_id, adate, atime, doc_id, pat_id)
            )
            conn.commit()
            print(f"\n  Appointment {apt_id} created successfully.")
        except Error as e2:
            print(f"\n  [ERROR] {e2}")
    finally:
        cursor.close(); conn.close()
    press_enter()


def apt_delete():
    """
    Cancel an appointment.
    - Looks up the appointment and previews it before confirming.
    - Blocks cancellation if a linked invoice already exists (medical record
      integrity). The database trigger trg_block_apt_delete enforces the same
      rule at the DB level as a safety net.
    """
    apt_id = inp("AppointmentID to cancel").upper()

    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()

    # Preview appointment details
    cursor.execute(
        "SELECT a.AppointmentID, a.AppointmentDate, a.AppointmentTime, "
        "       p.PatientName, d.DoctorName "
        "FROM Appointments a "
        "JOIN Patients p ON a.PatientID = p.PatientID "
        "JOIN Doctors  d ON a.DoctorID  = d.DoctorID "
        "WHERE a.AppointmentID=%s",
        (apt_id,)
    )
    row = cursor.fetchone()
    if not row:
        print(f"  No appointment found with ID '{apt_id}'.")
        cursor.close(); conn.close()
        press_enter(); return

    print(f"\n  Found: [{row[0]}] {row[3]} with Dr. {row[4]} on {row[1]} at {row[2]}")

    # Check whether a linked invoice exists
    cursor.execute(
        "SELECT COUNT(*) FROM Invoices WHERE AppointmentID=%s", (apt_id,)
    )
    inv_count = cursor.fetchone()[0]
    if inv_count > 0:
        print(f"\n  [BLOCKED] This appointment has {inv_count} linked invoice(s).")
        print("  Appointments with issued invoices cannot be cancelled.")
        cursor.close(); conn.close()
        press_enter(); return

    if not confirm("Cancel this appointment?"):
        print("  Operation cancelled.")
        cursor.close(); conn.close()
        press_enter(); return

    try:
        cursor.execute("DELETE FROM Appointments WHERE AppointmentID=%s", (apt_id,))
        conn.commit()
        if cursor.rowcount:
            print(f"\n  Appointment {apt_id} has been cancelled.")
        else:
            print(f"\n  No appointment with ID '{apt_id}' found.")
    except Error as e:
        # Trigger trg_block_apt_delete will raise a signal if a race condition
        # somehow bypasses the Python check above.
        print(f"\n  [ERROR] {e}")
    finally:
        cursor.close(); conn.close()
    press_enter()
