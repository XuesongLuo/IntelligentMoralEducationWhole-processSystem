import defaultFavicon from '@/assets/images/dyq_icon_64_64.ico'
import moralExamFavicon from '@/assets/images/button_德育画像构建与考试_174_174.ico'
import resultFavicon from '@/assets/images/button_结果查看_174_174.ico'
import resourceStudyFavicon from '@/assets/images/button_德育资源学习_174_174.ico'

export const APP_NAME = 'IMEWS 德育全过程智能系统'

export const DEFAULT_FAVICON = defaultFavicon

export const ROUTE_META_MAP = {
  Login: { title: `登录 - ${APP_NAME}` },
  Register: { title: `注册 - ${APP_NAME}` },
  ResetPassword: { title: `找回密码 - ${APP_NAME}` },
  StudentHome: { title: `首页 - ${APP_NAME}` },
  StudentMoralExamHub: { title: `德育画像构建与考试 - ${APP_NAME}`, favicon: moralExamFavicon },
  StudentExamNotice: { title: `考试须知 - ${APP_NAME}`, favicon: moralExamFavicon },
  StudentExamPaper: { title: `在线考试 - ${APP_NAME}`, favicon: moralExamFavicon },
  StudentResults: { title: `结果查看 - ${APP_NAME}`, favicon: resultFavicon },
  StudentResourceStudyHub: { title: `德育资源学习 - ${APP_NAME}`, favicon: resourceStudyFavicon },
  TeacherHome: { title: `教师首页 - ${APP_NAME}` },
  TeacherMoralExamHub: { title: `德育画像构建与考试 - ${APP_NAME}`, favicon: moralExamFavicon },
  TeacherExamNotice: { title: `考试须知 - ${APP_NAME}`, favicon: moralExamFavicon },
  TeacherExamPaper: { title: `在线考试 - ${APP_NAME}`, favicon: moralExamFavicon },
  TeacherResults: { title: `结果查看 - ${APP_NAME}`, favicon: resultFavicon },
  TeacherResourceStudyHub: { title: `德育资源学习 - ${APP_NAME}`, favicon: resourceStudyFavicon },
  TeacherRosterManage: { title: `预录入名单管理 - ${APP_NAME}` }
}

function ensureFaviconNode() {
  let link = document.querySelector('link[rel="icon"]')
  if (!link) {
    link = document.createElement('link')
    link.setAttribute('rel', 'icon')
    document.head.appendChild(link)
  }
  return link
}

export function setDocumentMeta({ title, favicon } = {}) {
  document.title = title || APP_NAME
  const iconLink = ensureFaviconNode()
  iconLink.setAttribute('href', favicon || DEFAULT_FAVICON)
}
