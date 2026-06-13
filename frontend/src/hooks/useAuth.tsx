import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
  type ReactNode,
} from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { authApi, setStoredToken, setStoredRefreshToken, clearStoredToken, getStoredToken } from '../services/api';
import type { User, UserRole } from '../types';
import { PERMISSIONS } from '../types';

interface AuthContextValue {
  user: User | null;
  loading: boolean;
  loginWithGoogle: (idToken: string) => Promise<User>;
  loginWithPassword: (email: string, password: string) => Promise<User>;
  logout: () => void;
  hasPermission: (permission: string) => boolean;
  hasRole: (role: UserRole) => boolean;
  hasAnyRole: (roles: UserRole[]) => boolean;
}

const AuthContext = createContext<AuthContextValue | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const loadUser = async () => {
      const token = getStoredToken();
      if (!token) {
        setLoading(false);
        return;
      }
      try {
        const current = await authApi.me();
        setUser(current);
      } catch {
        clearStoredToken();
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    loadUser();
  }, []);

  const loginWithGoogleFn = useCallback(async (idToken: string) => {
    const auth = await authApi.loginGoogle(idToken);
    setStoredToken(auth.access_token);
    if (auth.refresh_token) setStoredRefreshToken(auth.refresh_token);
    setUser(auth.user);
    return auth.user;
  }, []);

  const loginWithPasswordFn = useCallback(async (email: string, password: string) => {
    const auth = await authApi.login(email, password);
    setStoredToken(auth.access_token);
    if (auth.refresh_token) setStoredRefreshToken(auth.refresh_token);
    setUser(auth.user);
    return auth.user;
  }, []);

  const logout = useCallback(() => {
    clearStoredToken();
    setUser(null);
  }, []);

  const hasPermission = useCallback(
    (permission: string): boolean => {
      if (!user) return false;
      const perms = PERMISSIONS[user.role] || [];
      return perms.includes('*') || perms.includes(permission);
    },
    [user],
  );

  const hasRole = useCallback(
    (role: UserRole): boolean => user?.role === role,
    [user],
  );

  const hasAnyRole = useCallback(
    (roles: UserRole[]): boolean => !!user && roles.includes(user.role),
    [user],
  );

  const value = useMemo(
    () => ({
      user,
      loading,
      loginWithGoogle: loginWithGoogleFn,
      loginWithPassword: loginWithPasswordFn,
      logout,
      hasPermission,
      hasRole,
      hasAnyRole,
    }),
    [user, loading, loginWithGoogleFn, loginWithPasswordFn, logout, hasPermission, hasRole, hasAnyRole],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const context = useContext(AuthContext);
  if (!context) throw new Error('useAuth must be used within AuthProvider');
  return context;
}

export function usePermission(permission: string): boolean {
  const { hasPermission } = useAuth();
  return hasPermission(permission);
}

export function useRole(role: UserRole): boolean {
  const { hasRole } = useAuth();
  return hasRole(role);
}

export function useAnyRole(roles: UserRole[]): boolean {
  const { hasAnyRole } = useAuth();
  return hasAnyRole(roles);
}

export function ProtectedRoute({ children, requiredPermission }: { children: ReactNode; requiredPermission?: string }) {
  const { user, loading, hasPermission } = useAuth();
  const location = useLocation();

  if (loading) {
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh' }}>
        <div className="spinner" />
      </div>
    );
  }

  if (!user) {
    return <Navigate to="/login" state={{ from: location }} replace />;
  }

  if (requiredPermission && !hasPermission(requiredPermission)) {
    return (
      <div className="page-content">
        <div className="empty-state">
          <div className="empty-icon">&#x1f512;</div>
          <h3>Access Denied</h3>
          <p>You don&apos;t have permission to access this resource.</p>
        </div>
      </div>
    );
  }

  return <>{children}</>;
}
