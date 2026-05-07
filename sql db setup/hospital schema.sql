create table Departments (
	DepartmentID varchar(20) primary key, 
    DepartmentName varchar(100) not null
);

create table Patients (
	PatientID varchar(20) primary key,
    PatientName varchar(100) not null,
    DateOfBirth date,
    Gender varchar(10),
    Address varchar(255), 
    PhoneNumber varchar(15)
);

create table Doctors (
	DoctorID varchar(20) primary key,
    DoctorName varchar(100) not null,
    Specialty varchar(100), 
    DepartmentID varchar(20),
    foreign key (DepartmentID) references Departments (DepartmentID)
		on delete set null
        on update cascade
);

create table Invoices (
	InvoiceID varchar(20) primary key,
    InvoiceDate date,
    TotalAmount decimal(15,2), 
    PatientID varchar(20),
    foreign key (PatientID) references Patients (PatientID)
		on delete cascade
        on update cascade
);

create table Appointments (
	AppointmentID varchar(20) primary key,
    AppointmentDate date,
    AppointmentTime time,
    DoctorID varchar(20),
    PatientID varchar(20),
    foreign key (DoctorID) references Doctors (DoctorID)
		on delete cascade
        on update cascade,
	foreign key (PatientID) references Patients (PatientID)
		on delete cascade
        on update cascade
);
