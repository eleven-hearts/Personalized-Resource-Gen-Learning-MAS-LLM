import request from './request'

export const login = (data) => {
  return request.post('/auth/login', data, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })
}

export const register = (data) => {
  return request.post('/auth/register', data)
}
