import { useState } from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import Login from './pages/Login';
import SecurityCam from './pages/SecurityCam';
import AlertDashboard from './pages/AlertDashboard';
import PerformanceDashboard from './pages/PerformanceDashboard';

const queryClient = new QueryClient();

export default function App() {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  const handleLogin = () => {
    setIsAuthenticated(true);
  };

  const handleLogout = () => {
    setIsAuthenticated(false);
  };

  if (!isAuthenticated) {
    return (
      <QueryClientProvider client={queryClient}>
        <Router>
          <Login onLogin={handleLogin} />
        </Router>
      </QueryClientProvider>
    );
  }

  return (
    <QueryClientProvider client={queryClient}>
      <Router>
        <Routes>
          <Route path="/security" element={<SecurityCam onLogout={handleLogout} />} />
          <Route path="/alerts" element={<AlertDashboard onLogout={handleLogout} />} />
          <Route path="/performance" element={<PerformanceDashboard onLogout={handleLogout} />} />
          <Route path="*" element={<Navigate to="/security" replace />} />
        </Routes>
      </Router>
    </QueryClientProvider>
  );
}