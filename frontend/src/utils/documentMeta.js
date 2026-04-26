import defaultFavicon from '@/assets/images/dyq_icon_64_64.ico'
import moralExamHubFavicon from '@/assets/images/home-navigation/moral-exam.ico'
import resultsFavicon from '@/assets/images/home-navigation/results.ico'
import resourceStudyFavicon from '@/assets/images/home-navigation/resource-study.ico'
import surveyFavicon from '@/assets/images/moral-exam/survey.ico'
import integrityFavicon from '@/assets/images/moral-exam/integrity.ico'
import ideologyFavicon from '@/assets/images/moral-exam/ideology.ico'

export const APP_NAME = 'IMEWS 德育全过程智能系统'
export const DEFAULT_FAVICON = defaultFavicon

export const EXAM_TYPE_META = {
  survey: { title: `画像构建 - ${APP_NAME}`, favicon: surveyFavicon },
  integrity: { title: `诚信考核 - ${APP_NAME}`, favicon: integrityFavicon },
  ideology: { title: `思政考试 - ${APP_NAME}`, favicon: ideologyFavicon }
}

export const ROUTE_META_MAP = {
  Login: { title: `登录 - ${APP_NAME}` },
  Register: { title: `注册 - ${APP_NAME}` },
  ResetPassword: { title: `找回密码 - ${APP_NAME}` },
  StudentHome: { title: `首页 - ${APP_NAME}` },
  StudentMoralExamHub: { title: `德育画像构建与考试 - ${APP_NAME}`, favicon: moralExamHubFavicon },
  StudentResults: { title: `结果查看 - ${APP_NAME}`, favicon: resultsFavicon },
  StudentResourceStudyHub: { title: `德育资源学习 - ${APP_NAME}`, favicon: resourceStudyFavicon },
  TeacherHome: { title: `教师首页 - ${APP_NAME}` },
  TeacherMoralExamHub: { title: `德育画像构建与考试 - ${APP_NAME}`, favicon: moralExamHubFavicon },
  TeacherResults: { title: `结果查看 - ${APP_NAME}`, favicon: resultsFavicon },
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

export function getRouteDocumentMeta(route) {
  if (!route?.name) {
    return { title: APP_NAME, favicon: DEFAULT_FAVICON }
  }

  if (
    route.name === 'StudentExamNotice' ||
    route.name === 'StudentExamPaper' ||
    route.name === 'TeacherExamNotice' ||
    route.name === 'TeacherExamPaper'
  ) {
    const examType = route.params?.type
    return EXAM_TYPE_META[examType] || { title: `在线考试 - ${APP_NAME}`, favicon: moralExamHubFavicon }
  }

  return ROUTE_META_MAP[route.name] || { title: APP_NAME, favicon: DEFAULT_FAVICON }
}

export function setDocumentMeta({ title, favicon } = {}) {
  document.title = title || APP_NAME
  const iconLink = ensureFaviconNode()
  iconLink.setAttribute('href', favicon || DEFAULT_FAVICON)
}
