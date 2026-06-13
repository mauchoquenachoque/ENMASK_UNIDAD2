import { useEffect, useState, useCallback } from 'react';
import { Plus, Search, Trash2, TestTube, Database as DatabaseIcon, Wifi, WifiOff } from 'lucide-react';
import { connectionsApi, rulesApi } from '../services/api';
import type { Connection, ConnectionCreate, RuleCreate, DatabaseType } from '../types';
import { DATABASE_TYPES } from '../types';
import StatusBadge from '../components/StatusBadge';
import type { ToastType } from '../App';

interface Props {
  addToast: (msg: string, type?: ToastType) => void;
}

const defaultForm: ConnectionCreate = {
  name: '', type: 'postgres', host: 'localhost',
  port: 5432, database: '', username: '', password: '',
  ssl_enabled: false, pool_size: 5,
};

export default function Connections({ addToast }: Props) {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState<ConnectionCreate>(defaultForm);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [showDiscoverModal, setShowDiscoverModal] = useState(false);
  const [discovering, setDiscovering] = useState(false);
  const [suggestions, setSuggestions] = useState<RuleCreate[]>([]);
  const [selectedSuggestions, setSelectedSuggestions] = useState<number[]>([]);
  const [creatingSuggestions, setCreatingSuggestions] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await connectionsApi.listAll();
      setConnections(data);
    } catch {
      addToast('Failed to load connections', 'error');
    } finally {
      setLoading(false);
    }
  }, [addToast]);

  useEffect(() => { load(); }, [load]);

  const handleTypeChange = (t: DatabaseType) => {
    const dbType = DATABASE_TYPES.find(d => d.value === t);
    setForm(prev => ({ ...prev, type: t, port: dbType?.defaultPort || 5432 }));
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      await connectionsApi.create(form);
      addToast('Connection created successfully', 'success');
      setShowModal(false);
      setForm(defaultForm);
      load();
    } catch (err: unknown) {
      addToast((err as Error).message || 'Failed to create connection', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string, name: string) => {
    if (!confirm(`Delete connection "${name}"?`)) return;
    try {
      await connectionsApi.delete(id);
      addToast(`Connection "${name}" deleted`, 'success');
      load();
    } catch {
      addToast('Failed to delete connection', 'error');
    }
  };

  const handleTest = async (id: string) => {
    setTesting(id);
    try {
      const result = await connectionsApi.test(id);
      if (result.success) {
        addToast(`Connection OK (${result.latency_ms}ms, ${result.server_version})`, 'success');
      } else {
        addToast(`Connection failed: ${result.message}`, 'error');
      }
      load();
    } catch (err: unknown) {
      addToast((err as Error).message || 'Test failed', 'error');
    } finally {
      setTesting(null);
    }
  };

  const handleDiscover = async (id: string) => {
    setDiscovering(true);
    setShowDiscoverModal(true);
    setSuggestions([]);
    setSelectedSuggestions([]);
    try {
      const data = await connectionsApi.discover(id);
      setSuggestions(data);
      setSelectedSuggestions(data.map((_, idx) => idx));
      if (data.length === 0) addToast('No PII columns detected', 'info');
    } catch (err: unknown) {
      addToast((err as Error).message || 'Discovery failed', 'error');
      setShowDiscoverModal(false);
    } finally {
      setDiscovering(false);
    }
  };

  const handleCreateSuggestions = async () => {
    setCreatingSuggestions(true);
    try {
      const selected = selectedSuggestions.map(idx => suggestions[idx]);
      await rulesApi.bulkCreate(selected);
      addToast(`${selected.length} rules created`, 'success');
      setShowDiscoverModal(false);
    } catch (err: unknown) {
      addToast((err as Error).message || 'Failed to create rules', 'error');
    } finally {
      setCreatingSuggestions(false);
    }
  };

  const filtered = connections.filter(c =>
    c.name.toLowerCase().includes(search.toLowerCase()) ||
    c.type.toLowerCase().includes(search.toLowerCase()) ||
    c.host.toLowerCase().includes(search.toLowerCase())
  );

  return (
    <div>
      <div className="card">
        <div className="card-header">
          <div className="card-header-left">
            <h2>Database Connections</h2>
            <span className="card-count">{connections.length}</span>
          </div>
          <div className="card-header-right">
            <div className="search-input">
              <Search size={16} />
              <input
                type="text"
                placeholder="Search connections..."
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>
            <button className="btn btn-primary" onClick={() => setShowModal(true)}>
              <Plus size={16} /> Add Connection
            </button>
          </div>
        </div>

        {loading ? (
          <div className="loading-state"><div className="spinner" /></div>
        ) : filtered.length === 0 ? (
          <div className="empty-state">
            <DatabaseIcon size={48} />
            <h3>No connections yet</h3>
            <p>Add your first database connection to get started.</p>
            <button className="btn btn-primary" onClick={() => setShowModal(true)}>Add Connection</button>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Type</th>
                  <th>Host</th>
                  <th>Database</th>
                  <th>Status</th>
                  <th>SSL</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(c => (
                  <tr key={c.id}>
                    <td><span className="cell-primary">{c.name}</span></td>
                    <td>
                      <span className={`badge ${c.type === 'postgres' ? 'badge-info' : c.type === 'mysql' || c.type === 'mariadb' ? 'badge-warning' : 'badge-success'}`}>
                        {DATABASE_TYPES.find(d => d.value === c.type)?.label || c.type}
                      </span>
                    </td>
                    <td>{c.host}:{c.port}</td>
                    <td>{c.database}</td>
                    <td><StatusBadge status={c.status} /></td>
                    <td>{c.ssl_enabled ? <Wifi size={14} style={{ color: 'var(--color-success)' }} /> : <WifiOff size={14} style={{ color: 'var(--text-muted)' }} />}</td>
                    <td>
                      <div className="table-actions">
                        <button className="btn btn-secondary btn-icon" onClick={() => handleTest(c.id)} disabled={testing === c.id} title="Test connection">
                          <TestTube size={14} />
                        </button>
                        <button className="btn btn-secondary btn-icon" onClick={() => handleDiscover(c.id)} title="Discover PII">
                          <Search size={14} />
                        </button>
                        <button className="btn btn-danger btn-icon" onClick={() => handleDelete(c.id, c.name)} title="Delete">
                          <Trash2 size={14} />
                        </button>
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showModal && (
        <div className="modal-overlay" onClick={() => setShowModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>New Connection</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>&times;</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Connection Name</label>
                  <input required value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} placeholder="e.g. Production DB" />
                </div>
                <div className="form-group">
                  <label>Database Type</label>
                  <select value={form.type} onChange={e => handleTypeChange(e.target.value as DatabaseType)}>
                    {DATABASE_TYPES.map(dt => (
                      <option key={dt.value} value={dt.value}>{dt.label}</option>
                    ))}
                  </select>
                </div>
                <div className="form-grid form-grid-2">
                  <div className="form-group">
                    <label>Host</label>
                    <input required value={form.host} onChange={e => setForm(p => ({ ...p, host: e.target.value }))} />
                  </div>
                  <div className="form-group">
                    <label>Port</label>
                    <input type="number" required value={form.port} onChange={e => setForm(p => ({ ...p, port: Number(e.target.value) }))} />
                  </div>
                </div>
                <div className="form-group">
                  <label>Database Name</label>
                  <input required value={form.database} onChange={e => setForm(p => ({ ...p, database: e.target.value }))} />
                </div>
                <div className="form-grid form-grid-2">
                  <div className="form-group">
                    <label>Username</label>
                    <input required value={form.username} onChange={e => setForm(p => ({ ...p, username: e.target.value }))} />
                  </div>
                  <div className="form-group">
                    <label>Password</label>
                    <input type="password" required value={form.password} onChange={e => setForm(p => ({ ...p, password: e.target.value }))} />
                  </div>
                </div>
                <div className="form-grid form-grid-2">
                  <div className="form-group">
                    <label>SSL</label>
                    <label className="toggle-label">
                      <input type="checkbox" checked={form.ssl_enabled} onChange={e => setForm(p => ({ ...p, ssl_enabled: e.target.checked }))} />
                      <span>Enable SSL</span>
                    </label>
                  </div>
                  <div className="form-group">
                    <label>Pool Size</label>
                    <input type="number" min={1} max={50} value={form.pool_size} onChange={e => setForm(p => ({ ...p, pool_size: Number(e.target.value) }))} />
                  </div>
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? <><span className="spinner" /> Saving...</> : 'Save Connection'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showDiscoverModal && (
        <div className="modal-overlay" onClick={() => setShowDiscoverModal(false)}>
          <div className="modal modal-lg" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Discover PII</h2>
              <button className="modal-close" onClick={() => setShowDiscoverModal(false)}>&times;</button>
            </div>
            <div className="modal-body">
              {discovering ? (
                <div className="loading-state">
                  <div className="spinner" />
                  <p>Scanning schema for sensitive data...</p>
                </div>
              ) : suggestions.length === 0 ? (
                <div className="empty-state">
                  <p>No PII columns detected in this connection.</p>
                </div>
              ) : (
                <>
                  <p className="modal-description">Found {suggestions.length} columns that may contain sensitive data. Select the ones you want to create masking rules for.</p>
                  <div className="table-wrapper" style={{ maxHeight: 400, overflow: 'auto' }}>
                    <table>
                      <thead>
                        <tr>
                          <th style={{ width: 40 }}></th>
                          <th>Table</th>
                          <th>Column</th>
                          <th>Data Type</th>
                          <th>Suggested Strategy</th>
                          <th>Confidence</th>
                        </tr>
                      </thead>
                      <tbody>
                        {suggestions.map((s, idx) => (
                          <tr key={idx}>
                            <td>
                              <input
                                type="checkbox"
                                checked={selectedSuggestions.includes(idx)}
                                onChange={() => setSelectedSuggestions(prev => prev.includes(idx) ? prev.filter(i => i !== idx) : [...prev, idx])}
                              />
                            </td>
                            <td>{s.target_table}</td>
                            <td><strong>{s.target_column}</strong></td>
                            <td>{s.data_type || 'auto'}</td>
                            <td><span className="badge badge-info">{s.algorithm}</span></td>
                            <td><span className="badge badge-success">high</span></td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </>
              )}
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowDiscoverModal(false)}>Close</button>
              {!discovering && suggestions.length > 0 && (
                <button
                  className="btn btn-primary"
                  onClick={handleCreateSuggestions}
                  disabled={selectedSuggestions.length === 0 || creatingSuggestions}
                >
                  {creatingSuggestions ? <><span className="spinner" /> Creating...</> : `Create ${selectedSuggestions.length} Rules`}
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
