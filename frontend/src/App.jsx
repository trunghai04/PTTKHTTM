import React from 'react'
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom'
import Home from './pages/Home'
import SpamPage from './pages/SpamPage'
import NewsPage from './pages/NewsPage'
import Dashboard from './pages/Dashboard'
import './App.css'

function App() {
  return (
    <Router>
      <div className="app">
        <nav className="navbar">
          <div className="nav-container">
            <Link to="/" className="nav-logo">
              📊 Text Classification
            </Link>
            <div className="nav-menu">
              <Link to="/" className="nav-link">Home</Link>
              <Link to="/spam" className="nav-link">Spam Detection</Link>
              <Link to="/news" className="nav-link">News Classification</Link>
              <Link to="/dashboard" className="nav-link">Dashboard</Link>
            </div>
          </div>
        </nav>

        <main className="main-content">
          <Routes>
            <Route path="/" element={<Home />} />
            <Route path="/spam" element={<SpamPage />} />
            <Route path="/news" element={<NewsPage />} />
            <Route path="/dashboard" element={<Dashboard />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
