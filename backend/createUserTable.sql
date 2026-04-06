CREATE TABLE IF NOT EXISTS auth_users (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    phone VARCHAR(20) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    real_name VARCHAR(50) NOT NULL,
    role ENUM('student', 'teacher') NOT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uk_auth_users_phone (phone),
    KEY idx_auth_users_role (role)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



CREATE TABLE IF NOT EXISTS student_users (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    auth_user_id BIGINT UNSIGNED NOT NULL,
    student_no VARCHAR(50) NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uk_student_users_auth_user_id (auth_user_id),
    UNIQUE KEY uk_student_users_student_no (student_no),
    KEY idx_student_users_auth_user_id (auth_user_id),
    CONSTRAINT fk_student_users_auth_user_id
        FOREIGN KEY (auth_user_id)
        REFERENCES auth_users(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;



CREATE TABLE IF NOT EXISTS teacher_users (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    auth_user_id BIGINT UNSIGNED NOT NULL,
    teacher_no VARCHAR(50) NOT NULL,
    teacher_invite_verified TINYINT(1) NOT NULL DEFAULT 0,
    PRIMARY KEY (id),
    UNIQUE KEY uk_teacher_users_auth_user_id (auth_user_id),
    UNIQUE KEY uk_teacher_users_teacher_no (teacher_no),
    KEY idx_teacher_users_auth_user_id (auth_user_id),
    CONSTRAINT fk_teacher_users_auth_user_id
        FOREIGN KEY (auth_user_id)
        REFERENCES auth_users(id)
        ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

