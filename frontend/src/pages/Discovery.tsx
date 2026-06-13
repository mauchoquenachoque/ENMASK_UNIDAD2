import { useEffect, useState, useCallback } from 'react';
import { Search, Radar, Plus, Shield } from 'lucide-react';
import { discoveryApi, connectionsApi, rulesApi } from '../services/api';
import type { DiscoveryScan, DiscoveryResult, Connection, MaskingRule } from '../types';
import { MASKING_ALGORITHMS, COMPLIANCE_FRAMEWORKS } from '../types';
import StatusBadge from '../components/StatusBadge';
import type { ToastType } from '../App';

interface Props {
  addToast: (msg: string, type?: ToastType) => void;
}

export default function Discovery({ addToast }: Props) {
  const [connections, setConnections] = useState<Connection[]>([]);
  const [scans, setScans] = useState<DiscoveryScan[]>([]);
  const [results, setResults] = useState<DiscoveryResult[]>([]);
  const [selectedConn, setSelectedConn] = useState('');
  const [activeScan, setActiveScan] = useState<DiscoveryScan | null>(null);
  const [loading, setLoading] = useState(true);
  const [scanning, setScanning] = useState(false);
  const [selectedResults, setSelectedResults] = useState<string[]>([]);
  const [creatingRules, setCreatingRules] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const c = await connectionsApi.listAll();
      setConnections(c);
      const s = await discoveryApi.listScans();
      setScans(s);
    } catch {
      addToast('Failed to load data', 'error');
    } finally {
      setLoading(false);
    }
  }, [addToast]);

  useEffect(() => { load(); }, [load]);

  const pollScan = async (scanId: string) => {
    const poll = async () => {
      try {
        const scan = await discoveryApi.getScan(scanId);
        setActiveScan(scan);
        if (scan.status === 'scanning' || scan.status === 'pending') {
          setTimeout(poll, 2000);
        } else {
          setScanning(false);
          if (scan.status === 'completed') {
            const res = await discoveryApi.getResults(scanId);
            setResults(res);
            addToast(`Scan complete: ${scan.pii_found} PII columns found`, 'success');
          } else {
            addToast('Scan failed', 'error');
          }
          load();
        }
      } catch {
        setScanning(false);
      }
    };
    setTimeout(poll, 1500);
  };

  const handleStartScan = async () => {
    if (!selectedConn) { addToast('Select a connection', 'error'); return; }
    setScanning(true);
    setResults([]);
    setActiveScan(null);
    try {
      const scan = await discoveryApi.startScan({ connection_id: selectedConn });
      setActiveScan(scan);
      pollScan(scan.id);
    } catch (err: unknown) {
      addToast((err as Error).message || 'Failed to start scan', 'error');
      setScanning(false);
    }
  };

  const handleCreateRules = async () => {
    if (selectedResults.length === 0) return;
    setCreatingRules(true);
    try {
      const rules = await discoveryApi.createRulesFromResults(selectedResults);
      addToast(`${rules.length} rules created from discovery results`, 'success');
      setSelectedResults([]);
      load();
    } catch (err: unknown) {
      addToast((err as Error).message || 'Failed to create rules', 'error');
    } finally {
      setCreatingRules(false);
    }
  };

  const toggleResult = (id: string) => {
    setSelectedResults(prev => prev.includes(id) ? prev.filter(r => r !== id) : [...prev, id]);
  };

  const confidenceColor = (c: string) => {
    if (c === 'high') return 'badge-danger';
    if (c === 'medium') return 'badge-warning';
    return 'badge-success';
  };

  return (
    <div>
      <div className="card" style={{ marginBottom: '24px' }}>
        <div className="card-header">
          <h2>Data Discovery</h2>
        </div>
        <div className="discovery-controls">
          <div className="form-group">
            <label>Connection</label>
            <select value={selectedConn} onChange={e => setSelectedConn(e.target.value)}>
              <option value="">Select a connection to scan...</option>
              {connections.map(c => (
                <option key={c.id} value={c.id}>{c.name} ({c.type})</option>
              ))}
            </select>
          </div>
          <button className="btn btn-primary" onClick={handleStartScan} disabled={scanning || !selectedConn}>
            {scanning ? <><span className="spinner" /> Scanning...</> : <><Radar size={16} /> Start Scan</>}
          </button>
        </div>
        {activeScan && scanning && (
          <div className="scan-progress">
            <div className="progress-bar">
              <div className="progress-fill" style={{ width: `${activeScan.progress}%` }} />
            </div>
            <span className="progress-text">{activeScan.progress}% &middot; {activeScan.columns_scanned} columns scanned</span>
          </div>
        )}
      </div>

      <div className="card">
        <div className="card-header">
          <div className="card-header-left">
            <h2>Scan Results</h2>
            <span className="card-count">{results.length}</span>
          </div>
          <div className="card-header-right">
            {selectedResults.length > 0 && (
              <button className="btn btn-primary btn-sm" onClick={handleCreateRules} disabled={creatingRules}>
                {creatingRules ? <><span className="spinner" /> Creating...</> : <><Plus size={14} /> Create {selectedResults.length} Rules</>}
              </button>
            )}
          </div>
        </div>

        {loading ? (
          <div className="loading-state"><div className="spinner" /></div>
        ) : results.length === 0 ? (
          <div className="empty-state">
            <Search size={48} />
            <h3>No discovery results</h3>
            <p>Select a connection and start a scan to identify sensitive data.</p>
          </div>
        ) : (
          <div className="table-wrapper">
            <table>
              <thead>
                <tr>
                  <th style={{ width: 40 }}>
                    <input
                      type="checkbox"
                      checked={selectedResults.length === results.length && results.length > 0}
                      onChange={() => setSelectedResults(selectedResults.length === results.length ? [] : results.map(r => r.id))}
                    />
                  </th>
                  <th>Table</th>
                  <th>Column</th>
                  <th>PII Type</th>
                  <th>Confidence</th>
                  <th>Suggested Algorithm</th>
                  <th>Compliance</th>
                  <th>Rule Created</th>
                </tr>
              </thead>
              <tbody>
                {results.map(r => (
                  <tr key={r.id}>
                    <td>
                      <input
                        type="checkbox"
                        checked={selectedResults.includes(r.id)}
                        onChange={() => toggleResult(r.id)}
                        disabled={r.rule_created}
                      />
                    </td>
                    <td><code className="code-inline">{r.table_name}</code></td>
                    <td><strong>{r.column_name}</strong></td>
                    <td><span className="badge badge-info">{r.pii_type}</span></td>
                    <td><StatusBadge status={r.confidence} /></td>
                    <td>{MASKING_ALGORITHMS.find(a => a.value === r.suggested_algorithm)?.label || r.suggested_algorithm}</td>
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
                      {r.rule_created ? (
                        <span className="badge badge-success">Yes</span>
                      ) : (
                        <span className="badge badge-pending">No</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}
