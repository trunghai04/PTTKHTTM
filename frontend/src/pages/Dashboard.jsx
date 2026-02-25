import React, { useState, useEffect } from 'react'
import { statsAPI } from '../services/api'
import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip, BarChart, Bar, XAxis, YAxis, CartesianGrid } from 'recharts'
import './Dashboard.css'

const COLORS = {
  'Thể thao': '#4CAF50',
  'Chính trị': '#2196F3',
  'Kinh tế': '#FF9800',
  'Công nghệ': '#9C27B0',
  'Giải trí': '#E91E63',
  'Spam': '#F44336',
  'Not Spam': '#4CAF50'
}

function Dashboard() {
  const [overview, setOverview] = useState(null)
  const [newsCategories, setNewsCategories] = useState([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      setLoading(true)
      const [overviewData, categoriesData] = await Promise.all([
        statsAPI.getOverview(),
        statsAPI.getNewsCategories()
      ])
      setOverview(overviewData)
      setNewsCategories(categoriesData)
    } catch (err) {
      console.error('Failed to load stats:', err)
    } finally {
      setLoading(false)
    }
  }

  if (loading) {
    return (
      <div className="dashboard">
        <div className="loading">Đang tải dữ liệu...</div>
      </div>
    )
  }

  const pieData = newsCategories.map(item => ({
    name: item.category,
    value: item.count
  }))

  const spamData = overview?.spam_distribution ? [
    { name: 'Spam', value: overview.spam_distribution['Spam'] || 0 },
    { name: 'Not Spam', value: overview.spam_distribution['Not Spam'] || 0 }
  ] : []

  const newsBarData = newsCategories.map(item => ({
    category: item.category,
    count: item.count
  }))

  return (
    <div className="dashboard">
      <div className="page-header">
        <h1>📊 Statistics Dashboard</h1>
        <p>Thống kê và phân tích dữ liệu</p>
        <button className="refresh-button" onClick={loadStats}>
          🔄 Làm mới
        </button>
      </div>

      {overview && (
        <>
          <div className="stats-overview">
            <div className="stat-card">
              <div className="stat-icon">📈</div>
              <div className="stat-value">{overview.total_predictions}</div>
              <div className="stat-label">Tổng dự đoán</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">📧</div>
              <div className="stat-value">{overview.spam_total}</div>
              <div className="stat-label">Spam Detection</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">📰</div>
              <div className="stat-value">{overview.news_total}</div>
              <div className="stat-label">News Classification</div>
            </div>
            <div className="stat-card">
              <div className="stat-icon">🎯</div>
              <div className="stat-value">{(overview.average_confidence * 100).toFixed(1)}%</div>
              <div className="stat-label">Độ tin cậy TB</div>
            </div>
          </div>

          <div className="charts-grid">
            <div className="chart-card">
              <h2>Phân bố chủ đề Tin tức</h2>
              {pieData.length > 0 ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={pieData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {pieData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[entry.name] || '#8884d8'} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="no-data">Chưa có dữ liệu</div>
              )}
            </div>

            <div className="chart-card">
              <h2>Phân bố Spam</h2>
              {spamData.length > 0 && spamData.some(d => d.value > 0) ? (
                <ResponsiveContainer width="100%" height={300}>
                  <PieChart>
                    <Pie
                      data={spamData}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={100}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {spamData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={COLORS[entry.name] || '#8884d8'} />
                      ))}
                    </Pie>
                    <Tooltip />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                <div className="no-data">Chưa có dữ liệu</div>
              )}
            </div>
          </div>

          <div className="chart-card full-width">
            <h2>Thống kê theo chủ đề Tin tức</h2>
            {newsBarData.length > 0 ? (
              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={newsBarData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="category" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  <Bar dataKey="count" fill="#667eea" />
                </BarChart>
              </ResponsiveContainer>
            ) : (
              <div className="no-data">Chưa có dữ liệu</div>
            )}
          </div>

          <div className="distribution-cards">
            <div className="dist-card">
              <h3>Spam Distribution</h3>
              {overview.spam_distribution && Object.keys(overview.spam_distribution).length > 0 ? (
                <div className="dist-list">
                  {Object.entries(overview.spam_distribution).map(([label, count]) => (
                    <div key={label} className="dist-item">
                      <span className="dist-label">{label}</span>
                      <span className="dist-count">{count}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="no-data">Chưa có dữ liệu</p>
              )}
            </div>

            <div className="dist-card">
              <h3>News Distribution</h3>
              {overview.news_distribution && Object.keys(overview.news_distribution).length > 0 ? (
                <div className="dist-list">
                  {Object.entries(overview.news_distribution).map(([label, count]) => (
                    <div key={label} className="dist-item">
                      <span className="dist-label">{label}</span>
                      <span className="dist-count">{count}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="no-data">Chưa có dữ liệu</p>
              )}
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default Dashboard
