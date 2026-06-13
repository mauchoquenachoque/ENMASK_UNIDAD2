import { useEffect, useState } from 'react';
import { Database, Shield, Play, FileDigit, AlertTriangle, Activity } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import Chart from '../components/Chart';
import StatusBadge from '../components/StatusBadge';
import { reportsApi } from '../services/api';
import type { Summary, ActivityEntry, DatabaseType, ComplianceFramework } from '../types';
import { COMPLIANCE_FRAMEWORKS } from '../types';
import { formatDistanceToNow } from 'date-fns';

const RISK_COLORS = ['#22d3a5', '#f59e0b', '#f43f5e'];

export default function Dashboard() {
  const [summary, setSummary] = useState<Summary | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const load = async () => {
      try {
        const data = await reportsApi.summary();
        setSummary(data);
      } catch {
        setSummary({
          total_connections: 0,
          total_rules: 0,
          total_jobs: 0,
          total_records_processed: 0,
          active_jobs: 0,
          failed_jobs: 0,
          risk_score: 0,
          compliance_coverage: {} as Record<ComplianceFramework, number>,
          database_distribution: {} as Record<DatabaseType, number>,
          recent_activity: [],
        });
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  const complianceData = summary?.compliance_coverage
    ? Object.entries(summary.compliance_coverage).map(([key, value]) => ({
        name: COMPLIANCE_FRAMEWORKS.find(f => f.value === key)?.label || key,
        value,
      }))
    : [];

  const dbDistData = summary?.database_distribution
    ? Object.entries(summary.database_distribution).map(([key, value]) => ({
        name: key.charAt(0).toUpperCase() + key.slice(1),
        value,
      }))
    : [];

  const riskLevel = (summary?.risk_score ?? 0) <= 33 ? 'Low' : (summary?.risk_score ?? 0) <= 66 ? 'Medium' : 'Critical';
  const riskColor = (summary?.risk_score ?? 0) <= 33 ? 'var(--color-success)' : (summary?.risk_score ?? 0) <= 66 ? 'var(--color-warning)' : 'var(--color-danger)';

  return (
    <div className="dashboard">
      <div className="stats-grid">
        <MetricCard
          icon={Database}
          label="Connections"
          value={summary?.total_connections ?? 0}
          color="rgba(99,102,241,0.15)"
          loading={loading}
        />
        <MetricCard
          icon={Shield}
          label="Masking Rules"
          value={summary?.total_rules ?? 0}
          color="rgba(34,211,165,0.12)"
          loading={loading}
        />
        <MetricCard
          icon={Play}
          label="Jobs Run"
          value={summary?.total_jobs ?? 0}
          color="rgba(245,158,11,0.12)"
          loading={loading}
        />
        <MetricCard
          icon={FileDigit}
          label="Records Masked"
          value={summary?.total_records_processed ?? 0}
          color="rgba(244,63,94,0.12)"
          loading={loading}
        />
      </div>

      <div className="dashboard-grid">
        <div className="card">
          <div className="card-header">
            <h2>Risk Score</h2>
            <AlertTriangle size={18} style={{ color: riskColor }} />
          </div>
          <div className="risk-gauge">
            <div className="risk-gauge-value" style={{ color: riskColor }}>
              {summary?.risk_score ?? 0}%
            </div>
            <div className="risk-gauge-label">{riskLevel} Risk</div>
            <div className="risk-gauge-bar">
              <div
                className="risk-gauge-fill"
                style={{
                  width: `${summary?.risk_score ?? 0}%`,
                  background: riskColor,
                }}
              />
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <h2>Compliance Coverage</h2>
          </div>
          {complianceData.length > 0 ? (
            <Chart type="pie" data={complianceData} height={220} />
          ) : (
            <div className="empty-state" style={{ padding: '40px 0' }}>
              <p>No compliance data available</p>
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <h2>Database Distribution</h2>
          </div>
          {dbDistData.length > 0 ? (
            <Chart type="bar" data={dbDistData} height={220} />
          ) : (
            <div className="empty-state" style={{ padding: '40px 0' }}>
              <p>No database connections yet</p>
            </div>
          )}
        </div>

        <div className="card">
          <div className="card-header">
            <h2>Activity Feed</h2>
            <Activity size={18} style={{ color: 'var(--color-accent-2)' }} />
          </div>
          <div className="activity-feed">
            {summary?.recent_activity && summary.recent_activity.length > 0 ? (
              summary.recent_activity.map((entry: ActivityEntry) => (
                <div key={entry.id} className="activity-item">
                  <div className="activity-dot" />
                  <div className="activity-content">
                    <p className="activity-message">{entry.message}</p>
                    <span className="activity-time">
                      {formatDistanceToNow(new Date(entry.timestamp), { addSuffix: true })}
                    </span>
                  </div>
                </div>
              ))
            ) : (
              <div className="empty-state" style={{ padding: '24px 0' }}>
                <p>No recent activity</p>
              </div>
            )}
          </div>
        </div>
      </div>

      <div className="card" style={{ marginTop: '24px' }}>
        <div className="card-header">
          <h2>Quick Start</h2>
        </div>
        <div className="quickstart-steps">
          <div className="quickstart-step">
            <span className="quickstart-number">1</span>
            <div>
              <strong>Add a Connection</strong>
              <p>Register your database credentials to connect.</p>
            </div>
          </div>
          <div className="quickstart-step">
            <span className="quickstart-number">2</span>
            <div>
              <strong>Discover PII</strong>
              <p>Scan your schema for sensitive data automatically.</p>
            </div>
          </div>
          <div className="quickstart-step">
            <span className="quickstart-number">3</span>
            <div>
              <strong>Create Rules</strong>
              <p>Define masking strategies for each column.</p>
            </div>
          </div>
          <div className="quickstart-step">
            <span className="quickstart-number">4</span>
            <div>
              <strong>Run a Job</strong>
              <p>Apply masking and verify the results.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
