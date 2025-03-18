-- Reset Database
DROP DATABASE IF EXISTS chatgpt_scraper;
CREATE DATABASE chatgpt_scraper;
USE chatgpt_scraper;

-- Disable foreign key checks
SET FOREIGN_KEY_CHECKS = 0;

-- Drop existing tables
DROP TABLE IF EXISTS responses;
DROP TABLE IF EXISTS prompts;
DROP TABLE IF EXISTS chat_histories;
DROP TABLE IF EXISTS users;

-- Create tables
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    theme_preference VARCHAR(10) DEFAULT 'light',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE chat_histories (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    url TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Buat tabel prompts
CREATE TABLE prompts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    text TEXT NOT NULL,
    chat_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chat_id) REFERENCES chat_histories(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Buat tabel responses
CREATE TABLE responses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    text TEXT NOT NULL,
    prompt_id INT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (prompt_id) REFERENCES prompts(id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Buat index untuk optimasi
CREATE INDEX idx_users_username ON users(username);
CREATE INDEX idx_chat_histories_user ON chat_histories(user_id);
CREATE INDEX idx_prompts_chat ON prompts(chat_id);
CREATE INDEX idx_responses_prompt ON responses(prompt_id);

-- Aktifkan kembali foreign key checks
SET FOREIGN_KEY_CHECKS = 1; 