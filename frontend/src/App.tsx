import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import { useState, useCallback } from 'react';
import Layout from './components/Layout';
import ErrorBoundary from './components/ErrorBoundary';
import ToastContainer from './components/ToastContainer';
import Dashboard from './pages/Dashboard';
import Connections from './pages/Connections';
import Rules from './pages/Rules';
import Jobs from './pages/Jobs';
import Discovery from './pages/Discovery';
import Reports from './pages/Reports';
import Schedules from './pages/Schedules';
import Settings from './pages/Settings';
import Login from './pages/Login';
import Register from './pages/Register';
import { AuthProvider, ProtectedRoute } from './hooks/useAuth';

export type ToastType = 'success' | 'error' | 'info';

interface Toast {
  id: number;
  message: string;
  type: ToastType;
}

let toastId = 0;

function AppRoutes() {
  const [toasts, setToasts] = useState<Toast[]>([]);

  const addToast = useCallback((message: string, type: ToastType = 'info') => {
    const id = ++toastId;
    setToasts(prev => [...prev, { id, message, type }]);
    setTimeout(() => setToasts(prev => prev.filter(t => t.id !== id)), 4000);
  }, []);

  return (
    <>
      <Routes>
        <Route path="/login" element={<Login addToast={addToast} />} />
        <Route path="/register" element={<Register addToast={addToast} />} />
        <Route
          path="/*"
          element={
            <ProtectedRoute>
              <Layout>
                <ErrorBoundary>
                  <Routes>
                    <Route path="/" element={<Dashboard />} />
                    <Route path="/connections" element={<Connections addToast={addToast} />} />
                    <Route path="/rules" element={<Rules addToast={addToast} />} />
                    <Route path="/jobs" element={<Jobs addToast={addToast} />} />
                    <Route path="/discovery" element={<Discovery addToast={addToast} />} />
                    <Route path="/reports" element={<Reports />} />
                    <Route path="/schedules" element={<Schedules addToast={addToast} />} />
                    <Route path="/settings" element={<Settings addToast={addToast} />} />
                    <Route path="/admin" element={<ProtectedRoute requiredPermission="admin"><div className="empty-state"><h3>Admin Panel</h3><p>User management coming soon.</p></div></ProtectedRoute>} />
                    <Route path="*" element={<Navigate to="/" replace />} />
                  </Routes>
                </ErrorBoundary>
              </Layout>
            </ProtectedRoute>
          }
        />
      </Routes>
      <ToastContainer toasts={toasts} />
    </>
  );
}

export default function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
      </AuthProvider>
    </BrowserRouter>
  );
}
