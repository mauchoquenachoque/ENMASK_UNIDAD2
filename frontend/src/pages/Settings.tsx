import { useState, useEffect } from 'react';
import { User, Shield, Key, Bell, Save } from 'lucide-react';
import { settingsApi, authApi } from '../services/api';
import type { User as UserType, ApiKey, NotificationPreference } from '../types';
import { useAuth } from '../hooks/useAuth';
import type { ToastType } from '../App';

interface Props {
  addToast: (msg: string, type?: ToastType) => void;
}

type SettingsTab = 'profile' | 'security' | 'api-keys' | 'notifications';

export default function Settings({ addToast }: Props) {
  const { user } = useAuth();
  const [activeTab, setActiveTab] = useState<SettingsTab>('profile');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);

  const [profile, setProfile] = useState({ name: '', email: '' });
  const [passwords, setPasswords] = useState({ old: '', newPass: '', confirm: '' });
  const [apiKeys, setApiKeys] = useState<ApiKey[]>([]);
  const [newKeyName, setNewKeyName] = useState('');
  const [notifications, setNotifications] = useState<NotificationPreference>({
    email_on_job_complete: true,
    email_on_job_fail: true,
    email_on_scan_complete: false,
    slack_webhook: null,
    teams_webhook: null,
  });

  useEffect(() => {
    if (user) {
      setProfile({ name: user.name, email: user.email });
    }
  }, [user]);

  useEffect(() => {
    const loadTabData = async () => {
      setLoading(true);
      try {
        if (activeTab === 'api-keys') {
          const keys = await settingsApi.getApiKeys();
          setApiKeys(keys);
        } else if (activeTab === 'notifications') {
          const prefs = await settingsApi.getNotifications();
          setNotifications(prefs);
        }
      } catch {
        // silent
      } finally {
        setLoading(false);
      }
    };
    loadTabData();
  }, [activeTab]);

  const handleSaveProfile = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await settingsApi.updateProfile(profile);
      addToast('Profile updated', 'success');
    } catch (err: unknown) {
      addToast((err as Error).message || 'Failed to update profile', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleChangePassword = async (e: React.FormEvent) => {
    e.preventDefault();
    if (passwords.newPass !== passwords.confirm) {
      addToast('Passwords do not match', 'error');
      return;
    }
    setSaving(true);
    try {
      await authApi.changePassword(passwords.old, passwords.newPass);
      addToast('Password changed', 'success');
      setPasswords({ old: '', newPass: '', confirm: '' });
    } catch (err: unknown) {
      addToast((err as Error).message || 'Failed to change password', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleCreateApiKey = async () => {
    if (!newKeyName) return;
    try {
      const key = await settingsApi.createApiKey(newKeyName, ['read', 'write']);
      setApiKeys(prev => [...prev, key]);
      setNewKeyName('');
      addToast('API key created. Copy it now - it won\'t be shown again.', 'success');
    } catch (err: unknown) {
      addToast((err as Error).message || 'Failed to create API key', 'error');
    }
  };

  const handleDeleteApiKey = async (id: string) => {
    if (!confirm('Delete this API key?')) return;
    try {
      await settingsApi.deleteApiKey(id);
      setApiKeys(prev => prev.filter(k => k.id !== id));
      addToast('API key deleted', 'success');
    } catch {
      addToast('Failed to delete API key', 'error');
    }
  };

  const handleSaveNotifications = async () => {
    setSaving(true);
    try {
      await settingsApi.updateNotifications(notifications);
      addToast('Notification preferences saved', 'success');
    } catch (err: unknown) {
      addToast((err as Error).message || 'Failed to save preferences', 'error');
    } finally {
      setSaving(false);
    }
  };

  const tabs: { key: SettingsTab; label: string; icon: typeof User }[] = [
    { key: 'profile', label: 'Profile', icon: User },
    { key: 'security', label: 'Security', icon: Shield },
    { key: 'api-keys', label: 'API Keys', icon: Key },
    { key: 'notifications', label: 'Notifications', icon: Bell },
  ];

  return (
    <div className="settings-layout">
      <div className="settings-sidebar">
        {tabs.map(tab => (
          <button
            key={tab.key}
            className={`settings-tab ${activeTab === tab.key ? 'active' : ''}`}
            onClick={() => setActiveTab(tab.key)}
          >
            <tab.icon size={18} />
            <span>{tab.label}</span>
          </button>
        ))}
      </div>

      <div className="settings-content">
        {activeTab === 'profile' && (
          <div className="card">
            <div className="card-header">
              <h2>Profile</h2>
            </div>
            <form onSubmit={handleSaveProfile}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Full Name</label>
                  <input value={profile.name} onChange={e => setProfile(p => ({ ...p, name: e.target.value }))} />
                </div>
                <div className="form-group">
                  <label>Email</label>
                  <input type="email" value={profile.email} onChange={e => setProfile(p => ({ ...p, email: e.target.value }))} />
                </div>
                <div className="form-group">
                  <label>Role</label>
                  <input value={user?.role || ''} disabled />
                </div>
              </div>
              <div className="form-actions">
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? <><span className="spinner" /> Saving...</> : <><Save size={16} /> Save Changes</>}
                </button>
              </div>
            </form>
          </div>
        )}

        {activeTab === 'security' && (
          <div className="card">
            <div className="card-header">
              <h2>Change Password</h2>
            </div>
            <form onSubmit={handleChangePassword}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Current Password</label>
                  <input type="password" required value={passwords.old} onChange={e => setPasswords(p => ({ ...p, old: e.target.value }))} />
                </div>
                <div className="form-group">
                  <label>New Password</label>
                  <input type="password" required minLength={8} value={passwords.newPass} onChange={e => setPasswords(p => ({ ...p, newPass: e.target.value }))} />
                </div>
                <div className="form-group">
                  <label>Confirm New Password</label>
                  <input type="password" required value={passwords.confirm} onChange={e => setPasswords(p => ({ ...p, confirm: e.target.value }))} />
                </div>
              </div>
              <div className="form-actions">
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? <><span className="spinner" /> Updating...</> : 'Change Password'}
                </button>
              </div>
            </form>
          </div>
        )}

        {activeTab === 'api-keys' && (
          <div className="card">
            <div className="card-header">
              <h2>API Keys</h2>
            </div>
            <div className="api-key-create">
              <input
                placeholder="Key name..."
                value={newKeyName}
                onChange={e => setNewKeyName(e.target.value)}
              />
              <button className="btn btn-primary btn-sm" onClick={handleCreateApiKey} disabled={!newKeyName}>
                <Key size={14} /> Create Key
              </button>
            </div>
            {loading ? (
              <div className="loading-state"><div className="spinner" /></div>
            ) : apiKeys.length === 0 ? (
              <div className="empty-state" style={{ padding: '32px 0' }}>
                <p>No API keys. Create one to get started.</p>
              </div>
            ) : (
              <div className="table-wrapper">
                <table>
                  <thead>
                    <tr><th>Name</th><th>Key Prefix</th><th>Scopes</th><th>Last Used</th><th></th></tr>
                  </thead>
                  <tbody>
                    {apiKeys.map(k => (
                      <tr key={k.id}>
                        <td><strong>{k.name}</strong></td>
                        <td><code className="code-inline">{k.key_prefix}...</code></td>
                        <td>{k.scopes.join(', ')}</td>
                        <td>{k.last_used ? new Date(k.last_used).toLocaleDateString() : 'Never'}</td>
                        <td>
                          <button className="btn btn-danger btn-sm" onClick={() => handleDeleteApiKey(k.id)}>Delete</button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        )}

        {activeTab === 'notifications' && (
          <div className="card">
            <div className="card-header">
              <h2>Notification Preferences</h2>
            </div>
            <div className="form-grid">
              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={notifications.email_on_job_complete}
                  onChange={e => setNotifications(p => ({ ...p, email_on_job_complete: e.target.checked }))}
                />
                <span>Email on job completion</span>
              </label>
              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={notifications.email_on_job_fail}
                  onChange={e => setNotifications(p => ({ ...p, email_on_job_fail: e.target.checked }))}
                />
                <span>Email on job failure</span>
              </label>
              <label className="toggle-label">
                <input
                  type="checkbox"
                  checked={notifications.email_on_scan_complete}
                  onChange={e => setNotifications(p => ({ ...p, email_on_scan_complete: e.target.checked }))}
                />
                <span>Email on discovery scan completion</span>
              </label>
              <div className="form-group">
                <label>Slack Webhook URL</label>
                <input
                  value={notifications.slack_webhook || ''}
                  onChange={e => setNotifications(p => ({ ...p, slack_webhook: e.target.value || null }))}
                  placeholder="https://hooks.slack.com/..."
                />
              </div>
              <div className="form-group">
                <label>Teams Webhook URL</label>
                <input
                  value={notifications.teams_webhook || ''}
                  onChange={e => setNotifications(p => ({ ...p, teams_webhook: e.target.value || null }))}
                  placeholder="https://outlook.office.com/webhook/..."
                />
              </div>
            </div>
            <div className="form-actions">
              <button className="btn btn-primary" onClick={handleSaveNotifications} disabled={saving}>
                {saving ? <><span className="spinner" /> Saving...</> : <><Save size={16} /> Save Preferences</>}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
