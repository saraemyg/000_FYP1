import { useState } from 'react';

export default function PerformanceGraphs() {
  const [showPerBehavior, setShowPerBehavior] = useState(false);
  const [hoveredIndex, setHoveredIndex] = useState<number | null>(null);
  const [hoveredFps, setHoveredFps] = useState<{ index: number; point: { time: string; value: number } } | null>(null);

  // 24-hour FPS data - Average FPS per hour (with some critical drops)
  const fpsData = [
    { time: '00:00', value: 28.2 },
    { time: '01:00', value: 29.1 },
    { time: '02:00', value: 28.8 },
    { time: '03:00', value: 29.5 },
    { time: '04:00', value: 28.4 },
    { time: '05:00', value: 27.8 },
    { time: '06:00', value: 26.5 },
    { time: '07:00', value: 24.2 },
    { time: '08:00', value: 14.8 }, // CRITICAL - Below 15 FPS
    { time: '09:00', value: 13.5 }, // CRITICAL - Below 15 FPS
    { time: '10:00', value: 16.1 },
    { time: '11:00', value: 18.3 },
    { time: '12:00', value: 20.2 },
    { time: '13:00', value: 19.8 },
    { time: '14:00', value: 18.4 },
    { time: '15:00', value: 17.9 },
    { time: '16:00', value: 16.7 },
    { time: '17:00', value: 14.1 }, // CRITICAL - Below 15 FPS
    { time: '18:00', value: 13.8 }, // CRITICAL - Below 15 FPS (Peak usage)
    { time: '19:00', value: 15.2 },
    { time: '20:00', value: 17.6 },
    { time: '21:00', value: 21.1 },
    { time: '22:00', value: 24.5 },
    { time: '23:00', value: 26.9 }
  ];

  // Detection data with behavior breakdown per camera per hour
  const detectionsData = [
    { 
      camera: 'Cam A', 
      total: 145,
      WALK: 65,
      STAND: 42,
      RUN: 15,
      BEND: 18,
      SIT: 5
    },
    { 
      camera: 'Cam B', 
      total: 128,
      WALK: 58,
      STAND: 38,
      RUN: 12,
      BEND: 15,
      SIT: 5
    },
    { 
      camera: 'Cam C', 
      total: 98,
      WALK: 45,
      STAND: 28,
      RUN: 8,
      BEND: 12,
      SIT: 5
    },
    { 
      camera: 'Cam D', 
      total: 167,
      WALK: 75,
      STAND: 52,
      RUN: 18,
      BEND: 17,
      SIT: 5
    }
  ];

  const behaviorColors = {
    WALK: '#22c55e',
    STAND: '#3b82f6',
    RUN: '#eab308',
    BEND: '#a855f7',
    SIT: '#f59e0b'
  };

  const maxDetections = 200;

  return (
    <div className="grid grid-cols-1 xl:grid-cols-5 gap-6">
      {/* FPS Over Time - 2 columns */}
      <div className="xl:col-span-2 bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 transition-colors">
        <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-2">FPS Over Time (24 Hours)</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">Average FPS per hour - System status for the day</p>
        
        <div className="h-48 relative">
          {/* Grid lines */}
          <div className="absolute inset-0 flex flex-col justify-between">
            {[35, 30, 25, 20, 15, 10, 5, 0].map((val) => (
              <div key={val} className="flex items-center">
                <span className="text-xs text-gray-400 dark:text-gray-500 w-6">{val}</span>
                <div className="flex-1 border-t border-gray-200 dark:border-gray-700 ml-2"></div>
              </div>
            ))}
          </div>
          
          {/* Line graph */}
          <svg className="absolute inset-0 ml-8" viewBox="0 0 400 192" preserveAspectRatio="none">
            {/* Target line at 20 FPS (recommended minimum) */}
            <line
              x1="0"
              y1={192 - (20 / 35) * 192}
              x2="400"
              y2={192 - (20 / 35) * 192}
              stroke="#22c55e"
              strokeWidth="1"
              strokeDasharray="4 4"
              opacity="0.5"
            />
            
            {/* FPS line segments with color based on value */}
            {fpsData.map((point, index) => {
              if (index === fpsData.length - 1) return null;
              
              const x1 = (index / (fpsData.length - 1)) * 400;
              const y1 = 192 - (point.value / 35) * 192;
              const x2 = ((index + 1) / (fpsData.length - 1)) * 400;
              const y2 = 192 - (fpsData[index + 1].value / 35) * 192;
              
              // Critical: Red if below 15 FPS, Yellow if below 20 FPS, Blue if normal
              const isCritical = point.value < 15 || fpsData[index + 1].value < 15;
              const isWarning = !isCritical && (point.value < 20 || fpsData[index + 1].value < 20);
              
              let strokeColor = '#3b82f6'; // Blue (normal)
              if (isCritical) strokeColor = '#ef4444'; // Red (critical)
              else if (isWarning) strokeColor = '#eab308'; // Yellow (warning)
              
              return (
                <line
                  key={index}
                  x1={x1}
                  y1={y1}
                  x2={x2}
                  y2={y2}
                  stroke={strokeColor}
                  strokeWidth="2"
                />
              );
            })}
            
            {/* Data points */}
            {fpsData.map((point, index) => {
              const x = (index / (fpsData.length - 1)) * 400;
              const y = 192 - (point.value / 35) * 192;
              const isHovered = hoveredFps?.index === index;
              const isCritical = point.value < 15;
              const isWarning = !isCritical && point.value < 20;
              
              return (
                <g key={index}>
                  <circle
                    cx={x}
                    cy={y}
                    r={isHovered ? "6" : "4"}
                    fill={isCritical ? '#ef4444' : isWarning ? '#eab308' : '#3b82f6'}
                    className="cursor-pointer transition-all duration-200"
                    onMouseEnter={() => setHoveredFps({ index, point })}
                    onMouseLeave={() => setHoveredFps(null)}
                    style={{
                      filter: isHovered ? `drop-shadow(0 0 4px ${isCritical ? 'rgba(239, 68, 68, 0.6)' : isWarning ? 'rgba(234, 179, 8, 0.6)' : 'rgba(59, 130, 246, 0.6)'})` : 'none'
                    }}
                  />
                </g>
              );
            })}
          </svg>
        </div>
        
        {/* X-axis labels */}
        <div className="flex justify-between mt-2 ml-8">
          {fpsData.filter((_, i) => i % 2 === 0).map((point, index) => (
            <span key={index} className="text-xs text-gray-600 dark:text-gray-400">{point.time}</span>
          ))}
        </div>
        
        {/* Hover value display below graph */}
        <div className="mt-3 h-6 ml-8">
          {hoveredFps && (
            <div className={`inline-flex items-center gap-2 px-3 py-1 rounded text-sm font-medium animate-fadeIn ${
              hoveredFps.point.value < 15
                ? 'bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-400' 
                : hoveredFps.point.value < 20
                ? 'bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400'
                : 'bg-blue-100 dark:bg-blue-900/30 text-blue-700 dark:text-blue-400'
            }`}>
              <span>{hoveredFps.point.time}</span>
              <span className="font-bold">{hoveredFps.point.value} FPS</span>
              {hoveredFps.point.value < 15 && (
                <span className="text-xs font-bold">🔴 CRITICAL</span>
              )}
              {hoveredFps.point.value >= 15 && hoveredFps.point.value < 20 && (
                <span className="text-xs">⚠️ Below Optimal</span>
              )}
            </div>
          )}
        </div>
        
        <div className="mt-2 flex items-center justify-between">
          <span className="text-xs text-gray-600 dark:text-gray-400">Average: 19.5 FPS</span>
          <span className="px-2 py-1 bg-yellow-100 dark:bg-yellow-900/30 text-yellow-700 dark:text-yellow-400 rounded text-xs font-medium">
            Performance Warning
          </span>
        </div>
      </div>

      {/* Detections Per Hour - 2 columns */}
      <div className="xl:col-span-2 bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-base font-semibold text-gray-900 dark:text-white">Detections Per Hour</h3>
          
          {/* Toggle Switch */}
          <div className="flex items-center gap-2">
            <span className={`text-xs ${!showPerBehavior ? 'text-gray-900 dark:text-white font-medium' : 'text-gray-500 dark:text-gray-400'}`}>
              Overall
            </span>
            <button
              onClick={() => setShowPerBehavior(!showPerBehavior)}
              className="relative inline-flex h-5 w-9 items-center rounded-full transition-colors focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
              style={{ backgroundColor: showPerBehavior ? '#3b82f6' : '#d1d5db' }}
            >
              <span
                className={`inline-block h-3 w-3 transform rounded-full bg-white transition-transform ${
                  showPerBehavior ? 'translate-x-5' : 'translate-x-1'
                }`}
              />
            </button>
            <span className={`text-xs ${showPerBehavior ? 'text-gray-900 dark:text-white font-medium' : 'text-gray-500 dark:text-gray-400'}`}>
              Per Behavior
            </span>
          </div>
        </div>
        <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">Workload Monitoring by Camera</p>
        
        <div className="h-48 flex items-end justify-around gap-4 px-2">
          {detectionsData.map((point, index) => {
            const isHovered = hoveredIndex === index;
            
            if (showPerBehavior) {
              // Stacked bar chart for behaviors
              const behaviors: Array<keyof typeof behaviorColors> = ['SIT', 'BEND', 'RUN', 'STAND', 'WALK'];
              
              return (
                <div 
                  key={index} 
                  className="flex flex-col items-center"
                  style={{ width: '60px' }}
                  onMouseEnter={() => setHoveredIndex(index)}
                  onMouseLeave={() => setHoveredIndex(null)}
                >
                  <div className="w-full h-48 flex flex-col-reverse relative">
                    {behaviors.map((behavior) => {
                      const value = point[behavior];
                      const heightPercent = (value / maxDetections) * 100;
                      
                      return (
                        <div
                          key={behavior}
                          className="w-full transition-all duration-300 cursor-pointer"
                          style={{ 
                            height: `${heightPercent}%`,
                            backgroundColor: behaviorColors[behavior],
                            opacity: isHovered ? 0.9 : 1,
                            transform: isHovered ? 'scaleX(1.1)' : 'scaleX(1)'
                          }}
                        />
                      );
                    })}
                    
                    {/* Hover tooltip */}
                    {isHovered && (
                      <div className="absolute -top-2 left-1/2 transform -translate-x-1/2 -translate-y-full bg-gray-900 text-white text-xs px-3 py-2 rounded shadow-lg whitespace-nowrap z-10">
                        <div className="font-semibold mb-1">{point.camera}</div>
                        {['WALK', 'STAND', 'RUN', 'BEND', 'SIT'].map((behavior) => (
                          <div key={behavior} className="flex items-center justify-between gap-2">
                            <div className="flex items-center gap-1">
                              <div 
                                className="w-2 h-2 rounded-full" 
                                style={{ backgroundColor: behaviorColors[behavior as keyof typeof behaviorColors] }}
                              />
                              <span>{behavior}:</span>
                            </div>
                            <span className="font-medium">{point[behavior as keyof typeof point]}</span>
                          </div>
                        ))}
                        <div className="border-t border-gray-700 mt-1 pt-1 font-semibold">
                          Total: {point.total}
                        </div>
                      </div>
                    )}
                  </div>
                  <span className="text-xs text-gray-600 dark:text-gray-400 mt-2 font-medium">{point.camera}</span>
                </div>
              );
            } else {
              // Single bar for total
              const heightPercent = (point.total / maxDetections) * 100;
              
              return (
                <div 
                  key={index} 
                  className="flex flex-col items-center"
                  style={{ width: '60px' }}
                  onMouseEnter={() => setHoveredIndex(index)}
                  onMouseLeave={() => setHoveredIndex(null)}
                >
                  <div className="w-full h-48 flex items-end">
                    <div
                      className="w-full bg-blue-600 rounded-t transition-all duration-300 cursor-pointer relative"
                      style={{ 
                        height: `${heightPercent}%`,
                        transform: isHovered ? 'scaleY(1.05) scaleX(1.1)' : 'scaleY(1) scaleX(1)',
                        boxShadow: isHovered ? '0 4px 12px rgba(59, 130, 246, 0.4)' : 'none'
                      }}
                    >
                      {/* Hover tooltip */}
                      {isHovered && (
                        <div className="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 bg-gray-900 text-white text-xs px-3 py-2 rounded shadow-lg whitespace-nowrap z-10">
                          <div className="font-semibold">{point.camera}</div>
                          <div className="text-center">Total: <span className="font-bold">{point.total}</span> detections</div>
                        </div>
                      )}
                    </div>
                  </div>
                  <span className="text-xs text-gray-600 dark:text-gray-400 mt-2 font-medium">{point.camera}</span>
                </div>
              );
            }
          })}
        </div>
        
        {showPerBehavior && (
          <div className="mt-4 flex flex-wrap gap-3 justify-center">
            {Object.entries(behaviorColors).map(([behavior, color]) => (
              <div key={behavior} className="flex items-center gap-1">
                <div className="w-3 h-3 rounded" style={{ backgroundColor: color }} />
                <span className="text-xs text-gray-700 dark:text-gray-300 font-medium">{behavior}</span>
              </div>
            ))}
          </div>
        )}
        
        <div className="mt-4 flex items-center justify-between">
          <span className="text-xs text-gray-600 dark:text-gray-400">Average: 135 detections/hour</span>
          <span className="text-xs text-gray-600 dark:text-gray-400">Peak: 167 (Cam D)</span>
        </div>
      </div>

      {/* Resource Consumption - 1 column with modern design */}
      <div className="xl:col-span-1 bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 border border-gray-200 dark:border-gray-700 transition-colors">
        <h3 className="text-base font-semibold text-gray-900 dark:text-white mb-1">System Resources</h3>
        <p className="text-xs text-gray-500 dark:text-gray-400 mb-4">Hardware utilization monitoring</p>
        
        {/* GPU Card */}
        <div className="bg-gradient-to-br from-purple-50 to-purple-100 dark:from-purple-900/20 dark:to-purple-800/20 border border-purple-200 dark:border-purple-700 rounded-lg p-4 mb-4">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-8 h-8 bg-purple-500 dark:bg-purple-600 rounded-lg flex items-center justify-center">
              <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 3v2m6-2v2M9 19v2m6-2v2M5 9H3m2 6H3m18-6h-2m2 6h-2M7 19h10a2 2 0 002-2V7a2 2 0 00-2-2H7a2 2 0 00-2 2v10a2 2 0 002 2zM9 9h6v6H9V9z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-bold text-gray-900 dark:text-white">RTX 5060 Ti</p>
              <p className="text-xs text-gray-600 dark:text-gray-400">CUDA 8.9</p>
            </div>
          </div>
        </div>

        {/* RAM Usage */}
        <div className="mb-4">
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 bg-blue-100 dark:bg-blue-900/30 rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4 text-blue-600 dark:text-blue-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M4 4h16v2H4V4zm0 4h16v2H4V8zm0 4h16v2H4v-2zm0 4h16v2H4v-2z"/>
                </svg>
              </div>
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">RAM Usage</span>
            </div>
            <span className="text-sm font-bold text-gray-900 dark:text-white">65%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 overflow-hidden">
            <div className="bg-gradient-to-r from-blue-500 to-blue-600 h-2.5 rounded-full transition-all duration-500" style={{ width: '65%' }} />
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">13 GB / 20 GB</p>
        </div>

        {/* VRAM Usage */}
        <div>
          <div className="flex items-center justify-between mb-2">
            <div className="flex items-center gap-2">
              <div className="w-7 h-7 bg-purple-100 dark:bg-purple-900/30 rounded-lg flex items-center justify-center">
                <svg className="w-4 h-4 text-purple-600 dark:text-purple-400" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20 4H4c-1.11 0-1.99.89-1.99 2L2 18c0 1.11.89 2 2 2h16c1.11 0 2-.89 2-2V6c0-1.11-.89-2-2-2zm0 14H4v-6h16v6zm0-10H4V6h16v2z"/>
                </svg>
              </div>
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300">VRAM Usage</span>
            </div>
            <span className="text-sm font-bold text-gray-900 dark:text-white">72%</span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2.5 overflow-hidden">
            <div className="bg-gradient-to-r from-purple-500 to-purple-600 h-2.5 rounded-full transition-all duration-500" style={{ width: '72%' }} />
          </div>
          <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">5.8 GB / 8 GB</p>
        </div>

        {/* Status Badge */}
        <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
          <div className="flex items-center justify-between">
            <span className="text-xs text-gray-600 dark:text-gray-400">System Status</span>
            <span className="px-2.5 py-1 bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-400 rounded-full text-xs font-medium flex items-center gap-1">
              <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                <circle cx="12" cy="12" r="4"/>
              </svg>
              Healthy
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}