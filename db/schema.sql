/* 1: create the users table */

DROP TABLE IF EXISTS users;

CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
) ENGINE=InnoDB;

/* 2: create default admin account */
INSERT INTO users (username, password) 
VALUES ('admin', 'admin123')
ON DUPLICATE KEY UPDATE password = VALUES(password);