export default function PipelineStatus() {
  const pipeline = [
    {
      name: 'Detection',
      fullName: 'YOLO11n-Pose',
      status: 'Operating',
      queueDepth: 0,
      statusColor: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      metrics: [
        { label: 'Precision', value: '91.8%' },
        { label: 'Recall', value: '86.5%' },
        { label: 'mAP', value: '89.2%' }
      ],
      color: 'text-blue-600'
    },
    {
      name: 'Segmentation',
      fullName: 'DeepLabv3+',
      status: 'Operating',
      queueDepth: 0,
      statusColor: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      metrics: [
        { label: 'Precision', value: '88.3%' },
        { label: 'Recall', value: '85.7%' },
        { label: 'mAP', value: '86.8%' }
      ],
      color: 'text-green-600'
    },
    {
      name: 'Behavior Recognition',
      fullName: 'MLP Classifier',
      status: 'Operating',
      queueDepth: 1,
      statusColor: 'text-green-600',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      metrics: [
        { label: 'Precision', value: '85.2%' },
        { label: 'Recall', value: '82.1%' },
        { label: 'mAP', value: '83.4%' }
      ],
      color: 'text-purple-600'
    }
  ];

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
      <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Processing Pipeline Status</h3>
      <p className="text-sm text-gray-500 dark:text-gray-400 mb-6">Real-time monitoring of processing modules and performance metrics</p>
      
      {/* Pipeline Flowchart */}
      <div className="mb-6">
        <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Component Status & Queue Depth</h4>
        <div className="flex items-center gap-3">
          {pipeline.map((component, index) => (
            <div key={index} className="flex items-center flex-1">
              {/* Component Card */}
              <div className={`${component.bgColor} border ${component.borderColor} rounded-lg p-4 w-full transition-all duration-300 hover:shadow-md`}>
                <div className="flex items-start justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <svg className="w-5 h-5 text-green-600 flex-shrink-0" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/>
                    </svg>
                    <div>
                      <p className="text-sm font-bold text-gray-900 dark:text-white">{component.name}</p>
                      <p className="text-xs text-gray-600 dark:text-gray-400">({component.fullName})</p>
                    </div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between mt-3">
                  <div className="text-xs text-gray-600 dark:text-gray-400">
                    Queue: <span className="font-semibold text-gray-900 dark:text-white">{component.queueDepth}</span>
                  </div>
                  <span className={`px-2 py-1 ${component.bgColor} ${component.statusColor} rounded-full text-xs font-semibold border ${component.borderColor}`}>
                    {component.status}
                  </span>
                </div>
              </div>
              
              {/* Arrow between components */}
              {index < pipeline.length - 1 && (
                <div className="flex items-center justify-center px-2">
                  <svg className="w-6 h-6 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                  </svg>
                </div>
              )}
            </div>
          ))}
        </div>
      </div>

      {/* Model Performance Metrics */}
      <div>
        <h4 className="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">Model Performance Metrics</h4>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {pipeline.map((model, index) => (
            <div key={index} className="border border-gray-200 dark:border-gray-700 rounded-lg p-4 hover:border-gray-300 dark:border-gray-600 transition-colors">
              <div className="flex items-center gap-2 mb-3">
                <div className={`w-2 h-2 rounded-full ${model.bgColor} border ${model.borderColor}`}></div>
                <h5 className={`text-sm font-semibold ${model.color}`}>
                  {model.name}
                </h5>
              </div>
              <div className="space-y-2">
                {model.metrics.map((metric, mIndex) => (
                  <div key={mIndex} className="flex items-center justify-between">
                    <span className="text-xs text-gray-600 dark:text-gray-400">{metric.label}:</span>
                    <span className="text-sm font-bold text-gray-900 dark:text-white">{metric.value}</span>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}