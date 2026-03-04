import React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Home from './pages/Home'
import SpamPage from './pages/SpamPage'
import NewsPage from './pages/NewsPage'
import Dashboard from './pages/Dashboard'
import ScanHistory from './pages/ScanHistory'
import Login from './pages/Login'
import GoogleAuthCallback from './pages/GoogleAuthCallback'
import Docs from './pages/Docs'
import SpamDetail from './pages/SpamDetail'
import NewsDetail from './pages/NewsDetail'
import ProtectedRoute from './components/ProtectedRoute'
import AdminRoute from './components/AdminRoute'
import './App.css'

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/spam" element={<SpamPage />} />
        <Route path="/news" element={<NewsPage />} />
        <Route path="/spam/detail" element={<SpamDetail />} />
        <Route path="/news/detail" element={<NewsDetail />} />
        <Route path="/docs" element={<Docs />} />
        <Route path="/login" element={<Login />} />
        <Route path="/auth/google/callback" element={<GoogleAuthCallback />} />
        <Route
          path="/dashboard"
          element={
            <AdminRoute>
              <Dashboard />
            </AdminRoute>
          }
        />
        <Route
          path="/scan-history"
          element={
            <ProtectedRoute>
              <ScanHistory />
            </ProtectedRoute>
          }
        />
      </Routes>
    </Router>
  )
}

export default App
