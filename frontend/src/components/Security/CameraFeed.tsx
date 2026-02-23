import { useState } from 'react';

export interface Camera {
  id: string;
  name: string;
  location: string;
  status: 'active' | 'inactive';
  imageUrl: string;
}

interface CameraFeedProps {
  cameras: Camera[];
  selectedCamera: Camera;
  onSelectCamera: (camera: Camera) => void;
}

export default function CameraFeed({ cameras, selectedCamera, onSelectCamera }: CameraFeedProps) {
  const [layout, setLayout] = useState<'default' | 'grid'>('default');
  const [showLegend, setShowLegend] = useState(false);

  // ============================================
  // PLACEHOLDER IMAGE URLS - REPLACE THESE WITH YOUR ACTUAL CAMERA FEED URLS
  // ============================================
  // Example: 'https://your-server.com/camera-feed/cam-1.jpg'
  // Or use a streaming URL like: 'http://192.168.1.100:8080/video'
  // Leave empty ('') to show the default placeholder
  // ============================================
  
  const detections = [
    { id: 1, behavior: 'WALK', confidence: 92, x: 15, y: 25, width: 12, height: 35, color: 'rgb(34, 197, 94)' },
    { id: 2, behavior: 'STAND', confidence: 89, x: 42, y: 22, width: 11, height: 38, color: 'rgb(59, 130, 246)' },
    { id: 3, behavior: 'RUN', confidence: 86, x: 68, y: 28, width: 13, height: 32, color: 'rgb(234, 179, 8)' }
  ];

  // Behavior color legend
  const behaviorLegend = [
    { behavior: 'WALK', color: 'rgb(34, 197, 94)', bgColor: 'bg-green-500' },
    { behavior: 'STAND', color: 'rgb(59, 130, 246)', bgColor: 'bg-blue-500' },
    { behavior: 'RUN', color: 'rgb(234, 179, 8)', bgColor: 'bg-yellow-500' },
    { behavior: 'BEND', color: 'rgb(168, 85, 247)', bgColor: 'bg-purple-500' },
    { behavior: 'SIT', color: 'rgb(249, 115, 22)', bgColor: 'bg-orange-500' }
  ];

  return (
    <div className="space-y-4">
      {/* Layout Toggle */}
      <div className="flex items-center justify-between">
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Camera Views</h2>
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-600 dark:text-gray-400">Layout:</span>
          <button
            onClick={() => setLayout('default')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              layout === 'default'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1v-4z" />
            </svg>
          </button>
          <button
            onClick={() => setLayout('grid')}
            className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-colors ${
              layout === 'grid'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
            }`}
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1H5a1 1 0 01-1-1v-4zM14 15a1 1 0 011-1h4a1 1 0 011 1v4a1 1 0 01-1 1h-4a1 1 0 01-1-1v-4z" />
            </svg>
          </button>
        </div>
      </div>

      {layout === 'default' ? (
        // Default Layout: 1 Large + 3 Small
        <>
          {/* Main Camera Feed */}
          <div className="bg-white dark:bg-gray-800 dark:bg-gray-800 rounded-lg shadow-sm p-4">
            <div className="flex items-center justify-between mb-3">
              <div className="flex items-center gap-2">
                <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="4"/>
                </svg>
                <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{selectedCamera.name}</span>
                <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs font-medium rounded-full flex items-center gap-1">
                  <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="4"/>
                  </svg>
                  {selectedCamera.status === 'active' ? 'Active' : 'Inactive'}
                </span>
              </div>
            </div>

            <div className="relative bg-gray-900 rounded-lg overflow-hidden" style={{ aspectRatio: '16/9' }}>
              <div className="absolute top-4 left-4 bg-red-600 text-white px-2 py-1 rounded text-xs font-bold z-10">
                LIVE
              </div>
              
              <div className="absolute top-4 right-4 text-white text-sm font-mono z-10">
                {new Date().toLocaleTimeString()}
              </div>

              {/* Behavior Legend Info Icon */}
              <div 
                className="absolute bottom-4 left-4 z-20"
                onMouseEnter={() => setShowLegend(true)}
                onMouseLeave={() => setShowLegend(false)}
              >
                <div className="relative">
                  <div className="w-8 h-8 bg-gray-800 dark:bg-gray-700 bg-opacity-80 rounded-full flex items-center justify-center cursor-help hover:bg-opacity-100 transition-all">
                    <svg className="w-5 h-5 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                  
                  {/* Legend Tooltip */}
                  {showLegend && (
                    <div className="absolute bottom-full left-0 mb-2 bg-gray-900 dark:bg-gray-800 text-white rounded-lg shadow-xl p-3 min-w-[200px] border border-gray-700">
                      <p className="text-xs font-semibold mb-2 text-gray-300">Behavior Color Legend</p>
                      <div className="space-y-1.5">
                        {behaviorLegend.map((item) => (
                          <div key={item.behavior} className="flex items-center gap-2">
                            <div className={`w-3 h-3 ${item.bgColor} rounded`}></div>
                            <span className="text-xs text-gray-200">{item.behavior}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Placeholder Image or Detection Overlay */}
              {selectedCamera.imageUrl ? (
                <img 
                  src={selectedCamera.imageUrl} 
                  alt={selectedCamera.name}
                  className="w-full h-full object-cover"
                />
              ) : (
                <div className="w-full h-full flex items-center justify-center bg-gray-800">
                  <div className="text-center">
                    <svg className="w-16 h-16 text-gray-600 dark:text-gray-400 mx-auto mb-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    <p className="text-gray-400 text-sm">Camera Feed Placeholder</p>
                    <p className="text-gray-500 dark:text-gray-400 text-xs mt-1">Set imageUrl to display feed</p>
                  </div>
                </div>
              )}

              {/* Detection Overlays - only show if no image */}
              {!selectedCamera.imageUrl && (
                <div className="absolute inset-0">
                  {detections.map((detection) => (
                    <div
                      key={detection.id}
                      className="absolute"
                      style={{
                        left: `${detection.x}%`,
                        top: `${detection.y}%`,
                        width: `${detection.width}%`,
                        height: `${detection.height}%`,
                        border: `3px solid ${detection.color}`,
                        borderRadius: '4px'
                      }}
                    >
                      <div
                        className="absolute -top-7 left-0 px-2 py-0.5 text-xs font-bold text-white rounded"
                        style={{ backgroundColor: detection.color }}
                      >
                        {detection.behavior} ({detection.confidence}%)
                      </div>
                    </div>
                  ))}
                </div>
              )}

              <div className="absolute bottom-4 left-4 flex gap-2 z-10">
                <span className="bg-green-600 text-white px-2 py-1 rounded text-xs font-bold">
                  HD
                </span>
                <span className="bg-blue-600 text-white px-2 py-1 rounded text-xs font-bold">
                  AI Active
                </span>
              </div>

              <div className="absolute bottom-4 right-4 text-white text-xs font-mono z-10">
                <span className="opacity-75">Camera Feed</span> 1920x1080 @ 30fps
              </div>
            </div>
          </div>

          {/* Camera Thumbnails */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {cameras.filter(cam => cam.id !== selectedCamera.id).slice(0, 3).map((camera) => (
              <button
                key={camera.id}
                onClick={() => onSelectCamera(camera)}
                className="bg-white dark:bg-gray-800 dark:bg-gray-800 rounded-lg shadow-sm p-3 hover:shadow-md transition text-left"
              >
                <div className="relative bg-gray-900 rounded overflow-hidden mb-2" style={{ aspectRatio: '16/9' }}>
                  <div className="absolute top-2 left-2 bg-red-600 text-white px-1.5 py-0.5 rounded text-[10px] font-bold z-10">
                    LIVE
                  </div>
                  
                  {camera.imageUrl ? (
                    <img 
                      src={camera.imageUrl} 
                      alt={camera.name}
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="w-full h-full flex items-center justify-center bg-gray-800">
                      <svg className="w-8 h-8 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                      </svg>
                    </div>
                  )}

                  <div className="absolute bottom-2 right-2 text-white text-[10px] font-mono opacity-75 z-10">
                    1920x1080 @ 30fps
                  </div>
                </div>

                <div className="flex items-center justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-1.5">
                      <svg className={`w-3 h-3 ${camera.status === 'active' ? 'text-green-500' : 'text-gray-400'}`} fill="currentColor" viewBox="0 0 24 24">
                        <circle cx="12" cy="12" r="4"/>
                      </svg>
                      <p className="text-xs font-medium text-gray-900 dark:text-white">{camera.name}</p>
                    </div>
                    <p className="text-[10px] text-gray-500 dark:text-gray-400 mt-0.5">{camera.location}</p>
                  </div>
                </div>
              </button>
            ))}
          </div>
        </>
      ) : (
        // 2x2 Grid Layout
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {cameras.slice(0, 4).map((camera) => (
            <button
              key={camera.id}
              onClick={() => onSelectCamera(camera)}
              className={`bg-white dark:bg-gray-800 rounded-lg shadow-sm p-4 hover:shadow-md transition text-left ${
                selectedCamera.id === camera.id ? 'ring-2 ring-blue-500' : ''
              }`}
            >
              <div className="flex items-center justify-between mb-3">
                <div className="flex items-center gap-2">
                  <svg className="w-4 h-4 text-red-500" fill="currentColor" viewBox="0 0 24 24">
                    <circle cx="12" cy="12" r="4"/>
                  </svg>
                  <span className="text-sm font-medium text-gray-700 dark:text-gray-300">{camera.name}</span>
                  <span className={`px-2 py-0.5 ${camera.status === 'active' ? 'bg-green-100 text-green-700' : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'} text-xs font-medium rounded-full flex items-center gap-1`}>
                    <svg className="w-3 h-3" fill="currentColor" viewBox="0 0 24 24">
                      <circle cx="12" cy="12" r="4"/>
                    </svg>
                    {camera.status === 'active' ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>

              <div className="relative bg-gray-900 rounded-lg overflow-hidden" style={{ aspectRatio: '16/9' }}>
                <div className="absolute top-2 left-2 bg-red-600 text-white px-2 py-1 rounded text-xs font-bold z-10">
                  LIVE
                </div>
                
                {camera.imageUrl ? (
                  <img 
                    src={camera.imageUrl} 
                    alt={camera.name}
                    className="w-full h-full object-cover"
                  />
                ) : (
                  <div className="w-full h-full flex items-center justify-center bg-gray-800">
                    <svg className="w-12 h-12 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                  </div>
                )}

                <div className="absolute bottom-2 right-2 text-white text-xs font-mono opacity-75 z-10">
                  1920x1080 @ 30fps
                </div>
              </div>

              <div className="mt-2 text-xs text-gray-500 dark:text-gray-400">{camera.location}</div>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}