use hospital_management;
-- VIEWS 

-- show appointments scheduled today
create or replace view vw_today_appt as 
select 
	a.AppointmentID,
    a.AppointmentDate,
    a.AppointmentTime,
    p.PatientName,
    p.PhoneNumber,
    d.DoctorName,
    d.Specialty,
    de.DepartmentName
from Appointments a 
join Patients p on a.PatientID = p.PatientID
join Doctors d on a.DoctorID = d.DoctorID
join Departments de on d.DepartmentID = de.DepartmentID
where a.AppointmentDate = curdate()
order by a.AppointmentTime;

-- monthly revenue
create or replace view vw_month_rev as
select 
	date_format(InvoiceDate, "%y-%m") as Month,
    count(InvoiceID) as InvoiceAmount,
    sum(TotalAmount) as TotalRevenue
from Invoices
group by date_format(InvoiceDate, "%Y-%m");

-- (for doctor) patient & appointment history
create or replace view vw_appt_his as
select
	a.AppointmentID,
    a.AppointmentDate,
    a.AppointmentTime,
    p.PatientName,
    p.Gender,
    p.PhoneNumber,
    d.DoctorName
from Appointments a
join Patients p on a.PatientID = p.PatientID
join Doctors d on a.DoctorID = d.DoctorID;

CREATE OR REPLACE VIEW vw_doctor_appointment_count AS
SELECT 
    de.DepartmentName,
    d.DoctorID,
    COUNT(a.AppointmentID) AS TotalAppointments
FROM Doctors d
JOIN Departments de ON d.DepartmentID = de.DepartmentID
LEFT JOIN Appointments a ON d.DoctorID = a.DoctorID
GROUP BY de.DepartmentName, d.DoctorID;