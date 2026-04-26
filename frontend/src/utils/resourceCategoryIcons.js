import publicHealthIcon from '@/assets/images/resource-study/categories/public-health.png'
import doctorPatientDisputeIcon from '@/assets/images/resource-study/categories/doctor-patient-dispute.png'
import medicalFairnessIcon from '@/assets/images/resource-study/categories/medical-fairness.png'
import teamConflictIcon from '@/assets/images/resource-study/categories/team-conflict.png'
import patientPrivacyIcon from '@/assets/images/resource-study/categories/patient-privacy.png'
import researchIntegrityIcon from '@/assets/images/resource-study/categories/research-integrity.png'

const CATEGORY_ICON_MAP = {
  公共卫生事件应对: publicHealthIcon,
  医患纠纷处理: doctorPatientDisputeIcon,
  医疗资源分配公平性: medicalFairnessIcon,
  团队协作冲突: teamConflictIcon,
  患者隐私保护困境: patientPrivacyIcon,
  科研数据造假诱惑: researchIntegrityIcon
}

export function getResourceCategoryIcon(categoryName) {
  return CATEGORY_ICON_MAP[categoryName] || ''
}

export { CATEGORY_ICON_MAP }
