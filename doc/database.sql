-- 创建数据库
CREATE DATABASE IF NOT EXISTS mybilling DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

USE mybilling;

-- 创建用户表
CREATE TABLE IF NOT EXISTS `user` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `username` VARCHAR(64) NOT NULL,
    `email` VARCHAR(120) NOT NULL,
    `password_hash` VARCHAR(128) NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    UNIQUE KEY `uk_username` (`username`),
    UNIQUE KEY `uk_email` (`email`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建账本表
CREATE TABLE IF NOT EXISTS `ledger` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `name` VARCHAR(64) NOT NULL,
    `description` TEXT,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    `user_id` INT NOT NULL,
    PRIMARY KEY (`id`),
    KEY `idx_user_id` (`user_id`),
    CONSTRAINT `fk_ledger_user` FOREIGN KEY (`user_id`) REFERENCES `user` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建交易记录表
CREATE TABLE IF NOT EXISTS `transaction` (
    `id` INT NOT NULL AUTO_INCREMENT,
    `amount` DECIMAL(10,2) NOT NULL,
    `description` VARCHAR(256),
    `category` VARCHAR(64),
    `transaction_type` VARCHAR(20) NOT NULL,
    `date` DATETIME NOT NULL,
    `ledger_id` INT NOT NULL,
    `created_at` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (`id`),
    KEY `idx_ledger_id` (`ledger_id`),
    KEY `idx_date` (`date`),
    KEY `idx_transaction_type` (`transaction_type`),
    CONSTRAINT `fk_transaction_ledger` FOREIGN KEY (`ledger_id`) REFERENCES `ledger` (`id`) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 创建示例数据（可选）
-- 插入测试用户
INSERT INTO `user` (`username`, `email`, `password_hash`) VALUES
('test_user', 'test@example.com', 'pbkdf2:sha256:600000$your_salt$your_hash');

-- 插入测试账本
INSERT INTO `ledger` (`name`, `description`, `user_id`) VALUES
('日常开销', '记录日常生活中的各项支出', 1),
('工资收入', '记录每月的工资收入', 1);

-- 插入测试交易记录
INSERT INTO `transaction` (`amount`, `description`, `category`, `transaction_type`, `date`, `ledger_id`) VALUES
(100.00, '午餐', '餐饮', 'expense', NOW(), 1),
(5000.00, '月工资', '工资', 'income', NOW(), 2),
(200.00, '超市购物', '日用品', 'expense', NOW(), 1); 