/* 1: create the users table */
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

/* 2: create default admin account */
INSERT INTO users (username, password_hash) 
VALUES (
    'admin', 
    'scrypt:32768:8:1$worj6IkrZKHkzMYd$55b031e0a34e1afb81df9235bdbd38002e45fd816be8e7ae2f480c0384f04846084d2bb2f192843b41ccd96ee873c3e2f9a5aac4cd9d711af2aacd813e4aa172'
)
ON DUPLICATE KEY UPDATE password_hash=VALUES(password_hash);