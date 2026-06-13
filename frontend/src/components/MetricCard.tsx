import type { LucideIcon } from 'lucide-react';

interface MetricCardProps {
  icon: LucideIcon;
  label: string;
  value: string | number;
  trend?: {
    value: number;
    direction: 'up' | 'down';
    label?: string;
  };
  color?: string;
  loading?: boolean;
}

export default function MetricCard({ icon: Icon, label, value, trend, color, loading = false }: MetricCardProps) {
  return (
    <div className="metric-card">
      <div className="metric-card-icon" style={color ? { background: color } : undefined}>
        <Icon size={22} />
      </div>
      <div className="metric-card-content">
        {loading ? (
          <div className="spinner" />
        ) : (
          <>
            <div className="metric-card-value">{typeof value === 'number' ? value.toLocaleString() : value}</div>
            <div className="metric-card-label">{label}</div>
            {trend && (
              <div className={`metric-card-trend ${trend.direction === 'up' ? 'trend-up' : 'trend-down'}`}>
                <span>{trend.direction === 'up' ? '↑' : '↓'}</span>
                <span>{Math.abs(trend.value)}%</span>
                {trend.label && <span className="trend-label">{trend.label}</span>}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
}
