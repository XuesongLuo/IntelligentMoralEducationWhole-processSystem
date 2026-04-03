// src/mock/database.js

export const mockDb = {
    users: [
        {
            id: 's001',
            account: '20260001',
            password: '123456',
            token: 'mock-token-student-001',
            profile: {
                id: 's001',
                name: '张三',
                account: '20260001',
                role: 'student',
                phone: '13800000000',
                logo: ''
            }
        },
        {
            id: 's002',
            account: '20260002',
            password: '123456',
            token: 'mock-token-student-002',
            profile: {
                id: 's002',
                name: '李四',
                account: '20260002',
                role: 'student',
                phone: '13800000001',
                logo: ''
            }
        },
        {
            id: 't001',
            account: '2020007',
            password: '123456',
            token: 'mock-token-teacher-001',
            profile: {
                id: 't001',
                name: '李老师',
                account: '2020007',
                role: 'teacher',
                phone: '13900000000',
                logo: ''
            }
        }
    ],

    UserHomeMap: {
        s001: {
            studentId: '20260001',
            studentName: '张三',
            phone: '13800000000',
            levelValue: 8,
            aiUsageDuration: '12时36分20秒',
            simulationCompletion: 76,
            studyProgressList: [
                { id: 1, name: '思想理论', progress: 80, leftCount: 2 },
                { id: 2, name: '党史学习', progress: 65, leftCount: 4 },
                { id: 3, name: '法治教育', progress: 92, leftCount: 1 }
            ],
            scoreDimensions: [
                { key: 'a', name: '理想信念', best: 88, worst: 72 },
                { key: 'b', name: '责任担当', best: 90, worst: 70 },
                { key: 'c', name: '纪律意识', best: 84, worst: 68 },
                { key: 'd', name: '诚信意识', best: 93, worst: 75 },
                { key: 'e', name: '集体观念', best: 86, worst: 73 }
            ]
        },

        s002: {
            studentId: '20260002',
            studentName: '李四',
            phone: '13800000001',
            levelValue: 5,
            aiUsageDuration: '6时12分45秒',
            simulationCompletion: 58,
            studyProgressList: [
                { id: 1, name: '思想理论', progress: 52, leftCount: 5 },
                { id: 2, name: '党史学习', progress: 60, leftCount: 3 },
                { id: 3, name: '法治教育', progress: 48, leftCount: 6 }
            ],
            scoreDimensions: [
                { key: 'a', name: '理想信念', best: 76, worst: 65 },
                { key: 'b', name: '责任担当', best: 70, worst: 62 },
                { key: 'c', name: '纪律意识', best: 81, worst: 69 },
                { key: 'd', name: '诚信意识', best: 78, worst: 66 },
                { key: 'e', name: '集体观念', best: 74, worst: 63 }
            ]
        },
            t001: {
            studentId: '2020007',
            studentName: '李老师',
            phone: '13900000000',
            levelValue: 5,
            aiUsageDuration: '6时12分45秒',
            simulationCompletion: 58,
            studyProgressList: [
                { id: 1, name: '思想理论', progress: 52, leftCount: 5 },
                { id: 2, name: '党史学习', progress: 60, leftCount: 3 },
                { id: 3, name: '法治教育', progress: 48, leftCount: 6 }
            ],
            scoreDimensions: [
                { key: 'a', name: '理想信念', best: 76, worst: 65 },
                { key: 'b', name: '责任担当', best: 70, worst: 62 },
                { key: 'c', name: '纪律意识', best: 81, worst: 69 },
                { key: 'd', name: '诚信意识', best: 78, worst: 66 },
                { key: 'e', name: '集体观念', best: 74, worst: 63 }
            ]

        }
    },

    examResults: {
        s001: [
            {
                id: 'r001',
                type: 'questionnaire',
                examName: '德育画像问卷第1次',
                submitTime: '2026-04-01 14:20:00',
                duration: '18分钟',
                totalScore: 86
            },
            {
                id: 'r002',
                type: 'integrity',
                examName: '诚信考核第1次',
                submitTime: '2026-04-02 10:05:00',
                duration: '22分钟',
                totalScore: 91
            }
            ],
            s002: [
            {
                id: 'r003',
                type: 'questionnaire',
                examName: '德育画像问卷第1次',
                submitTime: '2026-04-01 16:10:00',
                duration: '20分钟',
                totalScore: 74
            }
        ]
    }
}