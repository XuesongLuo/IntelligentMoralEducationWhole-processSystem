import request from '@/utils/request'

function getRolePrefix() {
  const userInfo = JSON.parse(localStorage.getItem('userInfo') || '{}')
  return userInfo.role === 'teacher' ? '/teacher' : '/student'
}

export function getResourceCategories(params) {
  return request({
    url: `${getRolePrefix()}/resources/categories`,
    method: 'get',
    params
  })
}

export function getResourceItems(categoryCode, params) {
  return request({
    url: `${getRolePrefix()}/resources/categories/${encodeURIComponent(categoryCode)}/items`,
    method: 'get',
    params
  })
}

export function submitResourceHeartbeat(data = {}) {
  return request({
    url: `${getRolePrefix()}/resources/heartbeat`,
    method: 'post',
    data
  })
}

export function visitResource(resourceId) {
  return request({
    url: `${getRolePrefix()}/resources/${resourceId}/visit`,
    method: 'post'
  })
}

export function createResourceItem(categoryId, data) {
  return request({
    url: '/teacher/resources/categories/' + categoryId + '/items',
    method: 'post',
    data
  })
}

export function updateResourceItem(resourceId, data) {
  return request({
    url: '/teacher/resources/' + resourceId,
    method: 'put',
    data
  })
}

export function updateResourceVisibility(resourceId, isVisible) {
  return request({
    url: '/teacher/resources/' + resourceId + '/visibility',
    method: 'patch',
    data: { isVisible }
  })
}

export function deleteResourceItem(resourceId) {
  return request({
    url: '/teacher/resources/' + resourceId,
    method: 'delete'
  })
}
