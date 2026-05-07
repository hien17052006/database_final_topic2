USE hospital_management;

-- 1. drop roles & users if already exists
DROP ROLE IF EXISTS 'admin_role', 'receptionist_role', 'doctor_role';
DROP USER IF EXISTS 'admin01'@'localhost', 'recep01'@'localhost', 'doc01'@'localhost';

-- 2. Create roles
CREATE ROLE 'admin_role', 'receptionist_role', 'doctor_role';

-- 3. Role seperate
-- ADMIN: full authority
GRANT ALL PRIVILEGES ON hospital_management.* TO 'admin_role';

-- RECEPTIONIST: Only manage patients, appointments, and invoices. Do not touch department or doctor information.
GRANT SELECT, INSERT, UPDATE ON hospital_management.Patients TO 'receptionist_role';
GRANT SELECT, INSERT, UPDATE, DELETE ON hospital_management.Appointments TO 'receptionist_role';
GRANT SELECT, INSERT ON hospital_management.Invoices TO 'receptionist_role';
GRANT EXECUTE ON PROCEDURE hospital_management.sp_add_appt TO 'receptionist_role';
GRANT EXECUTE ON PROCEDURE hospital_management.sp_gen_inv TO 'receptionist_role';

-- DOCTOR (Bác sĩ): read-only
GRANT SELECT ON hospital_management.Patients TO 'doctor_role';
GRANT SELECT ON hospital_management.vw_appt_his TO 'doctor_role';
GRANT SELECT ON hospital_management.vw_today_appt TO 'doctor_role';

-- 4.
CREATE USER 'admin01'@'localhost' IDENTIFIED BY 'Admin@123';
CREATE USER 'recep01'@'localhost' IDENTIFIED BY 'Recep@123';
CREATE USER 'doc01'@'localhost' IDENTIFIED BY 'Doc@123';

GRANT 'admin_role' TO 'admin01'@'localhost';
GRANT 'receptionist_role' TO 'recep01'@'localhost';
GRANT 'doctor_role' TO 'doc01'@'localhost';

-- default role
SET DEFAULT ROLE ALL TO 'admin01'@'localhost', 'recep01'@'localhost', 'doc01'@'localhost';
FLUSH PRIVILEGES;
