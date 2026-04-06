// src/mock/database.js

export const mockDb = {
    users: [
    {
      id: 1,
      username: 'zhangsan',
      real_name: '张三',
      role: 'student',
      student_no: '20260001',
      teacher_no: null,
      phone: '13800000000',
      email: 'zhangsan@example.com',
      password: '123456',
      token: 'mock-token-student-001',
      login_accounts: ['zhangsan', '20260001', '13800000000', 'zhangsan@example.com']
    },
    {
      id: 2,
      username: 'lisi',
      real_name: '李四',
      role: 'student',
      student_no: '20260002',
      teacher_no: null,
      phone: '13800000001',
      email: 'lisi@example.com',
      password: '123456',
      token: 'mock-token-student-002',
      login_accounts: ['lisi', '20260002', '13800000001', 'lisi@example.com']
    },
    {
      id: 1001,
      username: 'teacher_li',
      real_name: '李老师',
      role: 'teacher',
      student_no: null,
      teacher_no: 'T2020007',
      phone: '13900000000',
      email: 'teacherli@example.com',
      password: '123456',
      token: 'mock-token-teacher-001',
      login_accounts: ['teacher_li', 'T2020007', '13900000000', 'teacherli@example.com']
    }
  ],

    userHomeMap: {
        1: {
            user: {
                id: 1,
                username: 'zhangsan',
                real_name: '张三',
                role: 'student',
                student_no: '20260001',
                teacher_no: null
            },
            level: {
                level_value: 8,
                level_display: '1月3星',
                level_icon_type: 'moon',
                ai_usage_seconds: 45380,
                ai_usage_text: '12:36:20'
            },
            learning_stats: {
                simulation_completion_rate: 76.0,
                remaining_resources: 7,
                categories: [
                {
                    category_code: 'doctor_patient_dispute',
                    category_name: '医患纠纷处理',
                    completed_count: 8,
                    total_count: 10,
                    completion_rate: 80.0
                },
                {
                    category_code: 'research_fraud',
                    category_name: '科研数据造假诱惑',
                    completed_count: 13,
                    total_count: 20,
                    completion_rate: 65.0
                },
                {
                    category_code: 'medical_fairness',
                    category_name: '医疗资源分配公平性',
                    completed_count: 11,
                    total_count: 12,
                    completion_rate: 91.7
                }
                ]
            },
            score_comparison: {
                best_result: {
                label: '最高成绩',
                dimensions: [
                    { key: 'a', name: '理想信念', score: 88 },
                    { key: 'b', name: '责任担当', score: 90 },
                    { key: 'c', name: '纪律意识', score: 84 },
                    { key: 'd', name: '诚信意识', score: 93 },
                    { key: 'e', name: '集体观念', score: 86 }
                ]
                },
                worst_result: {
                label: '最低成绩',
                dimensions: [
                    { key: 'a', name: '理想信念', score: 72 },
                    { key: 'b', name: '责任担当', score: 70 },
                    { key: 'c', name: '纪律意识', score: 68 },
                    { key: 'd', name: '诚信意识', score: 75 },
                    { key: 'e', name: '集体观念', score: 73 }
                ]
                }
            }
        },

        2: {
            user: {
                id: 2,
                username: 'lisi',
                real_name: '李四',
                role: 'student',
                student_no: '20260002',
                teacher_no: null
            },
            level: {
                level_value: 5,
                level_display: '5星',
                level_icon_type: 'star',
                ai_usage_seconds: 22365,
                ai_usage_text: '06:12:45'
            },
            learning_stats: {
                simulation_completion_rate: 58.0,
                remaining_resources: 14,
                categories: [
                {
                    category_code: 'doctor_patient_dispute',
                    category_name: '医患纠纷处理',
                    completed_count: 5,
                    total_count: 10,
                    completion_rate: 50.0
                }
                ]
            },
            score_comparison: {
                best_result: null,
                worst_result: null
            }
        },

        1001: {
            user: {
                id: 1001,
                username: 'teacher_li',
                real_name: '李老师',
                role: 'teacher',
                student_no: null,
                teacher_no: 'T2020007'
            },
            level: {
                level_value: 5,
                level_display: '5星',
                level_icon_type: 'star',
                ai_usage_seconds: 22365,
                ai_usage_text: '06:12:45'
            },
            learning_stats: {
                simulation_completion_rate: 58.0,
                remaining_resources: 14,
                categories: []
            },
            score_comparison: {
                best_result: null,
                worst_result: null
            }
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