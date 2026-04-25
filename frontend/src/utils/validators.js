export function isPhone(value) {
  return /^1[3-9]\d{9}$/.test(value)
}

export function isStudentNo(value) {
  return /^[A-Za-z]\d{9}$/.test(String(value || '').trim())
}

export function isTeacherNo(value) {
  return String(value || '').trim().length > 0
}

export function isStudentOrWorkNo(value) {
  return isStudentNo(value) || isTeacherNo(value)
}

export function isPassword(value) {
  return /^.{6,10}$/.test(value)
}

export function isRealName(value) {
  return /^[\u4e00-\u9fa5A-Za-z·\s]{2,20}$/.test(value)
}

export function isSmsCode(value) {
  return /^\d{4,6}$/.test(value)
}

export function isInviteCode(value) {
  return /^[A-Za-z0-9_-]{4,30}$/.test(value)
}

export function isAccount(value) {
  return isPhone(value) || isStudentOrWorkNo(value)
}
