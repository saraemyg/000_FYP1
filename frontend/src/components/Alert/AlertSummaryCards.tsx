export default function AlertSummaryCards() {
  const cards = [
    {
      icon: (
        <svg className="w-8 h-8 text-red-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
        </svg>
      ),
      value: '127',
      label: 'Total Alerts',
      subtitle: 'Last 24 hours',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-100'
    },
    {
      label: 'High Priority',
      subtitle: 'Immediate alerts for potentially dangerous behaviors',
      value: '1',
      subLabel: 'Active criteria',
      bgColor: 'bg-red-50',
      borderColor: 'border-red-200',
      textColor: 'text-red-700'
    },
    {
      label: 'Medium Priority',
      subtitle: 'Alerts for suspicious but not critical behaviors',
      value: '1',
      subLabel: 'Active criteria',
      bgColor: 'bg-yellow-50',
      borderColor: 'border-yellow-200',
      textColor: 'text-yellow-700'
    },
    {
      label: 'Low Priority',
      subtitle: 'Low normal behaviors for monitoring and analytics',
      value: '0',
      subLabel: 'Active criteria',
      bgColor: 'bg-green-50',
      borderColor: 'border-green-200',
      textColor: 'text-green-700'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
      {cards.map((card, index) => (
        <div
          key={index}
          className={`${card.bgColor} border ${card.borderColor} rounded-lg p-6`}
        >
          {index === 0 ? (
            <>
              <div className="flex justify-center mb-3">{card.icon}</div>
              <div className="text-center">
                <div className={`text-4xl font-bold ${card.textColor || 'text-red-700'} mb-1`}>
                  {card.value}
                </div>
                <div className="text-sm font-medium text-gray-700">{card.label}</div>
                <div className="text-xs text-gray-500 mt-1">{card.subtitle}</div>
              </div>
            </>
          ) : (
            <>
              <div className="text-sm font-medium text-gray-700 mb-2">{card.label}</div>
              <div className="text-xs text-gray-600 mb-3">{card.subtitle}</div>
              <div className={`text-3xl font-bold ${card.textColor} mb-1`}>{card.value}</div>
              <div className="text-xs text-gray-500">{card.subLabel}</div>
            </>
          )}
        </div>
      ))}
    </div>
  );
}
