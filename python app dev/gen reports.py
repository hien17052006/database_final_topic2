import os
import csv
from datetime import date, datetime
from mysql.connector import Error
from db_connection import get_connection
from crud import print_table, inp, press_enter, confirm

# ─────────────────────────────────────────────
#  REPORT EXPORT HELPER
# ─────────────────────────────────────────────

REPORT_DIR = "reports"

def _ensure_report_dir():
    os.makedirs(REPORT_DIR, exist_ok=True)

def _export_csv(filename, headers, rows):
    """Write rows to a CSV file inside the reports/ directory."""
    _ensure_report_dir()
    path = os.path.join(REPORT_DIR, filename)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)
    print(f"\n  Report saved → {path}")
    return path

def _timestamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


# ─────────────────────────────────────────────
#  BILLING / INVOICE MODULE
# ─────────────────────────────────────────────

def invoice_menu():
    while True:
        print("\n" + "═" * 50)
        print("  BILLING MANAGEMENT")
        print("═" * 50)
        print("  1. Create new invoice  [STORED PROCEDURE]")
        print("  2. View invoices by patient")
        print("  0. Back")
        choice = inp("Choose")

        if   choice == "1": _invoice_create()
        elif choice == "2": _invoice_by_patient()
        elif choice == "0": break
        else: print("  Invalid choice.")


def _invoice_create():
    """Call Stored Procedure sp_gen_inv to create a new invoice."""
    print("\n  --- CREATE NEW INVOICE ---")

    # Search patient by name/phone instead of requiring PatientID directly
    key = inp("Search patient by name or phone")
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    cursor.execute(
        "SELECT PatientID, PatientName, DateOfBirth, PhoneNumber "
        "FROM Patients WHERE PatientName LIKE %s OR PhoneNumber LIKE %s",
        (f"%{key}%", f"%{key}%")
    )
    p_rows = cursor.fetchall()
    if not p_rows:
        print("  No patient found.")
        cursor.close(); conn.close(); press_enter(); return

    print_table(["ID", "Full Name", "Date of Birth", "Phone"], p_rows)
    pat_id = inp("Enter PatientID")
    if not any(str(r[0]) == pat_id for r in p_rows):
        print("  PatientID not in search results. Operation cancelled.")
        cursor.close(); conn.close(); press_enter(); return

    amount = inp("Total Amount (VND)")
    try:
        float(amount)
    except ValueError:
        print("  Invalid amount.")
        cursor.close(); conn.close(); press_enter(); return

    try:
        # Auto-generate InvoiceID
        cursor.execute(
            "SELECT CONCAT('INV', LPAD(IFNULL(MAX(CAST(SUBSTRING(InvoiceID,4) AS UNSIGNED)),0)+1,3,'0')) "
            "FROM Invoices"
        )
        inv_id = cursor.fetchone()[0]

        cursor.callproc("sp_gen_inv", [inv_id, pat_id, float(amount), ""])
        conn.commit()
        cursor.execute("SELECT @_sp_gen_inv_3")
        msg = cursor.fetchone()[0]
        print(f"\n  → {msg}")
    except Error:
        # Fallback if stored procedure does not exist
        try:
            cursor.execute(
                "INSERT INTO Invoices VALUES (%s, CURDATE(), %s, %s)",
                (inv_id, float(amount), pat_id)
            )
            conn.commit()
            print(f"\n  Invoice {inv_id} created — {int(float(amount)):,} VND")
        except Error as e2:
            print(f"\n  [ERROR] {e2}")
    finally:
        cursor.close(); conn.close()
    press_enter()


def _invoice_by_patient():
    """
    View all invoices for a patient.
    Displays patient demographic information at the top for identification,
    followed by an itemised invoice list and cumulative total.
    """
    key = inp("Search patient by name or phone")
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()

    cursor.execute(
        "SELECT PatientID, PatientName, DateOfBirth, Gender, Address, PhoneNumber "
        "FROM Patients WHERE PatientName LIKE %s OR PhoneNumber LIKE %s",
        (f"%{key}%", f"%{key}%")
    )
    p_rows = cursor.fetchall()
    if not p_rows:
        print("  No patient found.")
        cursor.close(); conn.close(); press_enter(); return

    print_table(["ID", "Full Name", "Date of Birth", "Gender", "Address", "Phone"], p_rows)
    pat_id = inp("Enter PatientID")
    match = next((r for r in p_rows if str(r[0]) == pat_id), None)
    if not match:
        print("  PatientID not in search results. Operation cancelled.")
        cursor.close(); conn.close(); press_enter(); return

    # ── Patient header (invoice-style) ──────────────────────────────────
    pid, pname, dob, gender, addr, phone = match
    age_row = None
    try:
        cursor.execute("SELECT fn_cal_age(%s)", (dob,))
        age_row = cursor.fetchone()[0]
    except Error:
        pass
    age_str = f"{age_row} years old" if age_row is not None else str(dob)

    print("\n" + "─" * 55)
    print("  PATIENT INVOICE SUMMARY")
    print("─" * 55)
    print(f"  ID       : {pid}")
    print(f"  Name     : {pname}")
    print(f"  Gender   : {gender}    Age: {age_str}")
    print(f"  Address  : {addr}")
    print(f"  Phone    : {phone}")
    print("─" * 55)

    # ── Invoice list ─────────────────────────────────────────────────────
    cursor.execute(
        "SELECT i.InvoiceID, i.InvoiceDate, FORMAT(i.TotalAmount, 0) "
        "FROM Invoices i WHERE i.PatientID=%s ORDER BY i.InvoiceDate DESC",
        (pat_id,)
    )
    inv_rows = cursor.fetchall()
    cursor.execute(
        "SELECT SUM(TotalAmount) FROM Invoices WHERE PatientID=%s", (pat_id,)
    )
    total = cursor.fetchone()[0] or 0
    cursor.close(); conn.close()

    print_table(["Invoice ID", "Date", "Amount (VND)"], inv_rows)
    print(f"  Cumulative total: {int(total):,} VND\n")
    press_enter()


# ─────────────────────────────────────────────
#  REPORTS & STATISTICS  (medical context)
# ─────────────────────────────────────────────

def report_menu():
    while True:
        print("\n" + "═" * 50)
        print("  REPORTS & STATISTICS")
        print("═" * 50)
        print("  1. Billing summary by date range  [STORED PROCEDURE]")
        print("  2. Appointment count by department [VIEW]")
        print("  3. Patient distribution by age group  [UDF]")
        print("  0. Back")
        choice = inp("Choose")

        if   choice == "1": _report_billing_summary()
        elif choice == "2": _report_dept_workload()
        elif choice == "3": _report_age_group()
        elif choice == "0": break
        else: print("  Invalid choice.")


def _report_billing_summary():
    """
    Medical billing summary over a date range.
    Shows daily invoice count and total billed amount.
    Calls sp_revenue_report stored procedure.
    """
    import re
    while True:
        start = inp("From date (YYYY-MM-DD)")
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", start): break
        print("  Invalid format. Use YYYY-MM-DD.")
    while True:
        end = inp("To date   (YYYY-MM-DD)")
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", end): break
        print("  Invalid format. Use YYYY-MM-DD.")

    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    rows = []
    headers = ["Date", "Invoices", "Total Billed (VND)", "Average per Invoice (VND)"]
    try:
        cursor.callproc("sp_revenue_report", [start, end])
        for result in cursor.stored_results():
            rows = result.fetchall()
            print_table(headers, rows)
    except Error:
        cursor.execute(
            "SELECT InvoiceDate, COUNT(*), "
            "       FORMAT(SUM(TotalAmount), 0), FORMAT(AVG(TotalAmount), 0) "
            "FROM Invoices WHERE InvoiceDate BETWEEN %s AND %s "
            "GROUP BY InvoiceDate ORDER BY InvoiceDate",
            (start, end)
        )
        rows = cursor.fetchall()
        print_table(headers, rows)
    finally:
        cursor.close(); conn.close()

    if rows and confirm("Export this report to CSV?"):
        fname = f"billing_summary_{start}_to_{end}_{_timestamp()}.csv"
        _export_csv(fname, headers, rows)
    press_enter()


def _report_dept_workload():
    """
    Appointment volume grouped by department.
    Gives a higher-level view of clinical load across departments,
    useful for resource allocation and staffing decisions.
    Queries the view vw_doctor_appointment_count and aggregates by department.
    """
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    rows = []
    headers = ["Department", "No. of Doctors", "Total Appointments"]
    try:
        # Aggregate doctor-level view up to department level
        cursor.execute(
            "SELECT DepartmentName, "
            "       COUNT(DISTINCT DoctorID)  AS DoctorCount, "
            "       SUM(TotalAppointments)    AS TotalAppointments "
            "FROM vw_doctor_appointment_count "
            "GROUP BY DepartmentName "
            "ORDER BY TotalAppointments DESC"
        )
        rows = cursor.fetchall()
        print_table(headers, rows)
    except Error as e:
        print(f"\n  [ERROR] View 'vw_doctor_appointment_count' does not exist.\n  Details: {e}")
    finally:
        cursor.close(); conn.close()

    if rows and confirm("Export this report to CSV?"):
        fname = f"dept_workload_{_timestamp()}.csv"
        _export_csv(fname, headers, rows)
    press_enter()


def _report_age_group():
    """
    Classify patients into standard clinical age groups:
      Pediatric  : 0–17
      Adult      : 18–59
      Geriatric  : 60+
    Useful for epidemiological analysis and clinical resource planning.
    Uses UDF fn_cal_age().
    """
    conn = get_connection()
    if not conn: return
    cursor = conn.cursor()
    rows = []
    headers = ["Age Group", "Patient Count", "Percentage (%)"]
    try:
        cursor.execute(
            "SELECT "
            "  CASE "
            "    WHEN fn_cal_age(DateOfBirth) < 18 THEN 'Pediatric  (0–17)' "
            "    WHEN fn_cal_age(DateOfBirth) < 60 THEN 'Adult      (18–59)' "
            "    ELSE                                   'Geriatric  (60+)' "
            "  END AS AgeGroup, "
            "  COUNT(*)                          AS PatientCount, "
            "  ROUND(COUNT(*) * 100.0 / (SELECT COUNT(*) FROM Patients), 1) AS Pct "
            "FROM Patients "
            "GROUP BY AgeGroup "
            "ORDER BY MIN(fn_cal_age(DateOfBirth))"
        )
        rows = cursor.fetchall()
        print_table(headers, rows)
    except Error as e:
        print(f"\n  [ERROR] {e}")
    finally:
        cursor.close(); conn.close()

    if rows and confirm("Export this report to CSV?"):
        fname = f"patient_age_groups_{_timestamp()}.csv"
        _export_csv(fname, headers, rows)
    press_enter()
