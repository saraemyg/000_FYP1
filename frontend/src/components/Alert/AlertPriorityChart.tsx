import { useState, useEffect } from 'react';

export default function AlertPriorityChart() {
  const [hoveredBar, setHoveredBar] = useState<{ camera: string; priority: string } | null>(null);
  const [showTimeAnalysis, setShowTimeAnalysis] = useState(false);
  const [animated, setAnimated] = useState(false);
  const [hoveredHour, setHoveredHour] = useState<number | null>(null);

  useEffect(() => {
    // Trigger animation on mount
    setTimeout(() => setAnimated(true), 100);
  }, []);

  const cameraData = [
    { label: 'Cam A', location: 'Parking Lot', high: 45, medium: 28, low: 15 }, // Most dangerous
    { label: 'Cam B', location: 'Corridor A', high: 25, medium: 35, low: 30 },
    { label: 'Cam C', location: 'Entrance Lobby', high: 18, medium: 32, low: 38 },
    { label: 'Cam D', location: 'Building B', high: 5, medium: 20, low: 60 }  // Safest
  ];

  // 24-hour alert distribution data (mock data showing peak hours)
  const hourlyAlerts = [
    { hour: 0, count: 3 },   // 12 AM - 1 AM
    { hour: 1, count: 2 },   // 1 AM - 2 AM
    { hour: 2, count: 1 },   // 2 AM - 3 AM (Safest)
    { hour: 3, count: 1 },   // 3 AM - 4 AM
    { hour: 4, count: 2 },   // 4 AM - 5 AM
    { hour: 5, count: 5 },   // 5 AM - 6 AM
    { hour: 6, count: 12 },  // 6 AM - 7 AM
    { hour: 7, count: 18 },  // 7 AM - 8 AM
    { hour: 8, count: 25 },  // 8 AM - 9 AM
    { hour: 9, count: 22 },  // 9 AM - 10 AM
    { hour: 10, count: 15 }, // 10 AM - 11 AM
    { hour: 11, count: 14 }, // 11 AM - 12 PM
    { hour: 12, count: 16 }, // 12 PM - 1 PM
    { hour: 13, count: 13 }, // 1 PM - 2 PM
    { hour: 14, count: 11 }, // 2 PM - 3 PM
    { hour: 15, count: 14 }, // 3 PM - 4 PM
    { hour: 16, count: 18 }, // 4 PM - 5 PM
    { hour: 17, count: 28 }, // 5 PM - 6 PM
    { hour: 18, count: 32 }, // 6 PM - 7 PM (Peak - Highest)
    { hour: 19, count: 24 }, // 7 PM - 8 PM
    { hour: 20, count: 16 }, // 8 PM - 9 PM
    { hour: 21, count: 12 }, // 9 PM - 10 PM
    { hour: 22, count: 8 },  // 10 PM - 11 PM
    { hour: 23, count: 5 }   // 11 PM - 12 AM
  ];

  const maxHourlyAlerts = Math.max(...hourlyAlerts.map(h => h.count));

  // Find peak hours (highest alert count)
  const peakHour = hourlyAlerts.reduce((max, curr) => curr.count > max.count ? curr : max);
  const safestHour = hourlyAlerts.reduce((min, curr) => curr.count < min.count ? curr : min);

  const formatHour = (hour: number) => {
    const period = hour >= 12 ? 'PM' : 'AM';
    const displayHour = hour === 0 ? 12 : hour > 12 ? hour - 12 : hour;
    return `${displayHour}${period}`;
  };

  const maxValue = 100;

  // Calculate risk levels
  const getRiskLevel = (camera: typeof cameraData[0]) => {
    const totalAlerts = camera.high + camera.medium + camera.low;
    const riskScore = (camera.high * 3 + camera.medium * 2 + camera.low * 1) / totalAlerts;
    return riskScore;
  };

  const mostDangerous = cameraData.reduce((prev, current) => 
    getRiskLevel(current) > getRiskLevel(prev) ? current : prev
  );

  const safest = cameraData.reduce((prev, current) => 
    getRiskLevel(current) < getRiskLevel(prev) ? current : prev
  );

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 transition-colors">
      <div className="flex items-center justify-between mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Alert Priority Distribution</h3>
        
        {/* Toggle Button */}
        <button
          onClick={() => setShowTimeAnalysis(!showTimeAnalysis)}
          className={`flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-all ${
            showTimeAnalysis
              ? 'bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-400 border border-purple-300 dark:border-purple-700'
              : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 border border-gray-300 dark:border-gray-600 hover:bg-gray-200 dark:hover:bg-gray-600'
          }`}
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          {showTimeAnalysis ? 'Show by Camera' : 'Show Time Analysis'}
        </button>
      </div>
      
      {showTimeAnalysis ? (
        // 24-Hour Timeline Analysis
        <>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">Alert occurrence patterns across 24-hour period</p>
          
          <div className="mb-6">
            <div className="flex items-end justify-between h-48 gap-1">
              {hourlyAlerts.map((item) => {
                const heightPercent = (item.count / maxHourlyAlerts) * 100;
                const isHovered = hoveredHour === item.hour;
                
                // Determine color based on alert count (red for high, yellow for medium, green for low)
                let barColor = 'bg-green-500 dark:bg-green-600';
                if (item.count > 20) barColor = 'bg-red-500 dark:bg-red-600';
                else if (item.count > 10) barColor = 'bg-yellow-500 dark:bg-yellow-600';
                
                return (
                  <div
                    key={item.hour}
                    className="flex-1 flex flex-col items-center justify-end h-full"
                    onMouseEnter={() => setHoveredHour(item.hour)}
                    onMouseLeave={() => setHoveredHour(null)}
                  >
                    <div className="relative w-full flex items-end justify-center h-full">
                      <div
                        className={`w-full ${barColor} rounded-t transition-all duration-700 ease-out cursor-pointer relative`}
                        style={{ 
                          height: animated ? `${heightPercent}%` : '0%',
                          transitionDelay: `${item.hour * 30}ms`,
                          transform: isHovered ? 'scaleY(1.05)' : 'scaleY(1)',
                          boxShadow: isHovered ? '0 4px 12px rgba(0, 0, 0, 0.3)' : 'none'
                        }}
                      >
                        {isHovered && (
                          <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 bg-gray-900 dark:bg-gray-700 text-white text-xs px-2 py-1 rounded whitespace-nowrap z-10">
                            {formatHour(item.hour)}: {item.count} alerts
                          </div>
                        )}
                      </div>
                    </div>
                    {item.hour % 3 === 0 && (
                      <div className="text-[10px] text-gray-600 dark:text-gray-400 mt-1 font-medium">
                        {formatHour(item.hour)}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>

          <div className="flex justify-center gap-4 mb-4 text-xs">
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-red-500 dark:bg-red-600 rounded" />
              <span className="text-gray-700 dark:text-gray-300">High Activity (&gt;20)</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-yellow-500 dark:bg-yellow-600 rounded" />
              <span className="text-gray-700 dark:text-gray-300">Medium (10-20)</span>
            </div>
            <div className="flex items-center gap-1">
              <div className="w-3 h-3 bg-green-500 dark:bg-green-600 rounded" />
              <span className="text-gray-700 dark:text-gray-300">Low Activity (&lt;10)</span>
            </div>
          </div>

          {/* Time-based Risk Assessment Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            {/* Critical Time Zone */}
            <div className="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 border-2 border-red-200 dark:border-red-800 rounded-lg p-4 transition-colors">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-red-500 dark:bg-red-600 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1">
                  <h4 className="text-sm font-bold text-red-900 dark:text-red-300 mb-1">Critical Time Period</h4>
                  <p className="text-sm text-red-800 dark:text-red-400">
                    Peak activity detected at <span className="font-semibold">{formatHour(peakHour.hour)}</span> with {peakHour.count} alerts recorded during evening hours
                  </p>
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-xs bg-red-200 dark:bg-red-900/40 text-red-900 dark:text-red-300 px-2 py-1 rounded-full font-medium">
                      6 PM - 8 PM High Risk
                    </span>
                    <span className="text-xs text-red-700 dark:text-red-400">
                      Enhanced surveillance recommended
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Safe Time Zone */}
            <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-2 border-green-200 dark:border-green-800 rounded-lg p-4 transition-colors">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-green-500 dark:bg-green-600 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1">
                  <h4 className="text-sm font-bold text-green-900 dark:text-green-300 mb-1">Safe Time Period</h4>
                  <p className="text-sm text-green-800 dark:text-green-400">
                    Minimal activity at <span className="font-semibold">{formatHour(safestHour.hour)}</span> with only {safestHour.count} alert{safestHour.count !== 1 ? 's' : ''} during late night hours
                  </p>
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-xs bg-green-200 dark:bg-green-900/40 text-green-900 dark:text-green-300 px-2 py-1 rounded-full font-medium">
                      2 AM - 5 AM Low Risk
                    </span>
                    <span className="text-xs text-green-700 dark:text-green-400">
                      Optimal maintenance window
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      ) : (
        // Camera-based Stacked Bar Chart
        <>
          <div className="flex items-end justify-between h-64 mb-4">
            {cameraData.map((item, index) => {
              const highHeight = (item.high / maxValue) * 100;
              const mediumHeight = (item.medium / maxValue) * 100;
              const lowHeight = (item.low / maxValue) * 100;
              
              return (
                <div key={index} className="flex-1 flex flex-col items-center justify-end h-full px-2">
                  <div 
                    className="w-full flex flex-col items-center justify-end space-y-1 transition-all duration-300" 
                    style={{ height: '90%' }}
                  >
                    <div
                      className="w-full bg-red-500 dark:bg-red-600 rounded-t transition-all duration-1000 ease-out cursor-pointer hover:opacity-80 relative group"
                      style={{ 
                        height: animated ? `${highHeight}%` : '0%',
                        transitionDelay: `${index * 100}ms`
                      }}
                      onMouseEnter={() => setHoveredBar({ camera: item.label, priority: 'high' })}
                      onMouseLeave={() => setHoveredBar(null)}
                    >
                      {hoveredBar?.camera === item.label && hoveredBar?.priority === 'high' && (
                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 bg-gray-900 dark:bg-gray-700 text-white text-xs px-2 py-1 rounded whitespace-nowrap z-10">
                          High: {item.high}
                        </div>
                      )}
                    </div>
                    <div
                      className="w-full bg-yellow-500 dark:bg-yellow-600 transition-all duration-1000 ease-out cursor-pointer hover:opacity-80 relative group"
                      style={{ 
                        height: animated ? `${mediumHeight}%` : '0%',
                        transitionDelay: `${index * 100 + 200}ms`
                      }}
                      onMouseEnter={() => setHoveredBar({ camera: item.label, priority: 'medium' })}
                      onMouseLeave={() => setHoveredBar(null)}
                    >
                      {hoveredBar?.camera === item.label && hoveredBar?.priority === 'medium' && (
                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 bg-gray-900 dark:bg-gray-700 text-white text-xs px-2 py-1 rounded whitespace-nowrap z-10">
                          Medium: {item.medium}
                        </div>
                      )}
                    </div>
                    <div
                      className="w-full bg-green-500 dark:bg-green-600 transition-all duration-1000 ease-out cursor-pointer hover:opacity-80 relative group"
                      style={{ 
                        height: animated ? `${lowHeight}%` : '0%',
                        transitionDelay: `${index * 100 + 400}ms`
                      }}
                      onMouseEnter={() => setHoveredBar({ camera: item.label, priority: 'low' })}
                      onMouseLeave={() => setHoveredBar(null)}
                    >
                      {hoveredBar?.camera === item.label && hoveredBar?.priority === 'low' && (
                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 bg-gray-900 dark:bg-gray-700 text-white text-xs px-2 py-1 rounded whitespace-nowrap z-10">
                          Low: {item.low}
                        </div>
                      )}
                    </div>
                  </div>
                  <div className="text-center mt-2">
                    <div className="text-xs text-gray-600 dark:text-gray-400 font-medium">{item.label}</div>
                    <div className="text-xs text-gray-500 dark:text-gray-500">{item.location}</div>
                  </div>
                </div>
              );
            })}
          </div>

          <div className="flex justify-center gap-6 mb-4">
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-red-500 dark:bg-red-600 rounded" />
              <span className="text-xs text-gray-700 dark:text-gray-300">High</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-yellow-500 dark:bg-yellow-600 rounded" />
              <span className="text-xs text-gray-700 dark:text-gray-300">Medium</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-3 h-3 bg-green-500 dark:bg-green-600 rounded" />
              <span className="text-xs text-gray-700 dark:text-gray-300">Low</span>
            </div>
          </div>

          {/* Risk Assessment Cards */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mt-6">
            {/* Highest Risk Area */}
            <div className="bg-gradient-to-br from-red-50 to-red-100 dark:from-red-900/20 dark:to-red-800/20 border-2 border-red-200 dark:border-red-800 rounded-lg p-4 transition-colors">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-red-500 dark:bg-red-600 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1">
                  <h4 className="text-sm font-bold text-red-900 dark:text-red-300 mb-1">Critical Alert Zone</h4>
                  <p className="text-sm text-red-800 dark:text-red-400">
                    <span className="font-semibold">{mostDangerous.label} ({mostDangerous.location})</span> exhibits the highest risk profile with {mostDangerous.high} high-priority alerts detected
                  </p>
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-xs bg-red-200 dark:bg-red-900/40 text-red-900 dark:text-red-300 px-2 py-1 rounded-full font-medium">
                      {mostDangerous.high} High Priority
                    </span>
                    <span className="text-xs text-red-700 dark:text-red-400">
                      Requires immediate attention
                    </span>
                  </div>
                </div>
              </div>
            </div>

            {/* Lowest Risk Area */}
            <div className="bg-gradient-to-br from-green-50 to-green-100 dark:from-green-900/20 dark:to-green-800/20 border-2 border-green-200 dark:border-green-800 rounded-lg p-4 transition-colors">
              <div className="flex items-start gap-3">
                <div className="flex-shrink-0">
                  <div className="w-10 h-10 bg-green-500 dark:bg-green-600 rounded-full flex items-center justify-center">
                    <svg className="w-6 h-6 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <div className="flex-1">
                  <h4 className="text-sm font-bold text-green-900 dark:text-green-300 mb-1">Secure Perimeter</h4>
                  <p className="text-sm text-green-800 dark:text-green-400">
                    <span className="font-semibold">{safest.label} ({safest.location})</span> demonstrates optimal security status with only {safest.high} high-priority alerts recorded
                  </p>
                  <div className="mt-2 flex items-center gap-2">
                    <span className="text-xs bg-green-200 dark:bg-green-900/40 text-green-900 dark:text-green-300 px-2 py-1 rounded-full font-medium">
                      {safest.low} Low Priority
                    </span>
                    <span className="text-xs text-green-700 dark:text-green-400">
                      Maintaining stable conditions
                    </span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
}