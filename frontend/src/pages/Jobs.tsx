import { useEffect, useState, useCallback } from 'react';
import { Play, StopCircle, RotateCcw, Eye, Share2, FileText, Plus, Search } from 'lucide-react';
import { jobsApi, connectionsApi, rulesApi } from '../services/api';
import type { MaskingJob, JobCreate, Connection, MaskingRule, JobStatus, AuditLogEntry } from '../types';
import StatusBadge from '../components/StatusBadge';
import { useAuth } from '../hooks/useAuth';
import { formatDistanceToNow } from 'date-fns';
import type { ToastType } from '../App';

interface Props {
  addToast: (msg: string, type?: ToastType) => void;
}

export default function Jobs({ addToast }: Props) {
  const { user } = useAuth();
  const [jobs, setJobs] = useState<MaskingJob[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [rules, setRules] = useState<MaskingRule[]>([]);
  const [loading, setLoading] = useState(true);
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [selectedConn, setSelectedConn] = useState('');
  const [selectedRules, setSelectedRules] = useState<string[]>([]);
  const [jobName, setJobName] = useState('');
  const [saving, setSaving] = useState(false);
  const [running, setRunning] = useState<Set<string>>(new Set());
  const [filterStatus, setFilterStatus] = useState<string>('');
  const [search, setSearch] = useState('');

  const [showPreviewModal, setShowPreviewModal] = useState(false);
  const [previewData, setPreviewData] = useState<Record<string, unknown>[]>([]);
  const [previewIsMasked, setPreviewIsMasked] = useState(false);
  const [previewingJob, setPreviewingJob] = useState<string | null>(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewMaskPref, setPreviewMaskPref] = useState(true);

  const [showShareModal, setShowShareModal] = useState(false);
  const [shareEmail, setShareEmail] = useState('');
  const [sharingJob, setSharingJob] = useState<MaskingJob | null>(null);
  const [sharing, setSharing] = useState(false);

  const [showAuditModal, setShowAuditModal] = useState(false);
  const [auditLogs, setAuditLogs] = useState<AuditLogEntry[]>([]);
  const [auditLoading, setAuditLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [j, c, r] = await Promise.all([jobsApi.listAll(), connectionsApi.listAll(), rulesApi.listAll()]);
      setJobs(j);
      setConnections(c);
      setRules(r);
    } catch {
      addToast('Failed to load data', 'error');
    } finally {
      setLoading(false);
    }
  }, [addToast]);

  useEffect(() => { load(); }, [load]);

  const getConnectionName = (id: string) =>
    connections.find(c => c.id === id)?.name ?? id.slice(0, 8) + '...';

  const filteredRules = rules.filter(r => r.connection_id === selectedConn);

  const toggleRule = (id: string) =>
    setSelectedRules(prev => prev.includes(id) ? prev.filter(r => r !== id) : [...prev, id]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!selectedConn) { addToast('Select a connection', 'error'); return; }
    if (selectedRules.length < 1) { addToast('Select at least one rule', 'error'); return; }
    setSaving(true);
    try {
      await jobsApi.create({ name: jobName || undefined, connection_id: selectedConn, rule_ids: selectedRules });
      addToast('Job created', 'success');
      setShowCreateModal(false);
      setSelectedConn('');
      setSelectedRules([]);
      setJobName('');
      load();
    } catch (err: unknown) {
      addToast((err as Error).message || 'Failed to create job', 'error');
    } finally {
      setSaving(false);
    }
  };

  const pollJob = async (jobId: string) => {
    const poll = async () => {
      try {
        const updated = await jobsApi.get(jobId);
        setJobs(prev => prev.map(j => j.id === jobId ? updated : j));
        if (updated.status === 'running' || updated.status === 'pending') {
          setTimeout(poll, 2000);
        } else {
          setRunning(prev => { const s = new Set(prev); s.delete(jobId); return s; });
          if (updated.status === 'completed') addToast(`Job completed - ${updated.records_processed} records processed`, 'success');
          else if (updated.status === 'failed') addToast(`Job failed: ${updated.error_message}`, 'error');
        }
      } catch {
        setRunning(prev => { const s = new Set(prev); s.delete(jobId); return s; });
      }
    };
    setTimeout(poll, 1500);
  };

  const handleRun = async (job: MaskingJob) => {
    setRunning(prev => new Set(prev).add(job.id));
    try {
      await jobsApi.run(job.id);
      addToast('Job started', 'info');
      pollJob(job.id);
    } catch (err: unknown) {
      addToast((err as Error).message || 'Failed to run job', 'error');
      setRunning(prev => { const s = new Set(prev); s.delete(job.id); return s; });
    }
  };

  const handleCancel = async (job: MaskingJob) => {
    try {
      await jobsApi.cancel(job.id);
      addToast('Job cancelled', 'info');
      load();
    } catch (err: unknown) {
      addToast((err as Error).message || 'Failed to cancel job', 'error');
    }
  };

  const handleUnmask = async (job: MaskingJob) => {
    setRunning(prev => new Set(prev).add(job.id));
    try {
      await jobsApi.unmask(job.id);
      addToast('Unmasking started', 'info');
      pollJob(job.id);
    } catch (err: unknown) {
      addToast((err as Error).message || 'Failed to unmask', 'error');
      setRunning(prev => { const s = new Set(prev); s.delete(job.id); return s; });
    }
  };

  const handlePreview = async (jobId: string) => {
    setPreviewingJob(jobId);
    setShowPreviewModal(true);
    setPreviewLoading(true);
    setPreviewData([]);
    setPreviewMaskPref(true);
    try {
      const resp = await jobsApi.query(jobId, true);
      setPreviewData(resp.data || []);
      setPreviewIsMasked(resp.is_masked);
    } catch (err: unknown) {
      addToast((err as Error).message || 'Failed to query data', 'error');
      setShowPreviewModal(false);
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleToggleMasking = async () => {
    if (!previewingJob) return;
    setPreviewLoading(true);
    try {
      const newPref = !previewMaskPref;
      const resp = await jobsApi.query(previewingJob, newPref);
      setPreviewData(resp.data || []);
      setPreviewIsMasked(resp.is_masked);
      setPreviewMaskPref(newPref);
    } catch (err: unknown) {
      addToast((err as Error).message || 'Failed to toggle masking', 'error');
    } finally {
      setPreviewLoading(false);
    }
  };

  const handleShare = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!sharingJob || !shareEmail) return;
    setSharing(true);
    try {
      await jobsApi.share(sharingJob.id, { email: shareEmail, permission: 'read' });
      addToast(`Job shared with ${shareEmail}`, 'success');
      setShareEmail('');
      setShowShareModal(false);
      load();
    } catch (err: unknown) {
      addToast((err as Error).message || 'Failed to share job', 'error');
    } finally {
      setSharing(false);
    }
  };

  const handleShowAudit = async (jobId: string) => {
    setShowAuditModal(true);
    setAuditLoading(true);
    setAuditLogs([]);
    try {
      const logs = await jobsApi.audit(jobId);
      setAuditLogs(logs);
    } catch (err: unknown) {
      addToast((err as Error).message || 'Failed to load audit logs', 'error');
      setShowAuditModal(false);
    } finally {
      setAuditLoading(false);
    }
  };

  const filtered = jobs.filter(j => {
    const matchStatus = !filterStatus || j.status === filterStatus;
    const matchSearch = !search || getConnectionName(j.connection_id).toLowerCase().includes(search.toLowerCase());
    return matchStatus && matchSearch;
  });

  return (
    <div>
      <div className="card">
        <div className="card-header">
          <div className="card-header-left">
            <h2>Masking Jobs</h2>
            <span className="card-count">{jobs.length}</span>
          </div>
          <div className="card-header-right">
            <div className="search-input">
              <Search size={16} />
              <input type="text" placeholder="Search jobs..." value={search} onChange={e => setSearch(e.target.value)} />
            </div>
            <select className="filter-select" value={filterStatus} onChange={e => setFilterStatus(e.target.value)}>
              <option value="">All Statuses</option>
              <option value="pending">Pending</option>
              <option value="running">Running</option>
              <option value="completed">Completed</option>
              <option value="failed">Failed</option>
              <option value="unmasked">Unmasked</option>
            </select>
            <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>
              <Plus size={16} /> New Job
            </button>
          </div>
        </div>

        {loading ? (
          <div className="loading-state"><div className="spinner" /></div>
        ) : filtered.length === 0 ? (
          <div className="empty-state">
            <Play size={48} />
            <h3>No jobs yet</h3>
            <p>Create a job to apply masking rules to a database.</p>
            <button className="btn btn-primary" onClick={() => setShowCreateModal(true)}>Create Job</button>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th>Name</th>
                  <th>Connection</th>
                  <th>Rules</th>
                  <th>Status</th>
                  <th>Progress</th>
                  <th>Records</th>
                  <th>Started</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(j => (
                  <tr key={j.id}>
                    <td><span className="cell-primary">{j.name || `Job ${j.id.slice(0, 8)}`}</span></td>
                    <td>{getConnectionName(j.connection_id)}</td>
                    <td>{j.rule_ids.length} rule{j.rule_ids.length !== 1 ? 's' : ''}</td>
                    <td><StatusBadge status={j.status} /></td>
                    <td>
                      {j.status === 'running' ? (
                        <div className="progress-bar">
                          <div className="progress-fill" style={{ width: `${j.progress}%` }} />
                          <span className="progress-text">{j.progress}%</span>
                        </div>
                      ) : (
                        <span style={{ color: 'var(--text-muted)', fontSize: '13px' }}>
                          {j.status === 'completed' ? '100%' : '—'}
                        </span>
                      )}
                    </td>
                    <td>{j.records_processed.toLocaleString()}</td>
                    <td style={{ fontSize: 12 }}>
                      {j.started_at ? formatDistanceToNow(new Date(j.started_at), { addSuffix: true }) : '—'}
                    </td>
                    <td>
                      <div className="table-actions">
                        {j.status !== 'running' && j.status !== 'completed' && (
                          <button className="btn btn-primary btn-sm" onClick={() => handleRun(j)} disabled={running.has(j.id)} title="Run">
                            <Play size={12} />
                          </button>
                        )}
                        {j.status === 'running' && (
                          <button className="btn btn-danger btn-sm" onClick={() => handleCancel(j)} title="Cancel">
                            <StopCircle size={12} />
                          </button>
                        )}
                        {j.status === 'completed' && (
                          <button className="btn btn-secondary btn-sm" onClick={() => handleUnmask(j)} disabled={running.has(j.id)} title="Unmask">
                            <RotateCcw size={12} />
                          </button>
                        )}
                        <button className="btn btn-secondary btn-sm" onClick={() => handlePreview(j.id)} title="Preview (DDM)">
                          <Eye size={12} />
                        </button>
                        {user?.id === j.owner_id && (
                          <>
                            <button className="btn btn-secondary btn-sm" onClick={() => { setSharingJob(j); setShowShareModal(true); }} title="Share">
                              <Share2 size={12} />
                            </button>
                            <button className="btn btn-secondary btn-sm" onClick={() => handleShowAudit(j.id)} title="Audit Log">
                              <FileText size={12} />
                            </button>
                          </>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {showCreateModal && (
        <div className="modal-overlay" onClick={() => setShowCreateModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Create Masking Job</h2>
              <button className="modal-close" onClick={() => setShowCreateModal(false)}>&times;</button>
            </div>
            <form onSubmit={handleCreate}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Job Name (optional)</label>
                  <input value={jobName} onChange={e => setJobName(e.target.value)} placeholder="e.g. Nightly masking run" />
                </div>
                <div className="form-group">
                  <label>Connection</label>
                  <select value={selectedConn} onChange={e => { setSelectedConn(e.target.value); setSelectedRules([]); }}>
                    <option value="">Select a connection...</option>
                    {connections.map(c => (
                      <option key={c.id} value={c.id}>{c.name} ({c.type})</option>
                    ))}
                  </select>
                </div>
                {selectedConn && (
                  <div className="form-group">
                    <label>Select Rules</label>
                    {filteredRules.length === 0 ? (
                      <p className="form-hint">No rules for this connection. Create rules first.</p>
                    ) : (
                      <div className="checkbox-list">
                        {filteredRules.map(r => (
                          <label key={r.id} className="checkbox-label">
                            <input type="checkbox" checked={selectedRules.includes(r.id)} onChange={() => toggleRule(r.id)} />
                            <span><strong>{r.name}</strong> &middot; {r.target_table}.{r.target_column}</span>
                          </label>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowCreateModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? <><span className="spinner" /> Creating...</> : 'Create Job'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showPreviewModal && previewingJob && (
        <div className="modal-overlay" onClick={() => setShowPreviewModal(false)}>
          <div className="modal modal-xl" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Dynamic Data Masking Preview</h2>
              <button className="modal-close" onClick={() => setShowPreviewModal(false)}>&times;</button>
            </div>
            <div className="modal-body">
              <div className="preview-status">
                <StatusBadge status={previewIsMasked ? 'masked' : 'unmasked_risk'} size="md" />
              </div>
              {previewLoading ? (
                <div className="loading-state"><div className="spinner" /></div>
              ) : previewData.length === 0 ? (
                <div className="empty-state"><p>No records found.</p></div>
              ) : (
                <div className="table-wrapper" style={{ maxHeight: 400, overflow: 'auto' }}>
                  <table>
                    <thead>
                      <tr>{Object.keys(previewData[0]).map(k => <th key={k}>{k}</th>)}</tr>
                    </thead>
                    <tbody>
                      {previewData.map((row, i) => (
                        <tr key={i}>{Object.values(row).map((v, j) => <td key={j}>{String(v)}</td>)}</tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={handleToggleMasking} disabled={previewLoading || previewData.length === 0}>
                {previewMaskPref ? 'Show Unmasked' : 'Show Masked'}
              </button>
              <button className="btn btn-secondary" onClick={() => setShowPreviewModal(false)}>Close</button>
            </div>
          </div>
        </div>
      )}

      {showShareModal && sharingJob && (
        <div className="modal-overlay" onClick={() => setShowShareModal(false)}>
          <div className="modal" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Share Job</h2>
              <button className="modal-close" onClick={() => setShowShareModal(false)}>&times;</button>
            </div>
            <form onSubmit={handleShare}>
              <div className="modal-body">
                <p className="modal-description">Users you share with will only see <strong>masked data</strong>.</p>
                <div className="form-group">
                  <label>User Email</label>
                  <input type="email" required value={shareEmail} onChange={e => setShareEmail(e.target.value)} placeholder="user@example.com" />
                </div>
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowShareModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={sharing}>
                  {sharing ? <><span className="spinner" /> Sharing...</> : 'Share'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showAuditModal && (
        <div className="modal-overlay" onClick={() => setShowAuditModal(false)}>
          <div className="modal modal-xl" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>Audit Log</h2>
              <button className="modal-close" onClick={() => setShowAuditModal(false)}>&times;</button>
            </div>
            <div className="modal-body">
              {auditLoading ? (
                <div className="loading-state"><div className="spinner" /></div>
              ) : auditLogs.length === 0 ? (
                <div className="empty-state"><p>No audit entries yet.</p></div>
              ) : (
                <div className="table-wrapper" style={{ maxHeight: 400, overflow: 'auto' }}>
                  <table>
                    <thead>
                      <tr><th>Time</th><th>User</th><th>Action</th><th>Masked?</th></tr>
                    </thead>
                    <tbody>
                      {auditLogs.map(log => (
                        <tr key={log.id}>
                          <td>{formatDistanceToNow(new Date(log.timestamp), { addSuffix: true })}</td>
                          <td>{log.user_email}</td>
                          <td>{log.action}</td>
                          <td><StatusBadge status={log.is_masked ? 'masked' : 'unmasked_risk'} /></td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
            <div className="modal-footer">
              <button className="btn btn-secondary" onClick={() => setShowAuditModal(false)}>Close</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
