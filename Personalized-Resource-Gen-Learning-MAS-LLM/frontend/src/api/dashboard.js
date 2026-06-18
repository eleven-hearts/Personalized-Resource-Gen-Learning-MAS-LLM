import request from './request'

export const getDashboardStats = () => {
  return request.get('/dashboard/stats')
}

/** 获取错题本 */
export const getWrongAnswers = () => {
  return request.get('/dashboard/wrong-answers')
}
