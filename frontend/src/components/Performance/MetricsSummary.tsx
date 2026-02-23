export default function MetricsSummary() {
  const metrics = [
    {
      icon: (
        <svg className="w-8 h-8 text-blue-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
      ),
      value: '4',
      label: 'Active Cameras',
      subtitle: 'All operational',
      bgColor: 'bg-blue-50',
      borderColor: 'border-blue-100'
    },
    {
      icon: (
        <svg className="w-8 h-8 text-green-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
        </svg>
      ),
      value: '24,538',
      label: 'Frames Analyzed',
      subtitle: 'Last 24 hours',
      badge: '+12%',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-100'
    },
    {
      icon: (
        <svg className="w-8 h-8 text-yellow-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
        </svg>
      ),
      value: '17.8',
      label: 'Average FPS',
      subtitle: 'Target: ≥15 FPS',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-100'
    },
    {
      icon: (
        <svg className="w-8 h-8 text-purple-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      value: '2.3ms',
      label: 'Processing Time',
      subtitle: 'Total processing',
      bgColor: 'bg-purple-50',
      borderColor: 'border-purple-100'
    },
    {
      icon: (
        <svg className="w-8 h-8 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
      ),
      value: 'Optimal',
      label: 'System Health',
      subtitle: 'All modules operating',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-100',
      statusColor: 'text-green-600'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
      {metrics.map((metric, index) => (
        <div
          key={index}
          className={`${metric.bgColor} border ${metric.borderColor} rounded-lg p-6`}
        >
          <div className="flex justify-center mb-3">{metric.icon}</div>
          <div className="text-center">
            <div className={`text-3xl font-bold ${metric.statusColor || 'text-gray-900'} mb-1 flex items-center justify-center gap-2`}>
              {metric.value}
              {metric.badge && (
                <span className="text-xs font-medium text-green-600 bg-green-100 px-2 py-0.5 rounded">
                  {metric.badge}
                </span>
              )}
            </div>
            <div className="text-sm font-medium text-gray-700">{metric.label}</div>
            <div className="text-xs text-gray-500 mt-1">{metric.subtitle}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
