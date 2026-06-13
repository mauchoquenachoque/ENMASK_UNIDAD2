import { Loader2 } from 'lucide-react';

interface LoadingSpinnerProps {
  size?: number;
  message?: string;
  fullPage?: boolean;
}

export default function LoadingSpinner({ size = 24, message, fullPage = false }: LoadingSpinnerProps) {
  const content = (
    <div className={`loading-spinner-container ${fullPage ? 'loading-fullpage' : ''}`}>
      <Loader2 className="loading-spinner-icon" size={size} />
      {message && <p className="loading-spinner-message">{message}</p>}
    </div>
  );

  return content;
}
