import React from 'react'
import { Link } from 'react-router-dom'
import './Home.css'

function Home() {
  return (
    <div className="home">
      <div className="hero">
        <h1>Text Classification System</h1>
        <p className="subtitle">
          Hệ thống phân loại văn bản thông minh với AI
        </p>
        <p className="description">
          Phân loại Email Spam và Phân loại Tin tức theo 5 chủ đề
        </p>
      </div>

      <div className="features">
        <div className="feature-card">
          <div className="feature-icon">📧</div>
          <h2>Spam Detection</h2>
          <p>Phát hiện email spam với độ chính xác cao</p>
          <Link to="/spam" className="feature-button">
            <span>Thử ngay</span>
          </Link>
        </div>

        <div className="feature-card">
          <div className="feature-icon">📰</div>
          <h2>News Classification</h2>
          <p>Phân loại tin tức theo 5 chủ đề: Thể thao, Chính trị, Kinh tế, Công nghệ, Giải trí</p>
          <Link to="/news" className="feature-button">
            <span>Thử ngay</span>
          </Link>
        </div>

        <div className="feature-card">
          <div className="feature-icon">📊</div>
          <h2>Statistics Dashboard</h2>
          <p>Xem thống kê và biểu đồ phân tích dữ liệu</p>
          <Link to="/dashboard" className="feature-button">
            <span>Xem thống kê</span>
          </Link>
        </div>
      </div>

      <div className="info-section">
        <h2>Về hệ thống</h2>
        <div className="info-grid">
          <div className="info-item">
            <h3>🤖 AI Models</h3>
            <p>2 mô hình độc lập sử dụng TF-IDF và Logistic Regression</p>
          </div>
          <div className="info-item">
            <h3>📈 Real-time</h3>
            <p>Dự đoán và lưu lịch sử ngay lập tức</p>
          </div>
          <div className="info-item">
            <h3>💾 Database</h3>
            <p>Lưu trữ lịch sử dự đoán với PostgreSQL</p>
          </div>
          <div className="info-item">
            <h3>🎯 Accuracy</h3>
            <p>Hiển thị độ tin cậy cho mỗi dự đoán</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Home
