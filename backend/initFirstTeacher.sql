INSERT INTO auth_users (
    phone,
    password_hash,
    real_name,
    role,
    is_active,
    created_at,
    updated_at
) VALUES (
    '18995537535',
    '$2b$12$6PMdqsGgMH3ySHVPjjaBdOiDn4scKaZuk2TMMpEcqMQaqXFXBCtjy',
    '管理员-王老师',
    'teacher',
    1,
    NOW(),
    NOW()
);

INSERT INTO teacher_users (
    auth_user_id,
    teacher_no,
    teacher_invite_verified
)
SELECT
    id,
    'T0001',
    1
FROM auth_users
WHERE phone = '18995537535';