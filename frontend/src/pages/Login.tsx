import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { fetchApiMeta } from '../services/api';
import { jwtDecode } from 'jwt-decode';
import { Loader2, Shield } from 'lucide-react';
import type { ToastType } from '../App';

interface Props {
  addToast: (msg: string, type?: ToastType) => void;
}

export default function Login({ addToast }: Props) {
  const { user, loginWithGoogle } = useAuth();
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [googleReady, setGoogleReady] = useState(false);

  useEffect(() => {
    if (user) navigate('/', { replace: true });
  }, [user, navigate]);

  useEffect(() => {
    const initGoogle = async () => {
      const meta = await fetchApiMeta();
      if (!meta) {
        addToast('Backend is not responding', 'error');
      }

      const scriptId = 'google-identity';
      if (!document.getElementById(scriptId)) {
        const s = document.createElement('script');
        s.src = 'https://accounts.google.com/gsi/client';
        s.id = scriptId;
        s.async = true;
        s.defer = true;
        document.head.appendChild(s);
        s.onload = () => renderButton();
      } else {
        renderButton();
      }
    };

    function renderButton() {
      // @ts-ignore
      if (!window.google?.accounts) return;

      const clientId = import.meta.env.VITE_GOOGLE_CLIENT_ID || '';
      if (!clientId) {
        addToast('VITE_GOOGLE_CLIENT_ID not configured', 'error');
        return;
      }

      // @ts-ignore
      window.google.accounts.id.initialize({
        client_id: clientId,
        callback: (resp: { credential?: string }) => {
          if (!resp?.credential) {
            addToast('Google login failed - no credential', 'error');
            return;
          }

          try {
            const decoded: { email?: string } = jwtDecode(resp.credential);
            const email = decoded.email || '';
            if (!email.endsWith('@virtual.upt.pe')) {
              addToast('Access denied: Use your @virtual.upt.pe institutional email', 'error');
              return;
            }
          } catch {
            addToast('Failed to process Google credentials', 'error');
            return;
          }

          setLoading(true);
          loginWithGoogle(resp.credential)
            .then(() => {
              addToast('Signed in successfully', 'success');
              navigate('/');
            })
            .catch((err: Error) => {
              addToast(err.message || 'Login failed', 'error');
            })
            .finally(() => setLoading(false));
        },
      });

      // @ts-ignore
      window.google.accounts.id.renderButton(document.getElementById('gsi-btn'), {
        theme: 'outline',
        size: 'large',
        width: 300,
      });
      setGoogleReady(true);
    }

    initGoogle();
  }, [addToast, loginWithGoogle, navigate]);

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <div className="login-logo">
            <div className="logo-icon">E</div>
            <span className="logo-text">Enmask</span>
          </div>
          <h1>Welcome back</h1>
          <p>Sign in with your institutional account to continue.</p>
        </div>

        <div className="login-body">
          <div id="gsi-btn" className="login-google-btn" />
          {!googleReady && (
            <div className="login-loading">
              <Loader2 size={20} className="loading-spinner-icon" />
              <span>Loading Google Sign-In...</span>
            </div>
          )}
          {loading && (
            <div className="login-loading">
              <Loader2 size={20} className="loading-spinner-icon" />
              <span>Signing in...</span>
            </div>
          )}
        </div>

        <div className="login-footer">
          <div className="login-restriction">
            <Shield size={14} />
            <span>Only @virtual.upt.pe accounts are allowed</span>
          </div>
        </div>
      </div>
    </div>
  );
}
