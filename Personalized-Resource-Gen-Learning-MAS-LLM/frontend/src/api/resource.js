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
  return request.post('/agents/generate', data)
}

export const generateLearningPath = (data) => {
  return request.post('/agents/learning-path', data)
}
