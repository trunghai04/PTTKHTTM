import React, { useState } from 'react'
import { spamAPI } from '../services/api'
import './SpamPage.css'

function SpamPage() {
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [history, setHistory] = useState([])
  const [stats, setStats] = useState(null)

  const handlePredict = async () => {
    if (!text.trim()) {
      setError('Vui lòng nhập nội dung email')
      return
    }

    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const response = await spamAPI.predict(text)
      setResult(response)
      // Auto-scroll to result
      setTimeout(() => {
        const el = document.querySelector('.result-card')
        if (el) el.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }, 50)
      // Refresh history
      loadHistory()
    } catch (err) {
      setError(err.response?.data?.detail || 'Có lỗi xảy ra')
    } finally {
      setLoading(false)
    }
  }

  const loadHistory = async () => {
    try {
      const data = await spamAPI.getHistory(10)
      setHistory(data)
    } catch (err) {
      console.error('Failed to load history:', err)
    }
  }

  React.useEffect(() => {
    loadHistory()
  }, [])

  return (
    <div className="spam-page">
      <div className="page-header">
        <h1>📧 Spam Detection</h1>
        <p>Phát hiện email spam với AI</p>
      </div>

      <div className="content-grid">
        <div className="prediction-section">
          <div className="card">
            <h2>Nhập nội dung email</h2>
            <p className="helper-text">
              Ví dụ: <em>“Em đã gửi email đăng ký môn học rồi ạ, thầy xem qua giúp em với.”</em>
            </p>
            <textarea
              className="text-input"
              value={text}
              onChange={(e) => setText(e.target.value)}
              placeholder="Nhập nội dung email cần kiểm tra..."
              rows="8"
            />
            <button
              className="predict-button"
              onClick={handlePredict}
              disabled={loading}
            >
              <span>{loading ? 'Đang xử lý...' : 'Kiểm tra Spam'}</span>
            </button>

            {error && <div className="error-message">{error}</div>}

            {result && (
              <div className="result-card">
                <h3>Kết quả dự đoán</h3>
                <div className={`result-label ${result.label === 'Spam' ? 'spam' : 'not-spam'}`}>
                  {result.label === 'Spam' ? '🚫 Spam' : '✅ Not Spam'}
                </div>
                <div className="confidence-row">
                  <div className="confidence">
                    Độ tin cậy tổng: <strong>{(result.confidence * 100).toFixed(2)}%</strong>
                  </div>
                  <div className="confidence-pill">
                    {result.label === 'Spam' ? 'Nghi ngờ Spam' : 'Có vẻ an toàn'}
                  </div>
                </div>
                <div className="confidence-bar">
                  <div
                    className="confidence-fill"
                    style={{ width: `${result.confidence * 100}%` }}
                  />
                </div>

                {(result.spam_probability != null || result.not_spam_probability != null) && (
                  <div className="probabilities">
                    <div className="prob-title">Phân bố xác suất</div>
                    <div className="prob-grid">
                      <div className="prob-item spam">
                        <span className="prob-label">Spam</span>
                        <span className="prob-value">
                          {((result.spam_probability ?? result.confidence) * 100).toFixed(1)}%
                        </span>
                      </div>
                      <div className="prob-item not-spam">
                        <span className="prob-label">Not Spam</span>
                        <span className="prob-value">
                          {(
                            (result.not_spam_probability ??
                              (1 - (result.spam_probability ?? result.confidence))) * 100
                          ).toFixed(1)}
                          %
                        </span>
                      </div>
                    </div>
                  </div>
                )}

                {result.warning && (
                  <div className="warning-banner">
                    <span>⚠</span>
                    <p>{result.warning}</p>
                  </div>
                )}
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
                      <span className={`label-badge ${item.predicted_label === 'Spam' ? 'spam' : 'not-spam'}`}>
                        {item.predicted_label}
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

export default SpamPage
