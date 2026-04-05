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
    },

    examNotices: {
        survey: [
            '本问卷所有题目均为必答题。',
            '答题开始后请勿刷新或关闭浏览器。',
            '倒计时结束后系统将自动提交。',
            '提交前请再次确认所有内容。'
        ],
        integrity: [
            '本考核所有题目均为必答题。',
            '考试过程中请独立完成，不要刷新页面。',
            '倒计时结束系统将自动提交。',
            '提交后答案不可修改。'
        ]
    },

    examEntryMap: {
        survey: {
            examId: 'survey-001',
            paperName: '德育画像构建测试问卷'
        },
        integrity: {
            examId: 'integrity-001',
            paperName: '科研诚信考核测试卷'
        }
    },

    examPaperMap: {
        'survey-001': {
            examId: 'survey-001',
            paperName: '德育画像构建测试问卷',
            durationSeconds: 5400,
            questions: [
                {
                    id: 'sq1',
                    type: 'single',
                    title: '当你在团队合作中遇到意见分歧时，通常会怎么做？',
                    options: [
                    { label: '坚持自己观点', value: 'A' },
                    { label: '主动沟通协调', value: 'B' },
                    { label: '选择沉默', value: 'C' },
                    { label: '交给别人处理', value: 'D' }
                    ]
                },
                {
                    id: 'sq2',
                    type: 'multiple',
                    title: '你认为医学生应具备哪些核心品质？',
                    options: [
                    { label: '责任心', value: 'A' },
                    { label: '同理心', value: 'B' },
                    { label: '合作意识', value: 'C' },
                    { label: '诚信意识', value: 'D' }
                    ]
                },
                {
                    id: 'sq3',
                    type: 'judge',
                    title: '在面对患者情绪激动时，先安抚情绪再解释问题是合理的做法。'
                },
                {
                    id: 'sq4',
                    type: 'blank',
                    title: '请填写你认为医学职业最重要的一项价值。'
                },
                {
                    id: 'sq5',
                    type: 'essay',
                    title: '请简要描述一次你在学习或生活中体现责任担当的经历。'
                }
            ]
        },

        'integrity-001': {
            examId: 'integrity-001',
            paperName: '科研诚信考核测试卷',
            durationSeconds: 7200,
            questions: [
                {
                    id: 'iq1',
                    type: 'single',
                    title: '发现实验数据与预期不一致时，最合适的做法是：',
                    options: [
                    { label: '修改数据使其更好看', value: 'A' },
                    { label: '删除异常数据不记录', value: 'B' },
                    { label: '如实记录并分析原因', value: 'C' },
                    { label: '等待老师决定是否保留', value: 'D' }
                    ]
                },
                {
                    id: 'iq2',
                    type: 'multiple',
                    title: '以下哪些行为属于科研不端风险？',
                    options: [
                    { label: '伪造数据', value: 'A' },
                    { label: '篡改实验结果', value: 'B' },
                    { label: '规范引用他人成果', value: 'C' },
                    { label: '一稿多投', value: 'D' }
                    ]
                },
                {
                    id: 'iq3',
                    type: 'judge',
                    title: '只要论文结论正确，适当美化过程数据也是可以接受的。'
                },
                {
                    id: 'iq4',
                    type: 'blank',
                    title: '请填写你理解的“科研诚信”关键词。'
                },
                {
                    id: 'iq5',
                    type: 'essay',
                    title: '请简要说明你会如何处理导师要求“优化”实验结果的情况。'
                }
            ]
        }
    },

    examResultDetails: {
        s001: {
            r001: {
            id: 'r001',
            paperName: '德育画像构建测试问卷',
            studentNo: '20260001',
            realName: '张三',
            submitTime: '2026-04-01 14:20:00',
            durationMinutes: 18,
            answerList: [
                { questionId: 'sq1', questionTitle: '当你在团队合作中遇到意见分歧时，通常会怎么做？', answer: 'B' },
                { questionId: 'sq2', questionTitle: '你认为医学生应具备哪些核心品质？', answer: ['A', 'B', 'D'] }
            ],
            aiAnalysis: {
                dimensions: [
                { dimension: '科研诚信薄弱型', score: 80, reason: '基本具备规范意识。' },
                { dimension: '医患沟通焦虑型', score: 76, reason: '沟通表达尚可，但应对高压场景仍需训练。' },
                { dimension: '职业认同模糊型', score: 83, reason: '职业目标较清晰。' },
                { dimension: '人文关怀缺失型', score: 85, reason: '能体现一定的人文关怀意识。' },
                { dimension: '综合发展均衡型', score: 82, reason: '整体发展较均衡。' }
                ],
                summary: '建议继续加强压力场景下的沟通表达与科研规范训练。'
            }
            }
        },
        s002: {},
        t001: {}
    }
}