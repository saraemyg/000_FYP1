import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { AuthProvider, useAuth } from './hooks/useAuth';
import Layout from './components/Layout';
import Login from './pages/Login';
import SecurityCam from './pages/SecurityCam';
import AlertDashboard from './pages/AlertDashboard';
import PerformanceDashboard from './pages/PerformanceDashboard';

const queryClient = new QueryClient();

function AppRoutes() {
  const { isAuthenticated, isLoading, user } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50 dark:bg-gray-900">
        <div className="text-gray-500 text-sm">Loading...</div>
      </div>
    );
  }

  if (!isAuthenticated) return <Login />;

  return (
    <Routes>
      <Route element={<Layout />}>
        <Route path="/security" element={<SecurityCam />} />
        <Route path="/alerts" element={<AlertDashboard />} />
        <Route
          path="/performance"
          element={user?.role === 'admin' ? <PerformanceDashboard /> : <Navigate to="/security" replace />}
        />
        <Route path="*" element={<Navigate to="/security" replace />} />
      </Route>
    </Routes>
  );
}

export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <Router>
          <AppRoutes />
        </Router>
      </AuthProvider>
    </QueryClientProvider>
  );
}
