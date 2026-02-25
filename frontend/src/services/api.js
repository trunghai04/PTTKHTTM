import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const spamAPI = {
  predict: async (text) => {
    const response = await api.post('/api/spam/predict', { text })
    return response.data
  },
  getHistory: async (limit = 50) => {
    const response = await api.get(`/api/spam/history?limit=${limit}`)
    return response.data
  },
}

export const newsAPI = {
  predict: async (text) => {
    const response = await api.post('/api/news/predict', { text })
    return response.data
  },
  getHistory: async (limit = 50) => {
    const response = await api.get(`/api/news/history?limit=${limit}`)
    return response.data
  },
}

export const statsAPI = {
  getOverview: async () => {
    const response = await api.get('/api/stats/overview')
    return response.data
  },
  getNewsCategories: async () => {
    const response = await api.get('/api/stats/news/categories')
    return response.data
  },
}

export default api
