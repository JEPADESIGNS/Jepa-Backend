-- Phase 3: Biometric and Physical ID Integration for Attendance
-- Adds biometric verification and physical ID tracking to attendance records
-- MANDATORY: All attendance records must be verified via fingerprint/face recognition + physical ID

-- Note: biometric_type, biometric_data, physical_id, and verified_at columns are already 
-- defined in the main schema.sql, so we don't add them here to avoid duplicate column errors.

-- Create biometric_verification audit table for security compliance
CREATE TABLE IF NOT EXISTS biometric_verification (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    attendance_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    biometric_type TEXT NOT NULL,  -- 'fingerprint' or 'face_recognition'
    physical_id TEXT NOT NULL,     -- Physical ID card scanned
    biometric_data TEXT NOT NULL,  -- Device token/template hash
    verification_status TEXT NOT NULL DEFAULT 'Success',  -- 'Success', 'Failed', 'Retry'
    attempt_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    device_id TEXT,                -- Biometric scanner device identifier
    verified_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (attendance_id) REFERENCES attendance(id),
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Create physical_id_scan audit table
CREATE TABLE IF NOT EXISTS physical_id_scan (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    project_id INTEGER NOT NULL,
    physical_id TEXT NOT NULL,     -- Physical ID card number/UUID
    id_type TEXT DEFAULT 'Employee Card',  -- Type of physical ID
    scan_timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    scanner_device_id TEXT,        -- ID card scanner device identifier
    scan_status TEXT NOT NULL DEFAULT 'Valid',  -- 'Valid', 'Invalid', 'Expired', 'Revoked'
    notes TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (project_id) REFERENCES projects(id)
);

-- Create index for fast attendance lookups with biometric verification
CREATE INDEX IF NOT EXISTS idx_attendance_biometric_verification 
ON attendance(user_id, attendance_date, verified_at);

-- Create index for biometric verification audit trail
CREATE INDEX IF NOT EXISTS idx_biometric_verification_user 
ON biometric_verification(user_id, project_id, attempt_timestamp);

-- Create index for physical ID verification audit trail
CREATE INDEX IF NOT EXISTS idx_physical_id_scan_user 
ON physical_id_scan(user_id, project_id, scan_timestamp);
