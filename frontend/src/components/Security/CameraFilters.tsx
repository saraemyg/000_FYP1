import { useState } from 'react';

interface CameraFiltersProps {
  cameras?: Array<{ id: string; name: string; location: string }>;
  onFilterChange?: (cameraName: string) => void;
}

export default function CameraFilters({ cameras = [], onFilterChange = () => {} }: CameraFiltersProps) {
  const [selectedCamera, setSelectedCamera] = useState('All Cameras');
  const [dateFrom, setDateFrom] = useState('');
  const [dateTo, setDateTo] = useState('');
  const [timeFrom, setTimeFrom] = useState('');
  const [timeTo, setTimeTo] = useState('');

  const handleCameraChange = (cameraName: string) => {
    setSelectedCamera(cameraName);
    onFilterChange(cameraName);
  };

  const handleApply = () => {
    console.log('Filters applied:', { selectedCamera, dateFrom, dateTo, timeFrom, timeTo });
  };

  const handleReset = () => {
    setSelectedCamera('All Cameras');
    setDateFrom('');
    setDateTo('');
    setTimeFrom('');
    setTimeTo('');
    onFilterChange('All Cameras');
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6 transition-colors">
      <div className="flex items-center gap-2 mb-4">
        <svg className="w-5 h-5 text-gray-600 dark:text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
        </svg>
        <h2 className="text-lg font-semibold text-gray-900 dark:text-white">Search & Filter Cameras</h2>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-6 gap-4">
        <div className="md:col-span-2">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
            <span className="flex items-center gap-1">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
              </svg>
              Camera
            </span>
          </label>
          <select
            value={selectedCamera}
            onChange={(e) => handleCameraChange(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white transition-colors"
          >
            <option value="All Cameras">All Cameras</option>
            {cameras.map((camera) => (
              <option key={camera.id} value={camera.name}>
                {camera.name}
              </option>
            ))}
          </select>
        </div>

        <div className="md:col-span-1">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Date From</label>
          <input
            type="date"
            value={dateFrom}
            onChange={(e) => setDateFrom(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white transition-colors"
          />
        </div>

        <div className="md:col-span-1">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Date To</label>
          <input
            type="date"
            value={dateTo}
            onChange={(e) => setDateTo(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white transition-colors"
          />
        </div>

        <div className="md:col-span-1">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Time From</label>
          <input
            type="time"
            value={timeFrom}
            onChange={(e) => setTimeFrom(e.target.value)}
            className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white transition-colors"
          />
        </div>

        <div className="md:col-span-1">
          <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Time To</label>
          <div className="flex gap-2">
            <input
              type="time"
              value={timeTo}
              onChange={(e) => setTimeTo(e.target.value)}
              className="flex-1 px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-700 dark:text-white transition-colors"
            />
          </div>
        </div>
      </div>

      <div className="mt-4 flex items-center justify-between">
        <p className="text-sm text-gray-500 dark:text-gray-400">
          {selectedCamera === 'All Cameras' ? `Showing all ${cameras.length} cameras` : `Filtered: ${selectedCamera}`}
        </p>
        <div className="flex gap-2">
          <button
            onClick={handleReset}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition"
          >
            Reset
          </button>
          <button
            onClick={handleApply}
            className="bg-blue-600 dark:bg-blue-500 text-white px-4 py-2 rounded-md hover:bg-blue-700 dark:hover:bg-blue-600 transition text-sm font-medium"
          >
            Apply Filters
          </button>
        </div>
      </div>
    </div>
  );
}