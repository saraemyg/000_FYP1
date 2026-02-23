import NavigationBar from '../components/Security/NavigationBar';
import MetricsSummary from '../components/Performance/MetricsSummary';
import PerformanceGraphs from '../components/Performance/PerformanceGraphs';
import PipelineStatus from '../components/Performance/PipelineStatus';

interface PerformanceDashboardProps {
  onLogout: () => void;
}

export default function PerformanceDashboard({ onLogout }: PerformanceDashboardProps) {
  const handleExportCSV = () => {
    // Generate mock performance data for CSV export
    const headers = [
      'Timestamp',
      'Avg FPS',
      'Cam A Detections',
      'Cam B Detections',
      'Cam C Detections',
      'Cam D Detections',
      'CPU Usage (%)',
      'RAM Usage (%)',
      'GPU Usage (%)',
      'VRAM Usage (%)',
      'Detection Accuracy (%)',
      'Segmentation Accuracy (%)',
      'Behavior Accuracy (%)'
    ];

    // Generate 24 hours of data (one row per hour)
    const mockData = Array.from({ length: 24 }, (_, i) => {
      const hour = i.toString().padStart(2, '0');
      return [
        `2024-02-12 ${hour}:00:00`,
        (25 + Math.random() * 10).toFixed(1),  // FPS
        Math.floor(30 + Math.random() * 50),    // Cam A
        Math.floor(25 + Math.random() * 40),    // Cam B
        Math.floor(20 + Math.random() * 35),    // Cam C
        Math.floor(35 + Math.random() * 60),    // Cam D
        (55 + Math.random() * 25).toFixed(1),   // CPU
        (60 + Math.random() * 15).toFixed(1),   // RAM
        (65 + Math.random() * 20).toFixed(1),   // GPU
        (68 + Math.random() * 12).toFixed(1),   // VRAM
        (91 + Math.random() * 8).toFixed(1),    // Detection
        (89 + Math.random() * 9).toFixed(1),    // Segmentation
        (93 + Math.random() * 6).toFixed(1)     // Behavior
      ];
    });

    const csvContent = [
      headers.join(','),
      ...mockData.map(row => row.join(','))
    ].join('\n');

    // Create and download CSV file
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);
    link.setAttribute('href', url);
    link.setAttribute('download', `performance-metrics-${new Date().toISOString().split('T')[0]}.csv`);
    link.style.display = 'none';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      <NavigationBar onLogout={onLogout} />
      
      <div className="max-w-[1920px] mx-auto p-6">
        <div className="flex items-center justify-between mb-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Performance Metrics</h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              System performance monitoring and model accuracy tracking
            </p>
          </div>
          
          {/* CSV Export Button */}
          <button
            onClick={handleExportCSV}
            className="flex items-center gap-2 px-4 py-2 bg-blue-600 dark:bg-blue-500 text-white rounded-lg hover:bg-blue-700 dark:hover:bg-blue-600 transition-colors text-sm font-medium"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Export CSV
          </button>
        </div>

        {/* Metrics Summary Cards */}
        <div className="mb-6">
          <MetricsSummary />
        </div>

        {/* Performance Graphs */}
        <div className="mb-6">
          <PerformanceGraphs />
        </div>

        {/* Pipeline Status */}
        <PipelineStatus />
      </div>
    </div>
  );
}