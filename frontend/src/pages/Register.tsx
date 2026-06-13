import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../hooks/useAuth';
import { authApi, setStoredToken, setStoredRefreshToken } from '../services/api';
import { Loader2, Shield } from 'lucide-react';
import type { ToastType } from '../App';

interface Props {
  addToast: (msg: string, type?: ToastType) => void;
}

export default function Register({ addToast }: Props) {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(false);
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');

  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!name || !email || !password) {
      addToast('All fields are required', 'error');
      return;
    }

    if (password.length < 8) {
      addToast('Password must be at least 8 characters', 'error');
      return;
    }

    if (password !== confirmPassword) {
      addToast('Passwords do not match', 'error');
      return;
    }

    setLoading(true);
    try {
      const auth = await authApi.register(email, password, name);
      setStoredToken(auth.access_token);
      if (auth.refresh_token) setStoredRefreshToken(auth.refresh_token);
      addToast('Account created successfully', 'success');
      navigate('/');
    } catch (err: any) {
      addToast(err.message || 'Registration failed', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <div className="login-logo">
            <div className="logo-icon">E</div>
            <span className="logo-text">Enmask</span>
          </div>
          <h1>Create Account</h1>
          <p>Register to get started with Enmask.</p>
        </div>

        <div className="login-body">
          <form onSubmit={handleRegister} className="login-form">
            <div className="form-group">
              <label htmlFor="name">Full Name</label>
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Your full name"
                required
                autoFocus
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="your@email.com"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Min 8 characters"
                required
                minLength={8}
              />
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword">Confirm Password</label>
              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                placeholder="Repeat your password"
                required
                minLength={8}
              />
            </div>

            <button type="submit" className="btn-primary" disabled={loading}>
              {loading ? (
                <>
                  <Loader2 size={16} className="loading-spinner-icon" />
                  Creating account...
                </>
              ) : (
                'Register'
              )}
            </button>

            <div className="login-register-link">
              <p>Already have an account? <Link to="/login">Sign In</Link></p>
            </div>
          </form>
        </div>

        <div className="login-footer">
          <div className="login-restriction">
            <Shield size={14} />
            <span>Secure registration</span>
          </div>
        </div>
      </div>
    </div>
  );
}
