import request from './request'

export const getDashboardStats = () => {
  return request.get('/dashboard/stats')
}

/** 获取错题本 */
export const getWrongAnswers = () => {
  return request.get('/dashboard/wrong-answers')
}

/** 删除单道错题 */
export const deleteWrongAnswer = (id) => {
  return request.delete(`/dashboard/wrong-answers/${id}`)
}
