CREATE TABLE IF NOT EXISTS student_roster (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    student_no VARCHAR(50) NOT NULL,
    real_name VARCHAR(50) NOT NULL,
    is_enabled TINYINT(1) NOT NULL DEFAULT 1,
    imported_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_student_roster_student_no (student_no),
    KEY idx_student_roster_student_no (student_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


INSERT INTO student_roster (student_no, real_name, is_enabled)
VALUES
    ('20250001', '张三', 1),
    ('20250002', '李四', 1),
    ('20250003', '王五', 1),
    ('20250004', '赵六', 0);