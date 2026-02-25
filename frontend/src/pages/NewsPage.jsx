import React, { useState } from 'react'
import { newsAPI } from '../services/api'
import './NewsPage.css'

const categories = {
  'Thể thao': '⚽',
  'Chính trị': '🏛️',
  'Kinh tế': '💰',
  'Công nghệ': '💻',
  'Giải trí': '🎬'
}

function NewsPage() {
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])

  const handlePredict = async () => {
    if (!text.trim()) {
      setError('Vui lòng nhập nội dung tin tức')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await newsAPI.predict(text)
      setResult(response)
      loadHistory()
    } catch (err) {
      setError(err.response?.data?.detail || 'Có lỗi xảy ra')
    } finally {
      setLoading(false)
    }
  }

  const loadHistory = async () => {
    try {
      const data = await newsAPI.getHistory(10)
      setHistory(data)
    } catch (err) {
      console.error('Failed to load history:', err)
    }
  }

  React.useEffect(() => {
    loadHistory()
  }, [])

  const getCategoryIcon = (label) => {
    return categories[label] || '📰'
  }

  const getCategoryColor = (label) => {
    const colors = {
      'Thể thao': '#4CAF50',
      'Chính trị': '#2196F3',
      'Kinh tế': '#FF9800',
      'Công nghệ': '#9C27B0',
      'Giải trí': '#E91E63'
    }
    return colors[label] || '#667eea'
  }

  return (
    <div className="news-page">
      <div className="page-header">
        <h1>📰 News Classification</h1>
        <p>Phân loại tin tức theo 5 chủ đề</p>
      </div>

      <div className="content-grid">
        <div className="prediction-section">
          <div className="card">
            <h2>Nhập nội dung tin tức</h2>
            <p className="helper-text">
              Ví dụ: <em>“Messi ghi bàn trong trận chung kết World Cup...”</em>
            </p>
            <textarea
              className="text-input"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Nhập nội dung tin tức cần phân loại..."
              rows="8"
            />
            <button
              className="predict-button"
              onClick={handlePredict}
              disabled={loading}
            >
              <span>{loading ? 'Đang xử lý...' : 'Phân loại'}</span>
            </button>

            {error && <div className="error-message">{error}</div>}

            {result && (
              <div className="result-card">
                <h3>Kết quả dự đoán</h3>
                <div
                  className="result-label"
                  style={{ borderColor: getCategoryColor(result.label) }}
                >
                  <span className="category-icon">
                    {getCategoryIcon(result.label)}
                  </span>
                  <span>{result.label}</span>
                </div>
                <div className="confidence">
                  Độ tin cậy: <strong>{(result.confidence * 100).toFixed(2)}%</strong>
                </div>
                <div className="confidence-bar">
                  <div
                    className="confidence-fill"
                    style={{
                      width: `${result.confidence * 100}%`,
                      background: getCategoryColor(result.label)
                    }}
                  />
                </div>
              </div>
            )}
          </div>
        </div>

        <div className="history-section">
          <div className="card">
            <h2>Lịch sử dự đoán</h2>
            <button className="refresh-button" onClick={loadHistory}>
              🔄 Làm mới
            </button>
            <div className="history-list">
              {history.length === 0 ? (
                <p className="no-history">Chưa có lịch sử</p>
              ) : (
                history.map((item) => (
                  <div key={item.id} className="history-item">
                    <div className="history-label">
                      <span
                        className="label-badge"
                        style={{ backgroundColor: getCategoryColor(item.predicted_label) }}
                      >
                        {getCategoryIcon(item.predicted_label)} {item.predicted_label}
                      </span>
                      <span className="confidence-badge">
                        {(item.confidence * 100).toFixed(0)}%
                      </span>
                    </div>
                    <p className="history-text">{item.text.substring(0, 100)}...</p>
                    <small className="history-date">
                      {new Date(item.created_at).toLocaleString('vi-VN')}
                    </small>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default NewsPage
