import { useState } from 'react';

export default function BehaviorDistribution() {
  const [hoveredBehavior, setHoveredBehavior] = useState<string | null>(null);
  const [selectedNotifications, setSelectedNotifications] = useState<string[]>(['High Priority']);
  const [alertFocusEnabled, setAlertFocusEnabled] = useState(true);

  const behaviors = [
    { name: 'WALK', percentage: 44.3, color: '#22c55e', value: 2840 },
    { name: 'STAND', percentage: 33.0, color: '#3b82f6', value: 2115 },
    { name: 'BEND', percentage: 18.0, color: '#a855f7', value: 1153 },
    { name: 'SIT', percentage: 4.7, color: '#f59e0b', value: 301 },
    { name: 'RUN', percentage: 5.0, color: '#ef4444', value: 320 }
  ];

  const notificationOptions = ['High Priority', 'Movements', 'Low Priority'];

  const toggleNotification = (option: string) => {
    if (selectedNotifications.includes(option)) {
      setSelectedNotifications(selectedNotifications.filter(item => item !== option));
    } else {
      setSelectedNotifications([...selectedNotifications, option]);
    }
  };

  // Calculate angles for pie chart
  let currentAngle = -90; // Start from top
  const segments = behaviors.map(behavior => {
    const startAngle = currentAngle;
    const angle = (behavior.percentage / 100) * 360;
    currentAngle += angle;
    return {
      ...behavior,
      startAngle,
      endAngle: currentAngle
    };
  });

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
      <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-4">Behavior Distribution</h3>
      
      <div className="flex items-center justify-center mb-6">
        <div className="relative w-48 h-48">
          <svg viewBox="0 0 100 100" className="transform -rotate-90">
            <circle
              cx="50"
              cy="50"
              r="40"
              fill="none"
              stroke="#e5e7eb"
              strokeWidth="20"
            />
            {segments.map((segment) => {
              const circumference = 2 * Math.PI * 40;
              const offset = ((100 - segment.percentage) / 100) * circumference;
              const prevPercentage = behaviors
                .slice(0, behaviors.findIndex(b => b.name === segment.name))
                .reduce((sum, b) => sum + b.percentage, 0);
              const rotateOffset = (prevPercentage / 100) * circumference;
              
              const isHovered = hoveredBehavior === segment.name;
              
              return (
                <g key={segment.name}>
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    fill="none"
                    stroke={segment.color}
                    strokeWidth={isHovered ? "22" : "20"}
                    strokeDasharray={`${(segment.percentage / 100) * circumference} ${circumference}`}
                    strokeDashoffset={-rotateOffset}
                    className="cursor-pointer transition-all duration-300"
                    onMouseEnter={() => setHoveredBehavior(segment.name)}
                    onMouseLeave={() => setHoveredBehavior(null)}
                    style={{
                      filter: isHovered ? 'drop-shadow(0 0 8px rgba(0, 0, 0, 0.3))' : 'none'
                    }}
                  />
                </g>
              );
            })}
          </svg>
          
          {/* Center text */}
          <div className="absolute inset-0 flex flex-col items-center justify-center">
            {hoveredBehavior ? (
              <>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {behaviors.find(b => b.name === hoveredBehavior)?.percentage}%
                </div>
                <div className="text-xs text-gray-600 dark:text-gray-400">{hoveredBehavior}</div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {behaviors.find(b => b.name === hoveredBehavior)?.value}
                </div>
              </>
            ) : (
              <>
                <div className="text-2xl font-bold text-gray-900 dark:text-white">
                  {behaviors.reduce((sum, b) => sum + b.value, 0).toLocaleString()}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">Total</div>
              </>
            )}
          </div>
        </div>
      </div>

      <div className="space-y-2">
        {behaviors.map((behavior) => (
          <div 
            key={behavior.name} 
            className="flex items-center justify-between cursor-pointer p-1 rounded hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
            onMouseEnter={() => setHoveredBehavior(behavior.name)}
            onMouseLeave={() => setHoveredBehavior(null)}
          >
            <div className="flex items-center gap-2">
              <div
                className="w-3 h-3 rounded-full"
                style={{ backgroundColor: behavior.color }}
              />
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
          {notificationOptions.map((option) => (
            <button
              key={option}
              onClick={() => toggleNotification(option)}
              className={`flex items-center gap-1.5 px-3 py-1.5 rounded text-xs font-medium transition-all ${
                selectedNotifications.includes(option)
                  ? 'bg-blue-100 text-blue-700 border border-blue-300'
                  : 'bg-gray-100 text-gray-600 dark:text-gray-400 border border-gray-300 dark:border-gray-600 hover:bg-gray-200 dark:hover:bg-gray-600'
              }`}
            >
              {selectedNotifications.includes(option) ? (
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                </svg>
              ) : (
                <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
                </svg>
              )}
              {option}
            </button>
          ))}
        </div>
      </div>

      <div className="mt-4 bg-blue-50 border border-blue-100 rounded-lg p-3">
        <div className="flex items-center justify-between">
          <div>
            <p className="text-xs text-blue-900 font-medium">Alert Focus</p>
            <p className="text-xs text-blue-700 mt-1">
              Focus on critical activities with alert prioritization
            </p>
          </div>
          <button
            onClick={() => setAlertFocusEnabled(!alertFocusEnabled)}
            className="relative inline-flex h-6 w-11 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            style={{ backgroundColor: alertFocusEnabled ? '#3b82f6' : '#d1d5db' }}
          >
            <span
              className={`inline-block h-4 w-4 transform rounded-full bg-white transition-transform ${
                alertFocusEnabled ? 'translate-x-6' : 'translate-x-1'
              }`}
            />
          </button>
        </div>
      </div>
    </div>
  );
}