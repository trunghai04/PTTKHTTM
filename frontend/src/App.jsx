import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import SpamPage from './pages/SpamPage'
import NewsPage from './pages/NewsPage'
import Dashboard from './pages/Dashboard'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/spam" element={<SpamPage />} />
        <Route path="/news" element={<NewsPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
      </Routes>
    </Router>
  )
}

export default App
