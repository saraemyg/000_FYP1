import { useState, useEffect } from 'react';
import api from '../../services/api';

const COLORS: Record<string, string> = {
  WALKING:    '#22c55e',
  STANDING:   '#3b82f6',
  BENDING:    '#a855f7',
  SITTING:    '#f59e0b',
  RUNNING:    '#ef4444',
  FALLING:    '#dc2626',
  SUSPICIOUS: '#6b7280',
  UNKNOWN:    '#d1d5db',
};

interface BehaviorEntry {
  name: string;
  value: number;
  percentage: number;
  color: string;
}

export default function BehaviorDistribution() {
  const [behaviors, setBehaviors] = useState<BehaviorEntry[]>([]);
  const [hoveredBehavior, setHoveredBehavior] = useState<string | null>(null);
  const [selectedNotifications, setSelectedNotifications] = useState<string[]>(['High Priority']);
  const [alertFocusEnabled, setAlertFocusEnabled] = useState(true);

  useEffect(() => {
    api.get('/alerts/triggered?limit=200').then(res => {
      const counts: Record<string, number> = {};
      for (const a of res.data) {
        const b = (a.matched_attributes?.behavior_type || 'unknown').toUpperCase();
        counts[b] = (counts[b] || 0) + 1;
      }
      const total = Object.values(counts).reduce((s, v) => s + v, 0) || 1;
      const entries: BehaviorEntry[] = Object.entries(counts)
        .sort((a, b) => b[1] - a[1])
        .map(([name, value]) => ({
          name,
          value,
          percentage: Math.round((value / total) * 1000) / 10,
          color: COLORS[name] || '#6b7280',
        }));
      setBehaviors(entries);
    }).catch(() => {});
  }, []);

  const notificationOptions = ['High Priority', 'Movements', 'Low Priority'];
  const toggleNotification = (opt: string) =>
    setSelectedNotifications(prev =>
      prev.includes(opt) ? prev.filter(x => x !== opt) : [...prev, opt]
    );

  const total = behaviors.reduce((s, b) => s + b.value, 0);
  const circumference = 2 * Math.PI * 40;

  let currentOffset = 0;
  const segments = behaviors.map(b => {
    const dashLen = (b.percentage / 100) * circumference;
    const seg = { ...b, dashLen, offset: currentOffset };
    currentOffset += dashLen;
    return seg;
  });

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Behavior Distribution</h3>

      <div className="flex items-center justify-center mb-6">
        <div className="relative w-48 h-48">
          {behaviors.length === 0 ? (
            <div className="flex items-center justify-center h-full text-gray-400 text-sm">Loading...</div>
          ) : (
            <>
              <svg viewBox="0 0 100 100" className="transform -rotate-90">
                <circle cx="50" cy="50" r="40" fill="none" stroke="#e5e7eb" strokeWidth="20" />
                {segments.map(seg => (
                  <circle
                    key={seg.name}
                    cx="50" cy="50" r="40"
                    fill="none"
                    stroke={seg.color}
                    strokeWidth={hoveredBehavior === seg.name ? 22 : 20}
                    strokeDasharray={`${seg.dashLen} ${circumference}`}
                    strokeDashoffset={-seg.offset}
                    className="cursor-pointer transition-all duration-300"
                    onMouseEnter={() => setHoveredBehavior(seg.name)}
                    onMouseLeave={() => setHoveredBehavior(null)}
                  />
                ))}
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                {hoveredBehavior ? (
                  <>
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">
                      {behaviors.find(b => b.name === hoveredBehavior)?.percentage}%
                    </div>
                    <div className="text-xs text-gray-600 dark:text-gray-400">{hoveredBehavior}</div>
                    <div className="text-xs text-gray-500">{behaviors.find(b => b.name === hoveredBehavior)?.value}</div>
                  </>
                ) : (
                  <>
                    <div className="text-2xl font-bold text-gray-900 dark:text-white">{total.toLocaleString()}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-400">Total</div>
                  </>
                )}
              </div>
            </>
          )}
        </div>
      </div>

      <div className="space-y-2">
        {behaviors.map(behavior => (
          <div key={behavior.name}
            className="flex items-center justify-between cursor-pointer p-1 rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            onMouseEnter={() => setHoveredBehavior(behavior.name)}
            onMouseLeave={() => setHoveredBehavior(null)}>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 rounded-full" style={{ backgroundColor: behavior.color }} />
              <span className="text-sm text-gray-700 dark:text-gray-300">{behavior.name}</span>
            </div>
            <div className="flex items-center gap-2">
              <span className="text-xs text-gray-500 dark:text-gray-400">{behavior.value}</span>
              <span className="text-sm font-medium text-gray-900 dark:text-white">{behavior.percentage}%</span>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-4 pt-4 border-t">
        <p className="text-xs text-gray-600 dark:text-gray-400 mb-2 font-medium">Notify me for these priority levels:</p>
        <div className="flex flex-wrap gap-2">
          {notificationOptions.map(opt => (
            <button key={opt} onClick={() => toggleNotification(opt)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium transition-all ${
                selectedNotifications.includes(opt)
                  ? 'bg-blue-100 text-blue-700 border border-blue-300'
                  : 'bg-gray-100 text-gray-600 border border-gray-300 hover:bg-gray-200'
              }`}>
              {selectedNotifications.includes(opt)
                ? <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>
                : <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24"><path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/></svg>
              }
              {opt}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-4 bg-blue-50 border border-blue-100 rounded-lg p-3">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-blue-900 font-medium">Alert Focus</p>
            <p className="text-xs text-blue-700 mt-1">Focus on critical activities with alert prioritization</p>
          </div>
          <button onClick={() => setAlertFocusEnabled(!alertFocusEnabled)}
            className="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            style={{ backgroundColor: alertFocusEnabled ? '#3b82f6' : '#d1d5db' }}>
            <span className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${alertFocusEnabled ? 'translate-x-6' : 'translate-x-1'}`} />
          </button>
        </div>
      </div>
    </div>
  );
}
