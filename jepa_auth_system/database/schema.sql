-- JEPA Authentication System — Complete Database Schema

CREATE TABLE IF NOT EXISTS users (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    username            TEXT UNIQUE NOT NULL,
    email               TEXT UNIQUE NOT NULL,
    phone               TEXT UNIQUE NOT NULL,
    password_hash       TEXT NOT NULL,
    role                TEXT NOT NULL DEFAULT 'client',
    status              TEXT NOT NULL DEFAULT 'active',
    profile_pic         TEXT DEFAULT 'assets/default_avatar.png',
    full_name           TEXT,
    country_code        TEXT DEFAULT '+256',
    gender              TEXT,
    dob                 TEXT,
    bio                 TEXT,
    security_question   TEXT,
    security_answer_hash TEXT,
    recovery_code       TEXT UNIQUE,
    theme               TEXT NOT NULL DEFAULT 'dark',
    created_at          DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at          DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS logs (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp   DATETIME DEFAULT CURRENT_TIMESTAMP,
    user_id     INTEGER,
    username    TEXT,
    action      TEXT NOT NULL,
    ip_address  TEXT,
    details     TEXT,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

-- Optional future tables

CREATE TABLE IF NOT EXISTS otp_codes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    code        TEXT NOT NULL,
    expires_at  DATETIME NOT NULL,
    used        INTEGER NOT NULL DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

CREATE TABLE IF NOT EXISTS notifications (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id     INTEGER NOT NULL,
    title       TEXT NOT NULL,
    message     TEXT NOT NULL,
    is_read     INTEGER NOT NULL DEFAULT 0,
    created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
