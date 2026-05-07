# import essential library
import mysql.connector # connect to db
from mysql.connector import Error
from faker import Faker # seed data
import random
from datetime import date, timedelta


# config database connection
db_config = {
    "host": "localhost",
    "user": "root",
    "password": "123456",
    "database": "hospital_management"
}


def get_connection():
    try: 
        conn = mysql.connector.connect(**db_config)
        return conn
    except Error as e:
        print(f"\n [CONNECTION ERROR] {e}")
        print(" Please check your information in configuration\n")
        return None
    
def test_connection():
    conn = get_connection()
    if conn:
        print(" Connect to MYSQL successfully")
        conn.close()
        return True
    return False


# SEED DATA
fake = Faker("en_US")
random.seed(42)

departments = [
    ("DEPT001", "Internal Medicine"),         # Khoa Nội
    ("DEPT002", "General Surgery"),           # Khoa Ngoại Phẫu
    ("DEPT003", "Pediatrics"),                # Khoa Nhi
    ("DEPT004", "Cardiology"),                # Khoa Tim mạch
    ("DEPT005", "Dermatology"),               # Khoa Da liễu 
    ("DEPT006", "Neurology"),                 # Khoa Thần kinh
    ("DEPT007", "Ophthalmology"),             # Khoa Mắt
    ("DEPT008", "Emergency Department"),      # Khoa Cấp cứu
    ("DEPT009", "Obstetrics & Gynecology"),   # Khoa Sản Phụ khoa (OB-GYN)
    ("DEPT010", "Orthopedics"),               # Khoa Chấn thương chỉnh hình
    ("DEPT011", "Oncology"),                  # Khoa Ung bướu
    ("DEPT012", "Psychiatry"),                # Khoa Tâm thần học
    ("DEPT013", "Radiology"),                 # Khoa Chẩn đoán hình ảnh
    ("DEPT014", "Otolaryngology"),            # Khoa Tai Mũi Họng (ENT)
    ("DEPT015", "Endocrinology"),             # Khoa Nội tiết
]
 
specialties = [
    "General Internal Medicine",  # Nội tổng quát
    "General Surgery",            # Ngoại tổng quát
    "Pediatrics",                 # Nhi khoa
    "Cardiology",                 # Tim mạch
    "Dermatology",                # Da liễu
    "Neurology",                  # Nội thần kinh
    "Ophthalmology",              # Nhãn khoa
    "Pulmonology",                # Hô hấp
    "Gastroenterology",           # Tiêu hóa
    "Emergency Medicine",         # Y học cấp cứu
    "Obstetrics",                 # Sản khoa
    "Gynecology",                 # Phụ khoa
    "Orthopedic Surgery",         # Phẫu thuật chỉnh hình
    "Oncology",                   # Ung bướu
    "Psychiatry",                 # Tâm thần học
    "Radiology",                  # Chẩn đoán hình ảnh
    "Anesthesiology",             # Gây mê hồi sức
    "Otolaryngology (ENT)",       # Tai Mũi Họng
    "Urology",                    # Tiết niệu
    "Endocrinology",              # Nội tiết
    "Nephrology",                 # Thận học
    "Infectious Disease"          # Bệnh truyền nhiễm
]

genders = ["Male", "Female"]


def random_date(start_year = 1950, end_year = 2005):
    start = date(start_year, 1, 1)
    end = date(end_year, 12, 31)
    return start + timedelta(days = random.randint(0, (end - start).days))

def random_apt_date():
    start = date(2023, 1, 1)
    end = date(2025, 6, 30)
    return start + timedelta(days = random.randint(0, (end - start).days))

def random_time():
    hour = random.randint(7, 16)
    minute = random.choice([0, 15, 30, 45])
    return f"{hour: 02d}:{minute:02d}:00"

def seed_database():
    # delete old data and generate 100 sample records for each table
    conn = get_connection()
    if not conn:
        return
    cursor = conn.cursor()

    try: 
        cursor.execute("set foreign_key_checks = 0")
        for tbl in ["Invoices", "Appointments", "Doctors", 
                    "Patients", "Departments"]:
            # tbl is table in database
            cursor.execute(f"delete from {tbl}")
        
        # 1.Departments
        cursor.executemany("insert into Departments values (%s, %s)", departments)
        print(f"Departmentss: {len(departments)} rows")

        # 2.Patients
        patients = []
        for i in range(1, 101):
            patients.append((
                f"PAT{i:03d}", fake.name(), random_date().isoformat(),
                random.choice(genders),
                fake.address().replace("\n", ", ")[:255],
                fake.phone_number()[:15]
            ))
        cursor.executemany("insert into Patients values (%s,%s,%s,%s,%s,%s)", patients)
        print(f"Patients: {len(patients)} rows")

        #3. Doctors 
        dept_ids = [d[0] for d in departments]
        doctors = []
        for i in range(1, 101):
            doctors.append((
                f"DOC{i:03d}", fake.name(),
                random.choice(specialties),
                random.choice(dept_ids)
            ))
        cursor.executemany("insert into Doctors values (%s, %s, %s, %s)", doctors)
        print(f"Doctors: {len(doctors)} rows")

        #4. Appointments
        # prevent overlap appointment(2 appt with a doctor at the same time)
        used_slots = set()
        apts = []
        for i in range (1, 101):
            while True:
                doc_id = random.choice(doctors)[0]
                pat_id = random.choice(patients)[0]
                adate = random_apt_date()
                atime = random_time()
                if (doc_id, adate, atime) not in used_slots:
                    used_slots.add((doc_id, adate, atime))
                    break
            apts.append((f"APT{i:03d}", adate.isoformat(), atime, doc_id, pat_id))
        cursor.executemany("insert into Appointments values (%s, %s, %s, %s, %s)", apts)
        print(f"Appointments: {len(apts)} rows")

        #5. Invoices
        inv = []
        for i in range (1, 101):
            pat_id = random.choice(patients)[0]
            inv.append((
                f"INV{i:03d}", random_apt_date().isoformat(),
                round(random.uniform(100_000, 5_000_000), 2),
                pat_id
            ))
        cursor.executemany("insert into Invoices values (%s, %s, %s, %s)", inv)
        print(f"Invoices: {len(inv)} rows")

        cursor.execute("set foreign_key_checks = 1")
        conn.commit()
        print("\n Seed data complete")

    except Error as e: 
        conn.rollback()
        print(f"\n [ERROR] {e}")
    finally:
        cursor.close()
        conn.close()


if __name__ == "__main__":
    print("Inserting sample data...")
    seed_database()
