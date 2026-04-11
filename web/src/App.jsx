import React, { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import ChatPage from './pages/ChatPage'
import LogicAuditPage from './pages/LogicAuditPage'
import TutorialPage from './pages/TutorialPage'
import TelegramPage from './pages/TelegramPage'
import DocsPage from './pages/DocsPage'
import './App.css'

function App() {
  return (
    <Router>
      <div className="layout-root">
        <Sidebar />
        <main className="main-content">
          <Routes>
            <Route path="/" element={<ChatPage />} />
            <Route path="/audit" element={<LogicAuditPage />} />
            <Route path="/tutorial" element={<TutorialPage />} />
            <Route path="/telegram" element={<TelegramPage />} />
            <Route path="/docs" element={<DocsPage />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}

export default App
