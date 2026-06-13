import { NavLink, useLocation } from 'react-router-dom';
import {
  LayoutDashboard, Database, Shield, Play, Search, FileText,
  Clock, Settings, Users, ChevronDown, ChevronRight, Bell, LogOut, Menu, X,
} from 'lucide-react';
import { useState, useMemo } from 'react';
import { useAuth } from '../hooks/useAuth';
import type { LucideIcon } from 'lucide-react';

interface NavItem {
  to: string;
  label: string;
  icon: LucideIcon;
  permission?: string;
  badge?: number;
}

interface NavSection {
  label: string;
  items: NavItem[];
  permission?: string;
}

const sections: NavSection[] = [
  {
    label: 'Overview',
    items: [
      { to: '/', label: 'Dashboard', icon: LayoutDashboard },
    ],
  },
  {
    label: 'Data Protection',
    items: [
      { to: '/connections', label: 'Connections', icon: Database },
      { to: '/rules', label: 'Masking Rules', icon: Shield },
      { to: '/jobs', label: 'Jobs', icon: Play },
      { to: '/discovery', label: 'Discovery', icon: Search },
    ],
  },
  {
    label: 'Operations',
    items: [
      { to: '/reports', label: 'Reports', icon: FileText },
      { to: '/schedules', label: 'Schedules', icon: Clock },
    ],
  },
  {
    label: 'Administration',
    items: [
      { to: '/settings', label: 'Settings', icon: Settings },
      { to: '/admin', label: 'User Management', icon: Users, permission: 'admin' },
    ],
  },
];

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
  mobileOpen: boolean;
  onMobileClose: () => void;
}

export default function Sidebar({ collapsed, onToggle, mobileOpen, onMobileClose }: SidebarProps) {
  const { user, logout, hasPermission } = useAuth();
  const location = useLocation();
  const [expandedSections, setExpandedSections] = useState<Set<string>>(new Set(sections.map(s => s.label)));

  const toggleSection = (label: string) => {
    setExpandedSections(prev => {
      const next = new Set(prev);
      if (next.has(label)) next.delete(label);
      else next.add(label);
      return next;
    });
  };

  const visibleSections = useMemo(() => {
    return sections
      .map(section => ({
        ...section,
        items: section.items.filter(item => {
          if (item.permission === 'admin') return user?.role === 'admin';
          return true;
        }),
      }))
      .filter(section => section.items.length > 0);
  }, [user]);

  return (
    <>
      {mobileOpen && <div className="sidebar-overlay" onClick={onMobileClose} />}
      <aside className={`sidebar ${collapsed ? 'sidebar-collapsed' : ''} ${mobileOpen ? 'sidebar-mobile-open' : ''}`}>
        <div className="sidebar-logo">
          <div className="logo-icon">E</div>
          {!collapsed && (
            <>
              <span className="logo-text">Enmask</span>
              <span className="logo-badge">SDM</span>
            </>
          )}
          <button className="sidebar-mobile-close" onClick={onMobileClose}>
            <X size={18} />
          </button>
        </div>

        <nav className="sidebar-nav">
          {visibleSections.map(section => (
            <div key={section.label} className="sidebar-section">
              {!collapsed && (
                <button
                  className="sidebar-section-toggle"
                  onClick={() => toggleSection(section.label)}
                >
                  <span className="sidebar-section-label">{section.label}</span>
                  {expandedSections.has(section.label) ? <ChevronDown size={12} /> : <ChevronRight size={12} />}
                </button>
              )}
              {(collapsed || expandedSections.has(section.label)) && (
                <div className="sidebar-section-items">
                  {section.items.map(item => (
                    <NavLink
                      key={item.to}
                      to={item.to}
                      end={item.to === '/'}
                      className={({ isActive }) => `nav-item ${isActive ? 'active' : ''}`}
                      onClick={onMobileClose}
                      title={collapsed ? item.label : undefined}
                    >
                      <item.icon size={18} />
                      {!collapsed && <span>{item.label}</span>}
                      {!collapsed && item.badge !== undefined && item.badge > 0 && (
                        <span className="nav-badge">{item.badge}</span>
                      )}
                    </NavLink>
                  ))}
                </div>
              )}
            </div>
          ))}
        </nav>

        <div className="sidebar-footer">
          {user && !collapsed && (
            <div className="sidebar-user">
              <div className="sidebar-user-avatar">
                {user.picture ? (
                  <img src={user.picture} alt={user.name} />
                ) : (
                  <span>{user.name.charAt(0).toUpperCase()}</span>
                )}
              </div>
              <div className="sidebar-user-info">
                <span className="sidebar-user-name">{user.name}</span>
                <span className="sidebar-user-role">{user.role}</span>
              </div>
              <button className="sidebar-logout" onClick={logout} title="Sign out">
                <LogOut size={16} />
              </button>
            </div>
          )}
          {!collapsed && (
            <div className="sidebar-version">Enmask v2.0.0</div>
          )}
        </div>
      </aside>
    </>
  );
}
