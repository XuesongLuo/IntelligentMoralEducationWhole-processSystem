const ACTIVE_EXAM_STORAGE_KEY = 'active_exam_session'
const EXAM_NOTICE_STORAGE_KEY = 'active_exam_notice_seen'
const EXAM_CLIENT_SESSION_PREFIX = 'exam_client_session'

function readJson(key) {
  try {
    return JSON.parse(localStorage.getItem(key) || 'null')
  } catch {
    return null
  }
}

export function getActiveExamSession() {
  const session = readJson(ACTIVE_EXAM_STORAGE_KEY)
  if (!session || !session.role || !session.type || !session.examId || !session.userId) {
    return null
  }
  return session
}

export function setActiveExamSession({ userId, role, type, examId }) {
  localStorage.setItem(
    ACTIVE_EXAM_STORAGE_KEY,
    JSON.stringify({
      userId,
      role,
      type,
      examId: String(examId),
      updatedAt: Date.now()
    })
  )
}

export function clearActiveExamSession() {
  localStorage.removeItem(ACTIVE_EXAM_STORAGE_KEY)
  sessionStorage.removeItem(EXAM_NOTICE_STORAGE_KEY)
}

function buildClientSessionKey(userId, type, examId) {
  return `${EXAM_CLIENT_SESSION_PREFIX}_${userId}_${type}_${examId}`
}

export function getExamClientSessionId(userId, type, examId) {
  if (!userId || !type || !examId) return ''
  const key = buildClientSessionKey(userId, type, examId)
  const existing = localStorage.getItem(key)
  if (existing) return existing
  const generated =
    globalThis.crypto?.randomUUID?.() ||
    `${Date.now()}_${Math.random().toString(36).slice(2, 10)}`
  localStorage.setItem(key, generated)
  return generated
}

export function resetExamClientSessionId(userId, type, examId) {
  if (!userId || !type || !examId) return ''
  const key = buildClientSessionKey(userId, type, examId)
  const generated =
    globalThis.crypto?.randomUUID?.() ||
    `${Date.now()}_${Math.random().toString(36).slice(2, 10)}`
  localStorage.setItem(key, generated)
  return generated
}

export function buildExamPaperPath(session) {
  return `/${session.role}/exam-paper/${session.type}/${session.examId}`
}

export function isExamPaperRoute(route) {
  return typeof route?.path === 'string' && route.path.includes('/exam-paper/')
}

export function isExamEntryRoute(route, role) {
  if (typeof route?.path !== 'string' || !role) return false
  return (
    route.path === `/${role}/moral-exam` ||
    route.path.startsWith(`/${role}/exam-notice/`) ||
    route.path.startsWith(`/${role}/exam-paper/`)
  )
}

export function shouldShowActiveExamNotice(routePath, activePath) {
  const noticeKey = `${routePath}|${activePath}`
  const lastNoticeKey = sessionStorage.getItem(EXAM_NOTICE_STORAGE_KEY)
  if (lastNoticeKey === noticeKey) {
    return false
  }
  sessionStorage.setItem(EXAM_NOTICE_STORAGE_KEY, noticeKey)
  return true
}
