INSERT INTO users (
    username,
    student_no,
    phone,
    email,
    password_hash,
    real_name,
    role,
    teacher_invite_verified,
    is_active
) VALUES (
    'student001',
    '20230001',
    '13800000001',
    'student001@example.com',
    '$2b$12$6PMdqsGgMH3ySHVPjjaBdOiDn4scKaZuk2TMMpEcqMQaqXFXBCtjy',
    '张三',
    'student',
    0,
    1
);