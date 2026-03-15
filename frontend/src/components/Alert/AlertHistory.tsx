import { useState, useMemo, useEffect } from 'react';
import api from '../../services/api';

interface Alert {
  id: string;
  timestamp: string;
  camera: string;
  behavior: string;
  confidence: number;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'PENDING' | 'ACKNOWLEDGED';
}

function inferPriority(behavior: string, confidence: number): 'HIGH' | 'MEDIUM' | 'LOW' {
  const highBehaviors = ['falling', 'suspicious', 'running'];
  const medBehaviors = ['bending'];
  const b = behavior.toLowerCase();
  if (highBehaviors.includes(b) || confidence >= 0.9) return 'HIGH';
  if (medBehaviors.includes(b) || confidence >= 0.75) return 'MEDIUM';
  return 'LOW';
}

export default function AlertHistory() {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [searchQuery, setSearchQuery] = useState('');
  const [cameraFilter, setCameraFilter] = useState('All Cameras');
  const [behaviorFilter, setBehaviorFilter] = useState('All Behaviors');
  const [priorityFilter, setPriorityFilter] = useState('All Priorities');
  const [statusFilter, setStatusFilter] = useState('All Statuses');
  const [currentPage, setCurrentPage] = useState(1);
  const itemsPerPage = 10;

  useEffect(() => {
    setLoading(true);
    api.get('/alerts/triggered?limit=200')
      .then(res => {
        const mapped: Alert[] = res.data.map((a: any) => {
          const behavior = a.matched_attributes?.behavior_type || 'unknown';
          const confidence = Math.round((a.confidence_score || 0) * 100);
          const priority = inferPriority(behavior, a.confidence_score || 0);
          const status = a.is_acknowledged ? 'ACKNOWLEDGED' : 'PENDING';
          return {
            id: `#${a.alert_id}`,
            timestamp: new Date(a.triggered_at).toLocaleString('en-US', {
              month: 'short', day: 'numeric', year: 'numeric',
              hour: '2-digit', minute: '2-digit', hour12: true,
            }),
            camera: a.video_filename || 'Unknown',
            behavior: behavior.toUpperCase(),
            confidence,
            priority,
            status,
          };
        });
        setAlerts(mapped);
      })
      .catch(() => setError('Failed to load alerts.'))
      .finally(() => setLoading(false));
  }, []);

  const cameras = ['All Cameras', ...Array.from(new Set(alerts.map(a => a.camera)))];
  const behaviors = ['All Behaviors', ...Array.from(new Set(alerts.map(a => a.behavior)))];
  const priorities = ['All Priorities', 'HIGH', 'MEDIUM', 'LOW'];
  const statuses = ['All Statuses', 'PENDING', 'ACKNOWLEDGED'];

  const filteredAlerts = useMemo(() => {
    return alerts.filter(alert => {
      const matchesSearch =
        alert.id.toLowerCase().includes(searchQuery.toLowerCase()) ||
        alert.camera.toLowerCase().includes(searchQuery.toLowerCase()) ||
        alert.behavior.toLowerCase().includes(searchQuery.toLowerCase());
      const matchesCamera = cameraFilter === 'All Cameras' || alert.camera === cameraFilter;
      const matchesBehavior = behaviorFilter === 'All Behaviors' || alert.behavior === behaviorFilter;
      const matchesPriority = priorityFilter === 'All Priorities' || alert.priority === priorityFilter;
      const matchesStatus = statusFilter === 'All Statuses' || alert.status === statusFilter;
      return matchesSearch && matchesCamera && matchesBehavior && matchesPriority && matchesStatus;
    });
  }, [alerts, searchQuery, cameraFilter, behaviorFilter, priorityFilter, statusFilter]);

  const totalPages = Math.ceil(filteredAlerts.length / itemsPerPage);
  const startIndex = (currentPage - 1) * itemsPerPage;
  const currentAlerts = filteredAlerts.slice(startIndex, startIndex + itemsPerPage);

  const handleExportCSV = () => {
    const headers = ['ID', 'Timestamp', 'Camera', 'Behavior', 'Confidence', 'Priority', 'Status'];
    const csvContent = [
      headers.join(','),
      ...filteredAlerts.map(a =>
        [a.id, `"${a.timestamp}"`, `"${a.camera}"`, a.behavior, `${a.confidence}%`, a.priority, a.status].join(',')
      ),
    ].join('\n');
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    link.setAttribute('href', URL.createObjectURL(blob));
    link.setAttribute('download', `alert_history_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getPriorityColor = (p: string) =>
    p === 'HIGH' ? 'bg-red-500 text-white' : p === 'MEDIUM' ? 'bg-yellow-500 text-white' : 'bg-green-500 text-white';

  const getStatusColor = (s: string) =>
    s === 'PENDING' ? 'bg-yellow-500 text-white' : 'bg-blue-600 text-white';

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Alert History</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">View and analyze historical alert data</p>
        </div>
        <button
          onClick={handleExportCSV}
          className="flex items-center gap-2 px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          Export CSV
        </button>
      </div>

      <div className="mb-4 p-4 border border-gray-200 dark:border-gray-700 rounded-lg">
        <div className="flex items-center gap-2 mb-3">
          <svg className="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
          </svg>
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Filters</span>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
          <input type="text" value={searchQuery} onChange={e => { setSearchQuery(e.target.value); setCurrentPage(1); }}
            placeholder="Search alerts..."
            className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500" />
          {[
            { value: cameraFilter, setter: setCameraFilter, options: cameras },
            { value: behaviorFilter, setter: setBehaviorFilter, options: behaviors },
            { value: priorityFilter, setter: setPriorityFilter, options: priorities },
            { value: statusFilter, setter: setStatusFilter, options: statuses },
          ].map(({ value, setter, options }, i) => (
            <select key={i} value={value} onChange={e => { setter(e.target.value); setCurrentPage(1); }}
              className="px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500">
              {options.map(o => <option key={o} value={o}>{o}</option>)}
            </select>
          ))}
        </div>
      </div>

      {loading ? (
        <div className="text-center py-10 text-gray-500">Loading alerts...</div>
      ) : error ? (
        <div className="text-center py-10 text-red-500">{error}</div>
      ) : (
        <>
          <p className="text-sm text-gray-500 dark:text-gray-400 mb-4">
            Showing {startIndex + 1}–{Math.min(startIndex + itemsPerPage, filteredAlerts.length)} of {filteredAlerts.length} results
          </p>
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50 dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700">
                <tr>
                  {['ID', 'Timestamp', 'Camera', 'Behavior', 'Confidence', 'Priority', 'Status', 'Actions'].map(h => (
                    <th key={h} className={`px-4 py-3 text-left text-xs font-medium text-gray-700 dark:text-gray-300 ${h === 'Actions' ? 'text-center' : ''}`}>{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {currentAlerts.map(alert => (
                  <tr key={alert.id} className="hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">{alert.id}</td>
                    <td className="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{alert.timestamp}</td>
                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">{alert.camera}</td>
                    <td className="px-4 py-3 text-sm font-semibold text-gray-900 dark:text-white">{alert.behavior}</td>
                    <td className="px-4 py-3 text-sm text-gray-900 dark:text-white">{alert.confidence}%</td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded text-xs font-bold ${getPriorityColor(alert.priority)}`}>{alert.priority}</span>
                    </td>
                    <td className="px-4 py-3">
                      <span className={`px-2 py-1 rounded text-xs font-medium ${getStatusColor(alert.status)}`}>{alert.status}</span>
                    </td>
                    <td className="px-4 py-3 text-center">
                      <button className="text-gray-600 dark:text-gray-400 hover:text-gray-900 transition-colors">
                        <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                        </svg>
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>

          <div className="mt-4 flex items-center justify-between">
            <div className="text-sm text-gray-600 dark:text-gray-400">Page {currentPage} of {totalPages}</div>
            <div className="flex gap-2">
              <button onClick={() => setCurrentPage(p => Math.max(1, p - 1))} disabled={currentPage === 1}
                className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                Previous
              </button>
              {Array.from({ length: totalPages }, (_, i) => i + 1)
                .filter(p => p === 1 || p === totalPages || (p >= currentPage - 1 && p <= currentPage + 1))
                .map((page, idx, arr) => (
                  <div key={page} className="flex items-center">
                    {idx > 0 && arr[idx - 1] !== page - 1 && <span className="px-2 text-gray-500">...</span>}
                    <button onClick={() => setCurrentPage(page)}
                      className={`px-3 py-1 border rounded text-sm font-medium transition-colors ${currentPage === page ? 'bg-blue-600 text-white border-blue-600' : 'border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50'}`}>
                      {page}
                    </button>
                  </div>
                ))}
              <button onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))} disabled={currentPage === totalPages}
                className="px-3 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed transition-colors">
                Next
              </button>
            </div>
          </div>
        </>
      )}
    </div>
  );
}
