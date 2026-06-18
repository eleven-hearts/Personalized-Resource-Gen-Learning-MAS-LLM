import request from './request'

export const login = (data) => {
  const formData = new URLSearchParams()
  formData.append('username', data.username)
  formData.append('password', data.password)

  return request.post('/auth/login', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
  })
}

export const register = (data) => {
  return request.post('/auth/register', data)
}

export const getCurrentUser = () => {
  return request.get('/users/me')
}

export const updateCurrentUser = (data) => {
  return request.put('/users/me', data)
}
