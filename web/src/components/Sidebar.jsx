import React from 'react'
import { NavLink } from 'react-router-dom'
import { Shield, MessageSquare, FlaskConical, BookOpen, Send, FileText } from 'lucide-react'

const NAV = [
  { label: 'SWARM OPERATIONS', items: [
    { to: '/', icon: MessageSquare, label: 'Alpha Swarm' },
    { to: '/audit', icon: FlaskConical, label: 'Logic Audit' },
  ]},
  { label: 'RESOURCES', items: [
    { to: '/tutorial', icon: BookOpen, label: 'Tutorial Flow' },
    { to: '/telegram', icon: Send, label: 'Telegram Bot' },
    { to: '/docs', icon: FileText, label: 'Documentation' },
  ]},
]

export default function Sidebar() {
  return (
    <aside className="sidebar">
      <div className="sidebar-content">
        <div className="sidebar-header">
          <img src="/OxSen.png" alt="Oxlo Sentinel Logo" className="logo-img" />
          <span>SENTINEL HUB</span>
        </div>
        <nav className="sidebar-nav">
          {NAV.map(group => (
            <div key={group.label} className="nav-group">
              <label>{group.label}</label>
              {group.items.map(({ to, icon: Icon, label }) => (
                <NavLink
                  key={to}
                  to={to}
                  end={to === '/'}
                  className={({ isActive }) => `nav-item${isActive ? ' active' : ''}`}
                >
                  <Icon size={16} />
                  <span>{label}</span>
                </NavLink>
              ))}
            </div>
          ))}
        </nav>
        <div className="sidebar-footer">
          <div className="user-badge">
            <img src="/OxSen.png" alt="User Avatar" className="avatar-img" />
            <div>
              <p className="name">Omniscient Core</p>
              <p className="status">Active Node</p>
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}
