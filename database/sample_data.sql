-- Sample Data for Hospital Management System
-- Insert test data for development and demonstration

USE hospital_management;

-- ============================================
-- INSERT ADMIN DATA
-- ============================================
INSERT INTO admins (full_name, email, password, phone) VALUES
('Admin User', 'admin@hospital.com', 'scrypt:32768:8:1$a1b2c3d4$5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s', '9876543210'),
('Admin Manager', 'manager@hospital.com', 'scrypt:32768:8:1$a1b2c3d4$5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s', '9876543211');

-- ============================================
-- INSERT DOCTOR DATA
-- ============================================
INSERT INTO doctors (full_name, email, password, phone, specialization, license_number, experience_years, consultation_fee, availability_status) VALUES
('Dr. Rajesh Kumar', 'rajesh@hospital.com', 'scrypt:32768:8:1$a1b2c3d4$5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s', '9123456789', 'Cardiology', 'MED/2015/001', 8, 800.00, 'Available'),
('Dr. Priya Sharma', 'priya@hospital.com', 'scrypt:32768:8:1$a1b2c3d4$5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s', '9123456790', 'Neurology', 'MED/2017/002', 6, 750.00, 'Available'),
('Dr. Amit Patel', 'amit@hospital.com', 'scrypt:32768:8:1$a1b2c3d4$5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s', '9123456791', 'Orthopedics', 'MED/2016/003', 7, 600.00, 'Available'),
('Dr. Neha Desai', 'neha@hospital.com', 'scrypt:32768:8:1$a1b2c3d4$5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s', '9123456792', 'General Medicine', 'MED/2018/004', 5, 500.00, 'Available'),
('Dr. Vikram Singh', 'vikram@hospital.com', 'scrypt:32768:8:1$a1b2c3d4$5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s', '9123456793', 'Pediatrics', 'MED/2019/005', 4, 550.00, 'Unavailable');

-- ============================================
-- INSERT RECEPTIONIST DATA
-- ============================================
INSERT INTO receptionists (full_name, email, password, phone, shift) VALUES
('Ravi Kumar', 'ravi@hospital.com', 'scrypt:32768:8:1$a1b2c3d4$5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s', '9987654321', 'Morning'),
('Anita Singh', 'anita@hospital.com', 'scrypt:32768:8:1$a1b2c3d4$5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s', '9987654322', 'Afternoon'),
('Rohan Verma', 'rohan@hospital.com', 'scrypt:32768:8:1$a1b2c3d4$5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s', '9987654323', 'Evening');

-- ============================================
-- INSERT PATIENT DATA
-- ============================================
INSERT INTO patients (full_name, email, phone, date_of_birth, gender, blood_group, address, city, state, postal_code, emergency_contact, emergency_phone, medical_history, allergies, assigned_doctor_id) VALUES
('John Doe', 'john@example.com', '9111111111', '1990-05-15', 'Male', 'O+', '123 Main St', 'Mumbai', 'Maharashtra', '400001', 'Jane Doe', '9111111112', 'No major illnesses', 'Penicillin', 1),
('Sarah Smith', 'sarah@example.com', '9111111113', '1985-08-22', 'Female', 'B+', '456 Oak Ave', 'Delhi', 'Delhi', '110001', 'Tom Smith', '9111111114', 'Hypertension', 'Aspirin', 2),
('Michael Johnson', 'michael@example.com', '9111111115', '1992-03-10', 'Male', 'AB+', '789 Pine Rd', 'Bangalore', 'Karnataka', '560001', 'Anna Johnson', '9111111116', 'Diabetes', 'None', 3),
('Emma Wilson', 'emma@example.com', '9111111117', '1988-11-30', 'Female', 'A+', '321 Elm St', 'Chennai', 'Tamil Nadu', '600001', 'David Wilson', '9111111118', 'Asthma', 'Dust', 2),
('Robert Brown', 'robert@example.com', '9111111119', '1995-07-18', 'Male', 'O-', '654 Maple Dr', 'Hyderabad', 'Telangana', '500001', 'Lisa Brown', '9111111120', 'No known conditions', 'Latex', 4),
('Emily Davis', 'emily@example.com', '9111111121', '1993-02-14', 'Female', 'B-', '987 Cedar Ln', 'Pune', 'Maharashtra', '411001', 'James Davis', '9111111122', 'Allergy prone', 'Sulfa drugs', 1),
('James Wilson', 'james.w@example.com', '9111111123', '1987-09-25', 'Male', 'AB-', '147 Birch Ave', 'Ahmedabad', 'Gujarat', '380001', 'Patricia Wilson', '9111111124', 'Kidney issues', 'NSAIDs', 3);

-- ============================================
-- INSERT APPOINTMENT DATA
-- ============================================
INSERT INTO appointments (patient_id, doctor_id, appointment_date, appointment_time, reason_for_visit, status, notes) VALUES
(1, 1, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '10:00:00', 'Chest pain', 'Scheduled', 'First time patient'),
(2, 2, DATE_ADD(CURDATE(), INTERVAL 2 DAY), '11:30:00', 'Headache', 'Scheduled', 'Regular checkup'),
(3, 3, DATE_ADD(CURDATE(), INTERVAL 1 DAY), '02:00:00', 'Knee pain', 'Completed', 'Post-surgery review'),
(4, 2, DATE_ADD(CURDATE(), INTERVAL 3 DAY), '03:30:00', 'Respiratory issues', 'Scheduled', 'Asthma management'),
(5, 4, CURDATE(), '09:00:00', 'Regular checkup', 'Completed', 'Annual health checkup'),
(6, 1, DATE_ADD(CURDATE(), INTERVAL 5 DAY), '04:00:00', 'Heart screening', 'Scheduled', 'Preventive care'),
(7, 3, DATE_ADD(CURDATE(), INTERVAL 2 DAY), '01:00:00', 'Joint pain', 'Cancelled', 'Patient requested cancellation');

-- ============================================
-- INSERT DIAGNOSIS DATA
-- ============================================
INSERT INTO diagnoses (appointment_id, doctor_id, patient_id, diagnosis_description, severity, icd_code) VALUES
(3, 3, 3, 'Post-operative knee recovery progressing well', 'Mild', 'M25.561'),
(5, 4, 5, 'Routine physical examination - All normal', 'Mild', 'Z00.00');

-- ============================================
-- INSERT PRESCRIPTION DATA
-- ============================================
INSERT INTO prescriptions (appointment_id, doctor_id, patient_id, medicine_name, dosage, frequency, duration, instructions, medicine_cost) VALUES
(3, 3, 3, 'Ibuprofen', '400mg', 'Twice daily', '7 days', 'Take after food', 150.00),
(3, 3, 3, 'Diclofenac', '50mg', 'Twice daily', '5 days', 'Apply gel on knee', 200.00),
(5, 4, 5, 'Vitamin D', '1000 IU', 'Once daily', '30 days', 'Take with breakfast', 300.00);

-- ============================================
-- INSERT BILL DATA
-- ============================================
INSERT INTO bills (patient_id, appointment_id, consultation_fee, medicine_charges, lab_charges, other_charges, total_amount, discount_amount, net_amount, payment_status, payment_method, payment_date) VALUES
(3, 3, 600.00, 350.00, 0.00, 0.00, 950.00, 50.00, 900.00, 'Paid', 'Card', NOW()),
(5, 5, 500.00, 300.00, 500.00, 0.00, 1300.00, 100.00, 1200.00, 'Paid', 'Cash', NOW());
