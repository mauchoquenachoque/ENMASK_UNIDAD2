import { CheckCircle, XCircle, Info, X } from 'lucide-react';
import type { ToastType } from '../App';

interface Toast {
  id: number;
  message: string;
  type: ToastType;
}

interface Props {
  toasts: Toast[];
  onDismiss?: (id: number) => void;
}

const icons: Record<ToastType, typeof CheckCircle> = {
  success: CheckCircle,
  error: XCircle,
  info: Info,
};

const colors: Record<ToastType, string> = {
  success: 'toast-success',
  error: 'toast-error',
  info: 'toast-info',
};

export default function ToastContainer({ toasts, onDismiss }: Props) {
  return (
    <div className="toast-container" role="region" aria-label="Notifications">
      {toasts.map(t => {
        const Icon = icons[t.type];
        return (
          <div key={t.id} className={`toast ${colors[t.type]}`}>
            <Icon size={18} />
            <span className="toast-message">{t.message}</span>
            {onDismiss && (
              <button className="toast-dismiss" onClick={() => onDismiss(t.id)}>
                <X size={14} />
              </button>
            )}
          </div>
        );
      })}
    </div>
  );
}
