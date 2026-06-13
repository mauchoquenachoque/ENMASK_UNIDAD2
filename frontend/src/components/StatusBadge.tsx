import type { JobStatus, ConnectionStatus, DiscoveryConfidence } from '../types';

interface StatusBadgeProps {
  status: JobStatus | ConnectionStatus | DiscoveryConfidence | string;
  size?: 'sm' | 'md';
}

const statusConfig: Record<string, { class: string; label: string }> = {
  pending: { class: 'badge-pending', label: 'Pending' },
  running: { class: 'badge-warning', label: 'Running' },
  scanning: { class: 'badge-warning', label: 'Scanning' },
  completed: { class: 'badge-success', label: 'Completed' },
  failed: { class: 'badge-danger', label: 'Failed' },
  unmasked: { class: 'badge-info', label: 'Unmasked' },
  cancelled: { class: 'badge-pending', label: 'Cancelled' },
  scheduled: { class: 'badge-info', label: 'Scheduled' },
  connected: { class: 'badge-success', label: 'Connected' },
  disconnected: { class: 'badge-pending', label: 'Disconnected' },
  error: { class: 'badge-danger', label: 'Error' },
  testing: { class: 'badge-warning', label: 'Testing...' },
  high: { class: 'badge-danger', label: 'High' },
  medium: { class: 'badge-warning', label: 'Medium' },
  low: { class: 'badge-success', label: 'Low' },
  critical: { class: 'badge-danger', label: 'Critical' },
  masked: { class: 'badge-success', label: 'Masked' },
  unmasked_risk: { class: 'badge-danger', label: 'Unmasked' },
  partial: { class: 'badge-warning', label: 'Partial' },
};

export default function StatusBadge({ status, size = 'sm' }: StatusBadgeProps) {
  const config = statusConfig[status] || { class: 'badge-info', label: status };
  return (
    <span className={`badge ${config.class} ${size === 'md' ? 'badge-md' : ''}`}>
      {config.label}
    </span>
  );
}
