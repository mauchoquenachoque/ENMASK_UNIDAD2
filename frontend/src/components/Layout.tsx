import { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Menu, Bell, Search } from 'lucide-react';
import Sidebar from './Sidebar';
import { useAuth } from '../hooks/useAuth';

const pageMeta: Record<string, { title: string; description: string }> = {
  '/': { title: 'Dashboard', description: 'Platform overview and key metrics' },
  '/connections': { title: 'Connections', description: 'Manage database connections' },
  '/rules': { title: 'Masking Rules', description: 'Define data masking strategies' },
  '/jobs': { title: 'Jobs', description: 'Run and monitor masking operations' },
  '/discovery': { title: 'Discovery', description: 'Scan and identify sensitive data' },
  '/reports': { title: 'Reports', description: 'Compliance and risk reporting' },
  '/schedules': { title: 'Schedules', description: 'Automated job scheduling' },
  '/settings': { title: 'Settings', description: 'Account and system preferences' },
  '/admin': { title: 'Administration', description: 'User and system management' },
};

export default function Layout({ children }: { children: React.ReactNode }) {
  const { user } = useAuth();
  const location = useLocation();
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  const meta = pageMeta[location.pathname] || pageMeta['/'];

  return (
    <div className="app-shell">
      <Sidebar
        collapsed={sidebarCollapsed}
        onToggle={() => setSidebarCollapsed(!sidebarCollapsed)}
        mobileOpen={mobileOpen}
        onMobileClose={() => setMobileOpen(false)}
      />
      <div className="main-content">
        <header className="topbar">
          <div className="topbar-left">
            <button className="topbar-menu-btn" onClick={() => setMobileOpen(true)}>
              <Menu size={20} />
            </button>
            <button className="topbar-collapse-btn" onClick={() => setSidebarCollapsed(!sidebarCollapsed)}>
              <Menu size={18} />
            </button>
            <div className="topbar-title">
              <h1>{meta.title}</h1>
              <p>{meta.description}</p>
            </div>
          </div>
          <div className="topbar-actions">
            <div className="topbar-search">
              <Search size={16} />
              <input type="text" placeholder="Search..." />
            </div>
            <button className="topbar-icon-btn">
              <Bell size={18} />
              <span className="topbar-icon-badge">3</span>
            </button>
            {user && (
              <div className="topbar-user">
                <div className="topbar-user-avatar">
                  {user.picture ? (
                    <img src={user.picture} alt={user.name} />
                  ) : (
                    <span>{user.name.charAt(0).toUpperCase()}</span>
                  )}
                </div>
              </div>
            )}
          </div>
        </header>
        <main className="page-content">
          {children}
        </main>
      </div>
    </div>
  );
}
