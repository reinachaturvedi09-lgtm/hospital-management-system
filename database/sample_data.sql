-- ============================================================
-- Hospital Management System - Sample Data
-- Run this AFTER schema.sql
-- ============================================================

USE hospital_management;

-- ============================================================
-- Admin (password: admin123)
-- ============================================================
INSERT INTO admins (username, password, full_name, email, phone) VALUES
('admin', 'admin123', 'System Administrator', 'admin@hospital.com', '9876543210');

-- ============================================================
-- Doctors (password: doctor123)
-- ============================================================
INSERT INTO doctors (username, password, full_name, email, phone, specialization, qualification, experience_years, consultation_fee, availability) VALUES
('dr.smith', 'doctor123', 'Dr. Rajesh Smith', 'dr.smith@hospital.com', '9876543211', 'General Physician', 'MBBS, MD', 15, 800.00, 'Available'),
('dr.patel', 'doctor123', 'Dr. Ananya Patel', 'dr.patel@hospital.com', '9876543212', 'Cardiologist', 'MBBS, DM Cardiology', 12, 1200.00, 'Available'),
('dr.kumar', 'doctor123', 'Dr. Vikram Kumar', 'dr.kumar@hospital.com', '9876543213', 'Orthopedic Surgeon', 'MBBS, MS Ortho', 20, 1500.00, 'Available'),
('dr.sharma', 'doctor123', 'Dr. Priya Sharma', 'dr.sharma@hospital.com', '9876543214', 'Pediatrician', 'MBBS, MD Pediatrics', 8, 900.00, 'Available'),
('dr.reddy', 'doctor123', 'Dr. Suresh Reddy', 'dr.reddy@hospital.com', '9876543215', 'Dermatologist', 'MBBS, MD Dermatology', 10, 1000.00, 'On Leave');

-- ============================================================
-- Receptionists (password: rec123)
-- ============================================================
INSERT INTO receptionists (username, password, full_name, email, phone, shift) VALUES
('rec.jane', 'rec123', 'Jane Doe', 'rec.jane@hospital.com', '9876543220', 'Morning'),
('rec.mike', 'rec123', 'Michael Ross', 'rec.mike@hospital.com', '9876543221', 'Evening'),
('rec.sara', 'rec123', 'Sara Williams', 'rec.sara@hospital.com', '9876543222', 'Morning');

-- ============================================================
-- Patients
-- ============================================================
INSERT INTO patients (first_name, last_name, date_of_birth, gender, email, phone, address, blood_group, allergies, medical_history, assigned_doctor_id) VALUES
('Amit', 'Verma', '1990-05-15', 'Male', 'amit.verma@email.com', '9876543230', '12 MG Road, Delhi', 'O+', 'Penicillin', 'Hypertension', 1),
('Sneha', 'Gupta', '1985-08-22', 'Female', 'sneha.gupta@email.com', '9876543231', '45 Park Street, Kolkata', 'A+', 'None', 'Diabetes Type 2', 2),
('Rahul', 'Jain', '1978-01-10', 'Male', 'rahul.jain@email.com', '9876543232', '78 Civil Lines, Jaipur', 'B+', 'Aspirin', 'Asthma', 1),
('Priyanka', 'Nair', '1995-12-03', 'Female', 'priyanka.nair@email.com', '9876543233', '23 Marine Drive, Mumbai', 'AB+', 'None', 'No major illnesses', 4),
('Arjun', 'Singh', '1982-07-18', 'Male', 'arjun.singh@email.com', '9876543234', '56 Anna Salai, Chennai', 'O-', 'Sulfa drugs', 'Chronic back pain', 3),
('Meera', 'Iyer', '1993-03-25', 'Female', 'meera.iyer@email.com', '9876543235', '89 Residency Road, Bangalore', 'A-', 'None', 'Migraine', 2),
('Karthik', 'Menon', '1970-11-30', 'Male', 'karthik.menon@email.com', '9876543236', '34 MG Road, Kochi', 'B-', 'None', 'Heart disease', 2),
('Divya', 'Choudhary', '1988-09-14', 'Female', 'divya.c@email.com', '9876543237', '67 Civil Lines, Lucknow', 'O+', 'Ibuprofen', 'Allergic rhinitis', 1);

-- ============================================================
-- Appointments
-- ============================================================
INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, status, reason, notes, created_by) VALUES
(1, 1, CURDATE(), '09:00:00', 'Scheduled', 'Regular checkup', NULL, 1),
(2, 2, CURDATE(), '10:00:00', 'Scheduled', 'Heart palpitations', NULL, 1),
(3, 1, CURDATE(), '11:00:00', 'Completed', 'Breathing difficulty', 'Prescribed inhaler', 1),
(4, 4, CURDATE(), '09:30:00', 'Scheduled', 'Child vaccination', NULL, 2),
(5, 3, CURDATE(), '14:00:00', 'Scheduled', 'Back pain follow-up', NULL, 1),
(6, 2, CURDATE() + INTERVAL 1 DAY, '10:00:00', 'Scheduled', 'Migraine follow-up', NULL, 2),
(7, 2, CURDATE() - INTERVAL 1 DAY, '11:00:00', 'Completed', 'Chest pain', 'ECG done, follow-up needed', 1),
(8, 1, CURDATE() - INTERVAL 1 DAY, '15:00:00', 'Completed', 'Cold and cough', 'Viral infection', 3),
(1, 3, CURDATE() + INTERVAL 2 DAY, '09:00:00', 'Scheduled', 'Knee pain', NULL, 2),
(3, 1, CURDATE() - INTERVAL 3 DAY, '10:00:00', 'Cancelled', 'Routine checkup', 'Patient cancelled', 1);

-- ============================================================
-- Prescriptions
-- ============================================================
INSERT INTO prescriptions (appointment_id, patient_id, doctor_id, diagnosis, prescription_text, medicine_details, notes) VALUES
(3, 3, 1, 'Mild asthma exacerbation', 'Use inhaler twice daily for 2 weeks. Avoid dusty environments.', 'Salbutamol Inhaler - 2 puffs twice daily\nMontair LC - 1 tablet daily', 'Follow up in 2 weeks if no improvement.'),
(7, 7, 2, 'Chest pain - Musculoskeletal', 'ECG normal. Prescribed pain relief and rest.', 'Crocin 500mg - 1 tablet three times daily\nPantop 40mg - 1 tablet before breakfast', 'Avoid heavy lifting for 1 week. Follow up in 3 days.'),
(8, 8, 1, 'Viral upper respiratory infection', 'Complete rest. Stay hydrated. Take prescribed medicines.', 'Paracetamol 650mg - 1 tablet three times daily\nCetirizine 10mg - 1 tablet at bedtime\nSteam inhalation twice daily', 'Recovery expected in 5-7 days.');

-- ============================================================
-- Bills
-- ============================================================
INSERT INTO bills (patient_id, appointment_id, consultation_fee, medicine_charges, lab_charges, other_charges, total_amount, payment_status, payment_method) VALUES
(3, 3, 800.00, 450.00, 0.00, 0.00, 1250.00, 'Paid', 'Cash'),
(7, 7, 1200.00, 320.00, 500.00, 0.00, 2020.00, 'Paid', 'Card'),
(8, 8, 800.00, 280.00, 0.00, 0.00, 1080.00, 'Paid', 'UPI'),
(1, NULL, 800.00, 0.00, 0.00, 0.00, 800.00, 'Unpaid', 'Cash'),
(2, NULL, 1200.00, 0.00, 1000.00, 0.00, 2200.00, 'Partial', 'Insurance');
