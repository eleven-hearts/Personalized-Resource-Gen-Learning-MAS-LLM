import request from './request'

/** 上传PDF并生成学习路径 */
export const uploadPDF = (file) => {
  const formData = new FormData()
  formData.append('file', file)
  return request.post('/quiz/upload-pdf', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
    timeout: 120000, // 2分钟超时，AI生成需要时间
  })
}

/** 获取用户的所有学习路径 */
export const getLearningPaths = () => {
  return request.get('/quiz/paths')
}

/** 获取学习路径详情 */
export const getLearningPath = (pathId) => {
  return request.get(`/quiz/path/${pathId}`)
}

/** 为节点生成题目 */
export const generateQuestions = (nodeId) => {
  return request.post(`/quiz/node/${nodeId}/generate-questions`, {}, {
    timeout: 120000,
  })
}

/** 获取节点题目（不含答案） */
export const getQuestions = (nodeId) => {
  return request.get(`/quiz/node/${nodeId}/questions`)
}

/** 提交答题 */
export const submitQuiz = (nodeId, answers) => {
  return request.post(`/quiz/node/${nodeId}/submit`, answers)
}

/** 智能体根据答题准确率生成学习画像 */
export const generateProfile = () => {
  return request.post('/quiz/generate-profile', {}, {
    timeout: 120000,
  })
}

/** 将资源添加到学习路径节点 */
export const addResourceToNode = (nodeId, resourceId) => {
  return request.post(`/quiz/node/${nodeId}/add-resource?resource_id=${resourceId}`)
}

/** 从学习资源生成新学习路径 */
export const generatePathFromResource = (resourceId) => {
  return request.post(`/agents/generate-path-from-resource/${resourceId}`, {}, {
    timeout: 300000, // 5分钟超时
  })
}

/** 删除学习路径 */
export const deleteLearningPath = (pathId) => {
  return request.delete(`/quiz/path/${pathId}`)
}
