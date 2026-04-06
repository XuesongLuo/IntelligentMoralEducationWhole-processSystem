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
    '$2b$12$rpQs.mSO1RYnsdxNYNVOYe/8dlXqMmKooy.QULDltfpeTcsyv2CLW',
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
    '2020007',
    1
FROM auth_users
WHERE phone = '18995537535';