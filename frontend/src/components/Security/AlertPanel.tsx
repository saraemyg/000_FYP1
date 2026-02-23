import { useState, useMemo } from 'react';

interface Alert {
  id: string;
  behavior: string;
  priority: 'HIGH' | 'MEDIUM' | 'LOW';
  status: 'PENDING' | 'ACKNOWLEDGED';
  location: string;
  cameraId: string;
  cameraName: string;
  time: string;
  confidence: number;
}

interface AlertPanelProps {
  onViewCamera?: (cameraId: string) => void;
}

export default function AlertPanel({ onViewCamera = () => {} }: AlertPanelProps) {
  const [sortBy, setSortBy] = useState<'priority' | 'confidence'>('priority');

  const summary = {
    total: 127,
    period: 'Last 24 hours',
    active: 4,
    loitering: '1.2s'
  };

  const priorities = [
    { label: 'High Priority', count: 8, color: 'bg-red-50 border-red-200', textColor: 'text-red-700' },
    { label: 'Medium Priority', count: 5, color: 'bg-yellow-50 border-yellow-200', textColor: 'text-yellow-700' },
    { label: 'Low Priority', count: 3, color: 'bg-green-50 border-green-200', textColor: 'text-green-700' }
  ];

  // Generate more mock alerts for scrolling
  const allAlerts: Alert[] = [
    {
      id: '1',
      behavior: 'RUN',
      priority: 'HIGH',
      status: 'PENDING',
      location: 'Entrance Lobby',
      cameraId: 'cam-3',
      cameraName: 'Cam C',
      time: '5m ago',
      confidence: 95.0
    },
    {
      id: '2',
      behavior: 'RUN',
      priority: 'HIGH',
      status: 'PENDING',
      location: 'Parking Lot',
      cameraId: 'cam-1',
      cameraName: 'Cam A',
      time: '8m ago',
      confidence: 89.0
    },
    {
      id: '3',
      behavior: 'BEND',
      priority: 'MEDIUM',
      status: 'PENDING',
      location: 'Corridor A',
      cameraId: 'cam-2',
      cameraName: 'Cam B',
      time: '12m ago',
      confidence: 82.0
    },
    {
      id: '4',
      behavior: 'RUN',
      priority: 'HIGH',
      status: 'PENDING',
      location: 'Building B',
      cameraId: 'cam-4',
      cameraName: 'Cam D',
      time: '15m ago',
      confidence: 91.0
    },
    {
      id: '5',
      behavior: 'BEND',
      priority: 'MEDIUM',
      status: 'PENDING',
      location: 'Parking Lot',
      cameraId: 'cam-1',
      cameraName: 'Cam A',
      time: '18m ago',
      confidence: 78.0
    },
    {
      id: '6',
      behavior: 'STAND',
      priority: 'LOW',
      status: 'PENDING',
      location: 'Entrance Lobby',
      cameraId: 'cam-3',
      cameraName: 'Cam C',
      time: '22m ago',
      confidence: 87.0
    },
    {
      id: '7',
      behavior: 'RUN',
      priority: 'HIGH',
      status: 'ACKNOWLEDGED',
      location: 'Corridor A',
      cameraId: 'cam-2',
      cameraName: 'Cam B',
      time: '25m ago',
      confidence: 93.0
    },
    {
      id: '8',
      behavior: 'BEND',
      priority: 'MEDIUM',
      status: 'PENDING',
      location: 'Building B',
      cameraId: 'cam-4',
      cameraName: 'Cam D',
      time: '28m ago',
      confidence: 85.0
    },
    {
      id: '9',
      behavior: 'WALK',
      priority: 'LOW',
      status: 'ACKNOWLEDGED',
      location: 'Parking Lot',
      cameraId: 'cam-1',
      cameraName: 'Cam A',
      time: '32m ago',
      confidence: 76.0
    },
    {
      id: '10',
      behavior: 'RUN',
      priority: 'HIGH',
      status: 'PENDING',
      location: 'Entrance Lobby',
      cameraId: 'cam-3',
      cameraName: 'Cam C',
      time: '35m ago',
      confidence: 88.0
    },
    {
      id: '11',
      behavior: 'STAND',
      priority: 'LOW',
      status: 'ACKNOWLEDGED',
      location: 'Corridor A',
      cameraId: 'cam-2',
      cameraName: 'Cam B',
      time: '38m ago',
      confidence: 72.0
    },
    {
      id: '12',
      behavior: 'BEND',
      priority: 'MEDIUM',
      status: 'ACKNOWLEDGED',
      location: 'Building B',
      cameraId: 'cam-4',
      cameraName: 'Cam D',
      time: '42m ago',
      confidence: 80.0
    },
    {
      id: '13',
      behavior: 'RUN',
      priority: 'HIGH',
      status: 'PENDING',
      location: 'Parking Lot',
      cameraId: 'cam-1',
      cameraName: 'Cam A',
      time: '45m ago',
      confidence: 94.0
    },
    {
      id: '14',
      behavior: 'WALK',
      priority: 'LOW',
      status: 'PENDING',
      location: 'Entrance Lobby',
      cameraId: 'cam-3',
      cameraName: 'Cam C',
      time: '48m ago',
      confidence: 75.0
    },
    {
      id: '15',
      behavior: 'BEND',
      priority: 'MEDIUM',
      status: 'ACKNOWLEDGED',
      location: 'Corridor A',
      cameraId: 'cam-2',
      cameraName: 'Cam B',
      time: '52m ago',
      confidence: 83.0
    }
  ];

  // Sort alerts based on selected criteria
  const sortedAlerts = useMemo(() => {
    const sorted = [...allAlerts];
    
    if (sortBy === 'priority') {
      const priorityOrder = { HIGH: 0, MEDIUM: 1, LOW: 2 };
      sorted.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
    } else {
      sorted.sort((a, b) => b.confidence - a.confidence);
    }
    
    return sorted;
  }, [sortBy]);

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'HIGH':
        return 'bg-red-500';
      case 'MEDIUM':
        return 'bg-yellow-500';
      case 'LOW':
        return 'bg-green-500';
      default:
        return 'bg-gray-500';
    }
  };

  const getStatusColor = (status: string) => {
    return status === 'PENDING' ? 'bg-yellow-500' : 'bg-blue-500';
  };

  return (
    <div className="bg-white dark:bg-gray-800 dark:bg-gray-800 rounded-lg shadow-sm p-4 flex flex-col" style={{ height: '100%', maxHeight: '800px' }}>
      <h2 className="text-xl font-bold text-gray-900 dark:text-white mb-4">Alert</h2>

      <div className="grid grid-cols-3 gap-3 mb-4">
        <div className="bg-red-50 border border-red-100 rounded-lg p-3 text-center">
          <svg className="w-6 h-6 text-red-500 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
          <div className="text-2xl font-bold text-red-700">{summary.total}</div>
          <div className="text-xs text-red-600 mt-1">Total Alerts</div>
          <div className="text-[10px] text-red-500 mt-0.5">{summary.period}</div>
        </div>

        <div className="bg-blue-50 border border-blue-100 rounded-lg p-3 text-center">
          <svg className="w-6 h-6 text-blue-500 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
          <div className="text-2xl font-bold text-blue-700">{summary.active}</div>
          <div className="text-xs text-blue-600 mt-1">Active Cameras</div>
          <div className="text-[10px] text-blue-500 mt-0.5">All operational</div>
        </div>

        <div className="bg-yellow-50 border border-yellow-100 rounded-lg p-3 text-center">
          <svg className="w-6 h-6 text-yellow-500 mx-auto mb-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div className="text-2xl font-bold text-yellow-700">{summary.loitering}</div>
          <div className="text-xs text-yellow-600 mt-1">Loitering</div>
          <div className="text-[10px] text-yellow-500 mt-0.5">Average duration</div>
        </div>
      </div>

      <div className="grid grid-cols-3 gap-2 mb-4">
        {priorities.map((priority, index) => (
          <div key={index} className={`${priority.color} border rounded-lg p-2`}>
            <div className="text-xs font-medium text-gray-600 dark:text-gray-400 mb-1">{priority.label}</div>
            <div className={`text-lg font-bold ${priority.textColor}`}>{priority.count}</div>
            <div className="text-[10px] text-gray-500 dark:text-gray-400">Active criteria</div>
          </div>
        ))}
      </div>

      <div className="border-t pt-4 flex-1 flex flex-col min-h-0 overflow-hidden">
        <div className="flex items-center justify-between mb-3">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Alert Notifications</h3>
          
          {/* Sort Dropdown */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value as 'priority' | 'confidence')}
            className="text-xs border border-gray-300 dark:border-gray-600 rounded px-2 py-1 focus:outline-none focus:ring-2 focus:ring-blue-500"
          >
            <option value="priority">Sort by Priority</option>
            <option value="confidence">Sort by Confidence</option>
          </select>
        </div>
        
        <div className="flex-1 overflow-y-auto space-y-3 pr-2" style={{ maxHeight: 'calc(100% - 2rem)' }}>
          {sortedAlerts.map((alert) => (
            <div
              key={alert.id}
              className="border-l-4 rounded-r-lg p-3 bg-gray-50 dark:bg-gray-900 dark:bg-gray-700 flex-shrink-0"
              style={{ borderLeftColor: alert.priority === 'HIGH' ? '#ef4444' : alert.priority === 'MEDIUM' ? '#eab308' : '#22c55e' }}
            >
              <div className="flex items-start justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 ${getPriorityColor(alert.priority)} text-white text-xs font-bold rounded`}>
                    {alert.behavior}
                  </span>
                  <span className={`px-2 py-0.5 ${getStatusColor(alert.status)} text-white text-xs font-medium rounded`}>
                    {alert.status}
                  </span>
                </div>
              </div>

              <div className="flex items-center gap-1 text-sm text-gray-600 dark:text-gray-400 mb-1">
                <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                </svg>
                {alert.location} ({alert.cameraName})
              </div>

              <div className="flex items-center gap-1 text-xs text-gray-500 dark:text-gray-400 mb-2">
                <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                {alert.time}
              </div>

              <div className="text-xs text-gray-700 dark:text-gray-300 mb-2">
                Confidence: <span className="font-semibold">{alert.confidence}%</span>
              </div>

              <div className="flex gap-2">
                <button 
                  onClick={() => onViewCamera(alert.cameraId)}
                  className="flex items-center justify-center gap-1 px-3 py-1.5 bg-purple-600 text-white rounded text-xs font-medium hover:bg-purple-700 transition"
                  title="View Camera"
                >
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  View
                </button>
                <button className="flex-1 bg-blue-600 text-white px-3 py-1.5 rounded text-xs font-medium hover:bg-blue-700 transition flex items-center justify-center gap-1">
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                  </svg>
                  Acknowledge
                </button>
                <button className="flex-1 bg-gray-600 text-white px-3 py-1.5 rounded text-xs font-medium hover:bg-gray-700 transition flex items-center justify-center gap-1">
                  <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                  False Positive
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}