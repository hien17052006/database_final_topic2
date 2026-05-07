use hospital_management; 
-- INDEXES
-- find appointment with doctor
create index idx_appt_doctor on Appointments (DoctorID);
-- find appointment scheduled by patient
create index idx_appt_patient on Appointments (PatientID);
-- find appointment regarding date
create index idx_appt_date on Appointments (AppointmentDate);
-- find patient's invoice 
create index idx_inv_patient on Invoices (PatientID);
-- find doctor details in specific department
create index idx_doctor_dept on Doctors (DepartmentID);
-- find doctor according to specialty
create index idx_doctor_spe on Doctors (Specialty);
