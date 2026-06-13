import { useEffect, useState, useCallback } from 'react';
import { Plus, Clock, Play, Pause, Trash2, History } from 'lucide-react';
import { schedulesApi, connectionsApi, rulesApi } from '../services/api';
import type { Schedule, ScheduleCreate, ScheduleHistory as ScheduleHistoryType, Connection, MaskingRule } from '../types';
import StatusBadge from '../components/StatusBadge';
import { formatDistanceToNow } from 'date-fns';
import type { ToastType } from '../App';

interface Props {
  addToast: (msg: string, type?: ToastType) => void;
}

const FREQUENCIES = [
  { value: 'once', label: 'Once' },
  { value: 'hourly', label: 'Hourly' },
  { value: 'daily', label: 'Daily' },
  { value: 'weekly', label: 'Weekly' },
  { value: 'monthly', label: 'Monthly' },
  { value: 'custom', label: 'Custom (Cron)' },
];

export default function Schedules({ addToast }: Props) {
  const [schedules, setSchedules] = useState<Schedule[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [rules, setRules] = useState<MaskingRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [saving, setSaving] = useState(false);
  const [selectedConn, setSelectedConn] = useState('');
  const [selectedRules, setSelectedRules] = useState<string[]>([]);
  const [name, setName] = useState('');
  const [frequency, setFrequency] = useState<string>('daily');
  const [cronExpression, setCronExpression] = useState('');
  const [showHistory, setShowHistory] = useState(false);
  const [historyData, setHistoryData] = useState<ScheduleHistoryType[]>([]);
  const [historyLoading, setHistoryLoading] = useState(false);
  const [selectedSchedule, setSelectedSchedule] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [s, c, r] = await Promise.all([schedulesApi.list(), connectionsApi.listAll(), rulesApi.listAll()]);
      setSchedules(s);
      setConnections(c);
      setRules(r);
    } catch {
      addToast('Failed to load schedules', 'error');
    } finally {
      setLoading(false);
    }
  }, [addToast]);

  useEffect(() => { load(); }, [load]);

  const filteredRules = rules.filter(r => r.connection_id === selectedConn);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedConn || selectedRules.length === 0) {
      addToast('Select connection and rules', 'error');
      return;
    }
    setSaving(true);
    try {
      await schedulesApi.create({
        name,
        job_config: { connection_id: selectedConn, rule_ids: selectedRules },
        frequency: frequency as ScheduleCreate['frequency'],
        cron_expression: frequency === 'custom' ? cronExpression : undefined,
      });
      addToast('Schedule created', 'success');
      setShowModal(false);
      setName('');
      setSelectedConn('');
      setSelectedRules([]);
      load();
    } catch (err: unknown) {
      addToast((err as Error).message || 'Failed to create schedule', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleToggle = async (id: string, enabled: boolean) => {
    try {
      await schedulesApi.toggle(id, enabled);
      addToast(`Schedule ${enabled ? 'enabled' : 'disabled'}`, 'success');
      load();
    } catch {
      addToast('Failed to toggle schedule', 'error');
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this schedule?')) return;
    try {
      await schedulesApi.delete(id);
      addToast('Schedule deleted', 'success');
      load();
    } catch {
      addToast('Failed to delete schedule', 'error');
    }
  };

  const handleShowHistory = async (id: string) => {
    setSelectedSchedule(id);
    setShowHistory(true);
    setHistoryLoading(true);
    try {
      const data = await schedulesApi.history(id);
      setHistoryData(data);
    } catch {
      addToast('Failed to load history', 'error');
    } finally {
      setHistoryLoading(false);
    }
  };

  const getConnectionName = (id: string) =>
    connections.find(c => c.id === id)?.name ?? id.slice(0, 8) + '...';

  return (
    <div>
      <div className="card">
        <div className="card-header">
          <div className="card-header-left">
            <h2>Job Schedules</h2>
            <span className="card-count">{schedules.length}</span>
          </div>
          <button className="btn btn-primary" onClick={() => setShowModal(true)}>
            <Plus size={16} /> New Schedule
          </button>
        </div>

        {loading ? (
          <div className="loading-state"><div className="spinner" /></div>
        ) : schedules.length === 0 ? (
          <div className="empty-state">
            <Clock size={48} />
            <h3>No schedules yet</h3>
            <p>Create a schedule to automate masking jobs.</p>
            <button className="btn btn-primary" onClick={() => setShowModal(true)}>Create Schedule</button>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Connection</th>
                  <th>Frequency</th>
                  <th>Next Run</th>
                  <th>Last Run</th>
                  <th>Status</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {schedules.map(s => (
                  <tr key={s.id}>
                    <td><span className="cell-primary">{s.name}</span></td>
                    <td>{getConnectionName(s.job_config.connection_id)}</td>
                    <td>
                      <span className="badge badge-info">
                        {FREQUENCIES.find(f => f.value === s.frequency)?.label || s.frequency}
                      </span>
                    </td>
                    <td>{s.next_run ? formatDistanceToNow(new Date(s.next_run), { addSuffix: true }) : '—'}</td>
                    <td>{s.last_run ? formatDistanceToNow(new Date(s.last_run), { addSuffix: true }) : '—'}</td>
                    <td>
                      <span className={`badge ${s.enabled ? 'badge-success' : 'badge-pending'}`}>
                        {s.enabled ? 'Active' : 'Disabled'}
                      </span>
                    </td>
                    <td>
                      <div className="table-actions">
                        <button
                          className={`btn btn-sm ${s.enabled ? 'btn-secondary' : 'btn-success'}`}
                          onClick={() => handleToggle(s.id, !s.enabled)}
                          title={s.enabled ? 'Disable' : 'Enable'}
                        >
                          {s.enabled ? <Pause size={12} /> : <Play size={12} />}
                        </button>
                        <button className="btn btn-secondary btn-sm" onClick={() => handleShowHistory(s.id)} title="History">
                          <History size={12} />
                        </button>
                        <button className="btn btn-danger btn-sm" onClick={() => handleDelete(s.id)} title="Delete">
                          <Trash2 size={12} />
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
              <h2>New Schedule</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>&times;</button>
            </div>
            <form onSubmit={handleCreate}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Schedule Name</label>
                  <input required value={name} onChange={e => setName(e.target.value)} placeholder="e.g. Nightly masking" />
                </div>
                <div className="form-group">
                  <label>Connection</label>
                  <select required value={selectedConn} onChange={e => { setSelectedConn(e.target.value); setSelectedRules([]); }}>
                    <option value="">Select connection...</option>
                    {connections.map(c => <option key={c.id} value={c.id}>{c.name} ({c.type})</option>)}
                  </select>
                </div>
                {selectedConn && (
                  <div className="form-group">
                    <label>Select Rules</label>
                    {filteredRules.length === 0 ? (
                      <p className="form-hint">No rules for this connection.</p>
                    ) : (
                      <div className="checkbox-list">
                        {filteredRules.map(r => (
                          <label key={r.id} className="checkbox-label">
                            <input type="checkbox" checked={selectedRules.includes(r.id)} onChange={() => setSelectedRules(prev => prev.includes(r.id) ? prev.filter(id => id !== r.id) : [...prev, r.id])} />
                            <span>{r.name}</span>
                          </label>
                        ))}
                      </div>
                    )}
                  </div>
                )}
                <div className="form-group">
                  <label>Frequency</label>
                  <select value={frequency} onChange={e => setFrequency(e.target.value)}>
                    {FREQUENCIES.map(f => <option key={f.value} value={f.value}>{f.label}</option>)}
                  </select>
                </div>
                {frequency === 'custom' && (
                  <div className="form-group">
                    <label>Cron Expression</label>
                    <input value={cronExpression} onChange={e => setCronExpression(e.target.value)} placeholder="0 2 * * *" />
                    <span className="form-hint">e.g. "0 2 * * *" for daily at 2 AM</span>
                  </div>
                )}
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? <><span className="spinner" /> Creating...</> : 'Create Schedule'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showHistory && (
        <div className="modal-overlay" onClick={() => setShowHistory(false)}>
          <div className="modal modal-lg" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Schedule History</h2>
              <button className="modal-close" onClick={() => setShowHistory(false)}>&times;</button>
            </div>
            <div className="modal-body">
              {historyLoading ? (
                <div className="loading-state"><div className="spinner" /></div>
              ) : historyData.length === 0 ? (
                <div className="empty-state"><p>No execution history yet.</p></div>
              ) : (
                <div className="table-wrapper">
                  <table>
                    <thead>
                      <tr><th>Started</th><th>Completed</th><th>Status</th><th>Error</th></tr>
                    </thead>
                    <tbody>
                      {historyData.map(h => (
                        <tr key={h.id}>
                          <td>{formatDistanceToNow(new Date(h.started_at), { addSuffix: true })}</td>
                          <td>{h.completed_at ? formatDistanceToNow(new Date(h.completed_at), { addSuffix: true }) : '—'}</td>
                          <td><StatusBadge status={h.status} /></td>
                          <td style={{ color: 'var(--color-danger)', fontSize: '13px' }}>{h.error_message || '—'}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowHistory(false)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
