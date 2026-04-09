CREATE TABLE IF NOT EXISTS teacher_roster (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    teacher_no VARCHAR(50) NOT NULL,
    real_name VARCHAR(50) NOT NULL,
    is_enabled TINYINT(1) NOT NULL DEFAULT 1,
    imported_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_teacher_roster_teacher_no (teacher_no),
    KEY idx_teacher_roster_teacher_no (teacher_no)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


INSERT INTO teacher_roster (teacher_no, real_name, is_enabled)
VALUES
    ('T2020007', '李老师', 1),
    ('T2020008', '王老师', 1),
    ('T2020009', '赵老师', 1),
    ('T2020010', '孙老师', 0);
