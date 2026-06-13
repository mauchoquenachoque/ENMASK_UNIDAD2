import { useEffect, useState, useCallback } from 'react';
import { Plus, Search, Pencil, Trash2, Shield } from 'lucide-react';
import { rulesApi, connectionsApi } from '../services/api';
import type { MaskingRule, RuleCreate, Connection, MaskingAlgorithm, DataType, ComplianceFramework } from '../types';
import { MASKING_ALGORITHMS, DATA_TYPES, COMPLIANCE_FRAMEWORKS } from '../types';
import StatusBadge from '../components/StatusBadge';
import type { ToastType } from '../App';

interface Props {
  addToast: (msg: string, type?: ToastType) => void;
}

const defaultForm: RuleCreate = {
  name: '', description: '', connection_id: '', target_table: '',
  target_column: '', data_type: 'custom', algorithm: 'hashing',
  algorithm_options: {}, compliance_frameworks: [], priority: 0,
};

export default function Rules({ addToast }: Props) {
  const [rules, setRules] = useState<MaskingRule[]>([]);
  const [connections, setConnections] = useState<Connection[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState<RuleCreate>(defaultForm);
  const [saving, setSaving] = useState(false);
  const [editingId, setEditingId] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [filterAlgorithm, setFilterAlgorithm] = useState<string>('');
  const [selectedRules, setSelectedRules] = useState<string[]>([]);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const [r, c] = await Promise.all([rulesApi.listAll(), connectionsApi.listAll()]);
      setRules(r);
      setConnections(c);
    } catch {
      addToast('Failed to load data', 'error');
    } finally {
      setLoading(false);
    }
  }, [addToast]);

  useEffect(() => { load(); }, [load]);

  const getConnectionName = (id: string) =>
    connections.find(c => c.id === id)?.name ?? id.slice(0, 8) + '...';

  const openNewModal = () => {
    setEditingId(null);
    setForm(defaultForm);
    setShowModal(true);
  };

  const openEditModal = (rule: MaskingRule) => {
    setEditingId(rule.id);
    setForm({
      name: rule.name,
      description: rule.description,
      connection_id: rule.connection_id,
      target_table: rule.target_table,
      target_column: rule.target_column,
      data_type: rule.data_type,
      algorithm: rule.algorithm,
      algorithm_options: rule.algorithm_options || {},
      compliance_frameworks: rule.compliance_frameworks || [],
      priority: rule.priority,
    });
    setShowModal(true);
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setSaving(true);
    try {
      if (editingId) {
        await rulesApi.update(editingId, form);
        addToast('Rule updated', 'success');
      } else {
        await rulesApi.create(form);
        addToast('Rule created', 'success');
      }
      setShowModal(false);
      setForm(defaultForm);
      setEditingId(null);
      load();
    } catch (err: unknown) {
      addToast((err as Error).message || 'Failed to save rule', 'error');
    } finally {
      setSaving(false);
    }
  };

  const handleDelete = async (id: string) => {
    if (!confirm('Delete this rule?')) return;
    try {
      await rulesApi.delete(id);
      addToast('Rule deleted', 'success');
      load();
    } catch {
      addToast('Failed to delete rule', 'error');
    }
  };

  const handleBulkDelete = async () => {
    if (!confirm(`Delete ${selectedRules.length} rules?`)) return;
    try {
      await rulesApi.bulkDelete(selectedRules);
      addToast(`${selectedRules.length} rules deleted`, 'success');
      setSelectedRules([]);
      load();
    } catch {
      addToast('Failed to delete rules', 'error');
    }
  };

  const filtered = rules.filter(r => {
    const matchSearch = !search ||
      r.name.toLowerCase().includes(search.toLowerCase()) ||
      r.target_table.toLowerCase().includes(search.toLowerCase()) ||
      r.target_column.toLowerCase().includes(search.toLowerCase());
    const matchAlgorithm = !filterAlgorithm || r.algorithm === filterAlgorithm;
    return matchSearch && matchAlgorithm;
  });

  return (
    <div>
      <div className="card">
        <div className="card-header">
          <div className="card-header-left">
            <h2>Masking Rules</h2>
            <span className="card-count">{rules.length}</span>
          </div>
          <div className="card-header-right">
            {selectedRules.length > 0 && (
              <button className="btn btn-danger btn-sm" onClick={handleBulkDelete}>
                <Trash2 size={14} /> Delete {selectedRules.length}
              </button>
            )}
            <div className="search-input">
              <Search size={16} />
              <input type="text" placeholder="Search rules..." value={search} onChange={e => setSearch(e.target.value)} />
            </div>
            <select className="filter-select" value={filterAlgorithm} onChange={e => setFilterAlgorithm(e.target.value)}>
              <option value="">All Algorithms</option>
              {MASKING_ALGORITHMS.map(a => (
                <option key={a.value} value={a.value}>{a.label}</option>
              ))}
            </select>
            <button className="btn btn-primary" onClick={openNewModal}>
              <Plus size={16} /> New Rule
            </button>
          </div>
        </div>

        {loading ? (
          <div className="loading-state"><div className="spinner" /></div>
        ) : filtered.length === 0 ? (
          <div className="empty-state">
            <Shield size={48} />
            <h3>No masking rules yet</h3>
            <p>Create a rule to define how a specific column should be masked.</p>
            <button className="btn btn-primary" onClick={openNewModal}>Create Rule</button>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th style={{ width: 40 }}>
                    <input
                      type="checkbox"
                      checked={selectedRules.length === filtered.length && filtered.length > 0}
                      onChange={() => setSelectedRules(selectedRules.length === filtered.length ? [] : filtered.map(r => r.id))}
                    />
                  </th>
                  <th>Name</th>
                  <th>Connection</th>
                  <th>Table</th>
                  <th>Column</th>
                  <th>Algorithm</th>
                  <th>Compliance</th>
                  <th></th>
                </tr>
              </thead>
              <tbody>
                {filtered.map(r => (
                  <tr key={r.id}>
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedRules.includes(r.id)}
                        onChange={() => setSelectedRules(prev => prev.includes(r.id) ? prev.filter(id => id !== r.id) : [...prev, r.id])}
                      />
                    </td>
                    <td><span className="cell-primary">{r.name}</span></td>
                    <td>{getConnectionName(r.connection_id)}</td>
                    <td><code className="code-inline">{r.target_table}</code></td>
                    <td><code className="code-inline success">{r.target_column}</code></td>
                    <td>
                      <span className="badge badge-info">
                        {MASKING_ALGORITHMS.find(a => a.value === r.algorithm)?.label || r.algorithm}
                      </span>
                    </td>
                    <td>
                      <div className="badge-group">
                        {r.compliance_frameworks?.map(f => (
                          <span key={f} className="badge badge-pending" style={{ fontSize: '10px' }}>
                            {COMPLIANCE_FRAMEWORKS.find(cf => cf.value === f)?.label || f}
                          </span>
                        ))}
                      </div>
                    </td>
                    <td>
                      <div className="table-actions">
                        <button className="btn btn-secondary btn-icon" onClick={() => openEditModal(r)} title="Edit">
                          <Pencil size={14} />
                        </button>
                        <button className="btn btn-danger btn-icon" onClick={() => handleDelete(r.id)} title="Delete">
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
          <div className="modal modal-lg" onClick={e => e.stopPropagation()}>
            <div className="modal-header">
              <h2>{editingId ? 'Edit Masking Rule' : 'New Masking Rule'}</h2>
              <button className="modal-close" onClick={() => setShowModal(false)}>&times;</button>
            </div>
            <form onSubmit={handleSubmit}>
              <div className="form-grid">
                <div className="form-group">
                  <label>Rule Name</label>
                  <input required value={form.name} onChange={e => setForm(p => ({ ...p, name: e.target.value }))} placeholder="e.g. Mask email column" />
                </div>
                <div className="form-group">
                  <label>Description</label>
                  <input value={form.description || ''} onChange={e => setForm(p => ({ ...p, description: e.target.value }))} placeholder="Optional description" />
                </div>
                <div className="form-group">
                  <label>Connection</label>
                  <select required value={form.connection_id} onChange={e => setForm(p => ({ ...p, connection_id: e.target.value }))}>
                    <option value="">Select a connection...</option>
                    {connections.map(c => (
                      <option key={c.id} value={c.id}>{c.name} ({c.type})</option>
                    ))}
                  </select>
                </div>
                <div className="form-grid form-grid-2">
                  <div className="form-group">
                    <label>Table / Collection</label>
                    <input required value={form.target_table} onChange={e => setForm(p => ({ ...p, target_table: e.target.value }))} placeholder="users" />
                  </div>
                  <div className="form-group">
                    <label>Column / Field</label>
                    <input required value={form.target_column} onChange={e => setForm(p => ({ ...p, target_column: e.target.value }))} placeholder="email" />
                  </div>
                </div>
                <div className="form-grid form-grid-2">
                  <div className="form-group">
                    <label>Data Type</label>
                    <select value={form.data_type || 'custom'} onChange={e => setForm(p => ({ ...p, data_type: e.target.value as DataType }))}>
                      {DATA_TYPES.map(dt => (
                        <option key={dt.value} value={dt.value}>{dt.label}</option>
                      ))}
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Masking Algorithm</label>
                    <select value={form.algorithm} onChange={e => setForm(p => ({ ...p, algorithm: e.target.value as MaskingAlgorithm }))}>
                      {MASKING_ALGORITHMS.map(a => (
                        <option key={a.value} value={a.value}>{a.label}</option>
                      ))}
                    </select>
                  </div>
                </div>
                <div className="form-group">
                  <label>Compliance Frameworks</label>
                  <div className="checkbox-grid">
                    {COMPLIANCE_FRAMEWORKS.map(f => (
                      <label key={f.value} className="checkbox-label">
                        <input
                          type="checkbox"
                          checked={(form.compliance_frameworks || []).includes(f.value)}
                          onChange={e => {
                            const current = form.compliance_frameworks || [];
                            setForm(p => ({
                              ...p,
                              compliance_frameworks: e.target.checked
                                ? [...current, f.value]
                                : current.filter(v => v !== f.value),
                            }));
                          }}
                        />
                        <span>{f.label}</span>
                      </label>
                    ))}
                  </div>
                </div>
                {form.algorithm === 'substitution' && (
                  <div className="form-group">
                    <label>Faker Provider</label>
                    <input placeholder="e.g. name, email, phone_number" onChange={e => setForm(p => ({ ...p, algorithm_options: { ...p.algorithm_options, provider: e.target.value } }))} />
                  </div>
                )}
                {form.algorithm === 'hashing' && (
                  <div className="form-group">
                    <label>Salt (optional)</label>
                    <input placeholder="Optional salt for determinism" onChange={e => setForm(p => ({ ...p, algorithm_options: { ...p.algorithm_options, salt: e.target.value } }))} />
                  </div>
                )}
                {form.algorithm === 'perturbation' && (
                  <div className="form-grid form-grid-2">
                    <div className="form-group">
                      <label>Variance Type</label>
                      <select onChange={e => setForm(p => ({ ...p, algorithm_options: { ...p.algorithm_options, variance_type: e.target.value } }))}>
                        <option value="percentage">Percentage</option>
                        <option value="days">Days</option>
                      </select>
                    </div>
                    <div className="form-group">
                      <label>Variance Value (+/-)</label>
                      <input type="number" defaultValue={10} onChange={e => setForm(p => ({ ...p, algorithm_options: { ...p.algorithm_options, variance_value: parseFloat(e.target.value) } }))} />
                    </div>
                  </div>
                )}
              </div>
              <div className="modal-footer">
                <button type="button" className="btn btn-secondary" onClick={() => setShowModal(false)}>Cancel</button>
                <button type="submit" className="btn btn-primary" disabled={saving}>
                  {saving ? <><span className="spinner" /> Saving...</> : 'Save Rule'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
