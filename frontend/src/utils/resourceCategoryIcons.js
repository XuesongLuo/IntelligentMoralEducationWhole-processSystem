import publicHealthIcon from '@/assets/images/resource-study/categories/public-health.png'
import doctorPatientDisputeIcon from '@/assets/images/resource-study/categories/doctor-patient-dispute.png'
import medicalFairnessIcon from '@/assets/images/resource-study/categories/medical-fairness.png'
import teamConflictIcon from '@/assets/images/resource-study/categories/team-conflict.png'
import patientPrivacyIcon from '@/assets/images/resource-study/categories/patient-privacy.png'
import researchIntegrityIcon from '@/assets/images/resource-study/categories/research-integrity.png'
import publicHealthFavicon from '@/assets/images/resource-study/categories/public-health.ico'
import doctorPatientDisputeFavicon from '@/assets/images/resource-study/categories/doctor-patient-dispute.ico'
import medicalFairnessFavicon from '@/assets/images/resource-study/categories/medical-fairness.ico'
import teamConflictFavicon from '@/assets/images/resource-study/categories/team-conflict.ico'
import patientPrivacyFavicon from '@/assets/images/resource-study/categories/patient-privacy.ico'
import researchIntegrityFavicon from '@/assets/images/resource-study/categories/research-integrity.ico'

const CATEGORY_ICON_MAP = {
  公共卫生事件应对: publicHealthIcon,
  医患纠纷处理: doctorPatientDisputeIcon,
  医疗资源分配公平性: medicalFairnessIcon,
  团队协作冲突: teamConflictIcon,
  患者隐私保护困境: patientPrivacyIcon,
  科研数据造假诱惑: researchIntegrityIcon
}

const CATEGORY_FAVICON_MAP = {
  公共卫生事件应对: publicHealthFavicon,
  医患纠纷处理: doctorPatientDisputeFavicon,
  医疗资源分配公平性: medicalFairnessFavicon,
  团队协作冲突: teamConflictFavicon,
  患者隐私保护困境: patientPrivacyFavicon,
  科研数据造假诱惑: researchIntegrityFavicon
}

export function getResourceCategoryIcon(categoryName) {
  return CATEGORY_ICON_MAP[categoryName] || ''
}

export function getResourceCategoryFavicon(categoryName) {
  return CATEGORY_FAVICON_MAP[categoryName] || ''
}

export { CATEGORY_ICON_MAP, CATEGORY_FAVICON_MAP }
