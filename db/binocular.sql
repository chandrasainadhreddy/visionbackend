CREATE DATABASE IF NOT EXISTS binoculardb;
USE binoculardb;

-- Users table for registration, login, and password reset
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(15) NOT NULL,
    password VARCHAR(255) NOT NULL,
    profile_image VARCHAR(255) DEFAULT NULL,
    reset_token VARCHAR(255) DEFAULT NULL,
    reset_token_expiry DATETIME DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_reset_token (reset_token)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Tests table to track assessment sessions
CREATE TABLE IF NOT EXISTS tests (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    test_type ENUM('RAN', 'VRG', 'PUR') NOT NULL,
    started_at DATETIME NOT NULL,
    status VARCHAR(50) DEFAULT 'running',
    total_samples INT DEFAULT 0,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Eye tracking data table
CREATE TABLE IF NOT EXISTS eye_data (
    id INT AUTO_INCREMENT PRIMARY KEY,
    test_id INT NOT NULL,
    n INT NOT NULL,
    x DOUBLE NOT NULL,
    y DOUBLE NOT NULL,
    lx DOUBLE NOT NULL,
    ly DOUBLE NOT NULL,
    rx DOUBLE NOT NULL,
    ry DOUBLE NOT NULL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Results table to store AI analysis output
CREATE TABLE IF NOT EXISTS results (
    id INT AUTO_INCREMENT PRIMARY KEY,
    test_id INT NOT NULL,
    classification VARCHAR(100) NOT NULL,
    score DOUBLE NOT NULL,
    ai_notes TEXT DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (test_id) REFERENCES tests(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;
