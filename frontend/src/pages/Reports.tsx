import { useEffect, useState } from 'react';
import { FileText, Download, AlertTriangle, Shield } from 'lucide-react';
import { reportsApi } from '../services/api';
import type { ComplianceReport, RiskItem, ComplianceFramework } from '../types';
import { COMPLIANCE_FRAMEWORKS } from '../types';
import Chart from '../components/Chart';
import StatusBadge from '../components/StatusBadge';

export default function Reports() {
  const [report, setReport] = useState<ComplianceReport | null>(null);
  const [risks, setRisks] = useState<RiskItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedFramework, setSelectedFramework] = useState<string>('');
  const [exporting, setExporting] = useState<string | null>(null);

  useEffect(() => {
    const load = async () => {
      setLoading(true);
      try {
        const [comp, risk] = await Promise.all([
          reportsApi.compliance(selectedFramework || undefined),
          reportsApi.riskAssessment(),
        ]);
        setReport(comp);
        setRisks(risk.items || []);
      } catch {
        // silent
      } finally {
        setLoading(false);
      }
    };
    load();
  }, [selectedFramework]);

  const handleExport = async (format: string) => {
    setExporting(format);
    try {
      await reportsApi.exportReport(format as 'pdf' | 'excel' | 'csv' | 'json', 'compliance');
      addToast(`Report exported as ${format.toUpperCase()}`, 'success');
    } catch {
      // silent
    } finally {
      setExporting(null);
    }
  };

  const coverageData = report ? [
    { name: 'Covered', value: report.coverage_percentage },
    { name: 'Uncovered', value: 100 - report.coverage_percentage },
  ] : [];

  const riskDistribution = risks.reduce<Record<string, number>>((acc, r) => {
    acc[r.risk_level] = (acc[r.risk_level] || 0) + 1;
    return acc;
  }, {});

  const riskChartData = Object.entries(riskDistribution).map(([level, count]) => ({
    name: level.charAt(0).toUpperCase() + level.slice(1),
    value: count,
  }));

  function addToast(msg: string, type?: string) {
    console.log(`[${type}] ${msg}`);
  }

  return (
    <div>
      <div className="reports-header">
        <div className="reports-controls">
          <select
            className="filter-select"
            value={selectedFramework}
            onChange={e => setSelectedFramework(e.target.value)}
          >
            <option value="">All Frameworks</option>
            {COMPLIANCE_FRAMEWORKS.map(f => (
              <option key={f.value} value={f.value}>{f.label}</option>
            ))}
          </select>
          <div className="export-buttons">
            {['pdf', 'excel', 'csv', 'json'].map(fmt => (
              <button
                key={fmt}
                className="btn btn-secondary btn-sm"
                onClick={() => handleExport(fmt)}
                disabled={exporting === fmt}
              >
                <Download size={14} />
                {exporting === fmt ? '...' : fmt.toUpperCase()}
              </button>
            ))}
          </div>
        </div>
      </div>

      {loading ? (
        <div className="loading-state"><div className="spinner" /></div>
      ) : (
        <div className="reports-grid">
          <div className="card">
            <div className="card-header">
              <h2>Compliance Coverage</h2>
              <Shield size={18} style={{ color: 'var(--color-accent-2)' }} />
            </div>
            <div className="report-metric">
              <span className="report-metric-value" style={{ color: (report?.coverage_percentage ?? 0) >= 80 ? 'var(--color-success)' : 'var(--color-warning)' }}>
                {report?.coverage_percentage ?? 0}%
              </span>
              <span className="report-metric-label">Coverage</span>
            </div>
            {coverageData.length > 0 && (
              <Chart type="pie" data={coverageData} height={200} colors={['#22d3a5', '#252e45']} />
            )}
          </div>

          <div className="card">
            <div className="card-header">
              <h2>Risk Distribution</h2>
              <AlertTriangle size={18} style={{ color: 'var(--color-warning)' }} />
            </div>
            {riskChartData.length > 0 ? (
              <Chart type="bar" data={riskChartData} height={200} colors={['#f43f5e', '#f59e0b', '#6366f1', '#22d3a5']} />
            ) : (
              <div className="empty-state" style={{ padding: '40px 0' }}>
                <p>No risk data available</p>
              </div>
            )}
          </div>

          <div className="card reports-table-card">
            <div className="card-header">
              <h2>Risk Items</h2>
              <span className="card-count">{risks.length}</span>
            </div>
            {risks.length === 0 ? (
              <div className="empty-state">
                <FileText size={48} />
                <h3>No risk items</h3>
                <p>All columns are properly masked.</p>
              </div>
            ) : (
              <div className="table-wrapper" style={{ maxHeight: 400, overflow: 'auto' }}>
                <table>
                  <thead>
                    <tr>
                      <th>Table</th>
                      <th>Column</th>
                      <th>PII Type</th>
                      <th>Risk Level</th>
                      <th>Status</th>
                      <th>Recommendation</th>
                    </tr>
                  </thead>
                  <tbody>
                    {risks.map((r, i) => (
                      <tr key={i}>
                        <td><code className="code-inline">{r.table}</code></td>
                        <td><strong>{r.column}</strong></td>
                        <td>{r.pii_type}</td>
                        <td><StatusBadge status={r.risk_level} /></td>
                        <td><StatusBadge status={r.status} /></td>
                        <td style={{ fontSize: '13px', color: 'var(--text-secondary)' }}>{r.recommendation}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
