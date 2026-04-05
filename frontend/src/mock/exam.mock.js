import { mockDb } from './database'

function getCurrentUser() {
  return JSON.parse(localStorage.getItem('userInfo') || '{}')
}

function nowString() {
  const now = new Date()
  const yyyy = now.getFullYear()
  const MM = String(now.getMonth() + 1).padStart(2, '0')
  const dd = String(now.getDate()).padStart(2, '0')
  const hh = String(now.getHours()).padStart(2, '0')
  const mm = String(now.getMinutes()).padStart(2, '0')
  const ss = String(now.getSeconds()).padStart(2, '0')
  return `${yyyy}-${MM}-${dd} ${hh}:${mm}:${ss}`
}

function createDelay(data, delay = 200) {
  return new Promise(resolve => {
    setTimeout(() => resolve({ data }), delay)
  })
}

export function mockGetExamNotice(type) {
  return createDelay({
    items: mockDb.examNotices[type] || []
  })
}

export function mockGetExamInfo(type) {
  return createDelay(mockDb.examEntryMap[type] || {})
}

export function mockGetExamPaper(type, examId) {
  const paper = mockDb.examPaperMap[examId]
  return createDelay(paper || {
    examId,
    paperName: '未找到试卷',
    durationSeconds: 3600,
    questions: []
  })
}

export function mockSubmitExamPaper(payload) {
  const currentUser = getCurrentUser()
  const paper = mockDb.examPaperMap[payload.examId]
  const userId = currentUser.id

  if (!paper || !userId) {
    return Promise.reject(new Error('提交失败，试卷或用户不存在'))
  }

  const resultId = `r${Date.now()}`
  const title = payload.examType === 'survey' ? '画像构建' : '诚信考核'

  const answerList = paper.questions.map(q => {
    const found = payload.answers.find(a => a.questionId === q.id)
    return {
      questionId: q.id,
      questionTitle: q.title,
      answer: found ? found.answer : ''
    }
  })

  const detail = {
    id: resultId,
    paperName: paper.paperName,
    studentNo: currentUser.account,
    realName: currentUser.name,
    submitTime: nowString(),
    durationMinutes: Math.ceil((paper.durationSeconds || 3600) / 60),
    answerList,
    aiAnalysis: {
      dimensions: [
        { dimension: '科研诚信薄弱型', score: 78, reason: '整体具备基本诚信意识，但在情境题中对科研流程规范的把握仍不够稳定。' },
        { dimension: '医患沟通焦虑型', score: 82, reason: '面对压力场景时能保持基本沟通逻辑，但表达的同理性还有提升空间。' },
        { dimension: '职业认同模糊型', score: 75, reason: '能够体现职业责任感，但对岗位使命感的表达还不够坚定。' },
        { dimension: '人文关怀缺失型', score: 84, reason: '对患者体验与公平性有一定关注，体现出较好的关怀意识。' },
        { dimension: '综合发展均衡型', score: 80, reason: '整体表现较均衡，没有明显短板，但仍可继续提升稳定性。' }
      ],
      summary: '本次作答整体表现良好，建议继续加强科研规范、临床沟通和职业认同三方面的训练。'
    }
  }

  if (!mockDb.examResultDetails[userId]) {
    mockDb.examResultDetails[userId] = {}
  }
  mockDb.examResultDetails[userId][resultId] = detail

  if (!mockDb.examResults[userId]) {
    mockDb.examResults[userId] = []
  }

  mockDb.examResults[userId].unshift({
    id: resultId,
    title,
    submitTime: detail.submitTime,
    durationMinutes: detail.durationMinutes,
    analysisReady: true
  })

  return createDelay({ success: true, resultId })
}

export function mockGetExamResultList(params = {}) {
  const currentUser = getCurrentUser()
  const userId = params.userId || currentUser.id
  const pageNum = Number(params.pageNum || 1)
  const pageSize = Number(params.pageSize || 10)

  const list = mockDb.examResults[userId] || []
  const start = (pageNum - 1) * pageSize
  const end = start + pageSize

  return createDelay({
    records: list.slice(start, end),
    total: list.length
  })
}

export function mockGetExamResultDetail(resultId, userId) {
  const currentUser = getCurrentUser()
  const targetUserId = userId || currentUser.id
  const detail = mockDb.examResultDetails[targetUserId]?.[resultId]

  return createDelay(
    detail || {
      paperName: '',
      studentNo: '',
      realName: '',
      submitTime: '',
      durationMinutes: 0,
      answerList: [],
      aiAnalysis: {
        dimensions: [],
        summary: ''
      }
    }
  )
}