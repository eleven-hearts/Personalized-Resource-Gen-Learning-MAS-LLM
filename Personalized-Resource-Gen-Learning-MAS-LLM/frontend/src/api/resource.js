import request from './request'

export const getResources = (params) => {
  return request.get('/resources/', { params })
}

export const createResource = (data) => {
  return request.post('/resources/', data)
}

export const getResource = (id) => {
  return request.get(`/resources/${id}`)
}

export const deleteResource = (id) => {
  return request.delete(`/resources/${id}`)
}

export const generateResources = (data) => {
  return request.post('/agents/generate', data, {
    timeout: 300000, // 5分钟超时，AI生成需要时间
  })
}

export const generateLearningPath = (data) => {
  return request.post('/agents/learning-path', data)
}
