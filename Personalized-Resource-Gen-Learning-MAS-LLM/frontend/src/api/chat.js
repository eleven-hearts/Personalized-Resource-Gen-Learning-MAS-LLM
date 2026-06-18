import request from './request'

export const sendChatMessage = (data) => {
  return request.post('/chat/message', data)
}
