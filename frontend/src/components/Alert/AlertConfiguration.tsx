import { useState } from 'react';

interface BehaviorConfig {
  min: number;
  max: number;
  enabled: boolean;
  priority: 'LOW' | 'MEDIUM' | 'HIGH';
}

type ConfigState = {
  [key: string]: BehaviorConfig;
};

const DEFAULT_CONFIG: ConfigState = {
  RUN: { min: 80, max: 100, enabled: false, priority: 'LOW' },
  BEND: { min: 80, max: 100, enabled: false, priority: 'LOW' },
  WALK: { min: 80, max: 100, enabled: false, priority: 'LOW' },
  STAND: { min: 80, max: 100, enabled: false, priority: 'LOW' },
  SIT: { min: 80, max: 100, enabled: false, priority: 'LOW' },
  LOITER: { min: 80, max: 100, enabled: false, priority: 'LOW' },
  LAY: { min: 80, max: 100, enabled: false, priority: 'LOW' }
};

export default function AlertConfiguration() {
  const [config, setConfig] = useState<ConfigState>({
    RUN: { min: 90, max: 100, enabled: true, priority: 'HIGH' },
    BEND: { min: 70, max: 85, enabled: true, priority: 'MEDIUM' },
    WALK: { min: 60, max: 70, enabled: false, priority: 'LOW' },
    STAND: { min: 50, max: 65, enabled: false, priority: 'LOW' },
    SIT: { min: 40, max: 55, enabled: false, priority: 'LOW' },
    LOITER: { min: 75, max: 90, enabled: true, priority: 'HIGH' },
    LAY: { min: 85, max: 95, enabled: true, priority: 'HIGH' }
  });

  const getColorForBehavior = (behavior: string) => {
    const colors: { [key: string]: string } = {
      RUN: 'text-red-600',
      BEND: 'text-yellow-600',
      WALK: 'text-green-600',
      STAND: 'text-blue-600',
      SIT: 'text-purple-600',
      LOITER: 'text-orange-600',
      LAY: 'text-pink-600'
    };
    return colors[behavior] || 'text-gray-600 dark:text-gray-400';
  };

  const getPriorityColor = (priority: string) => {
    switch (priority) {
      case 'HIGH':
        return 'bg-red-100 text-red-700 border-red-300';
      case 'MEDIUM':
        return 'bg-yellow-100 text-yellow-700 border-yellow-300';
      case 'LOW':
        return 'bg-green-100 text-green-700 border-green-300';
      default:
        return 'bg-gray-100 text-gray-700 dark:text-gray-300 border-gray-300 dark:border-gray-600';
    }
  };

  const handleReset = () => {
    setConfig(DEFAULT_CONFIG);
  };

  const handleSave = () => {
    console.log('Saved configuration:', config);
    alert('Configuration saved successfully!');
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-sm p-6">
      <div className="flex items-center justify-between mb-4">
        <div>
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white">Alert Configuration</h3>
          <p className="text-sm text-gray-500 dark:text-gray-400">Setup confidence threshold and notifications</p>
        </div>
        <div className="flex gap-2">
          <button 
            onClick={handleReset}
            className="px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg text-sm font-medium text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors"
          >
            Reset
          </button>
          <button 
            onClick={handleSave}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            Save Changes
          </button>
        </div>
      </div>

      <div className="border rounded-lg overflow-hidden">
        <div className="bg-gray-50 dark:bg-gray-900 px-4 py-3 grid grid-cols-5 gap-4 text-sm font-medium text-gray-700 dark:text-gray-300">
          <div>Behavior</div>
          <div className="col-span-2">Confidence Threshold</div>
          <div>Priority Level</div>
          <div className="text-center">Enable</div>
        </div>

        <div className="divide-y">
          {Object.entries(config).map(([behavior, settings]) => (
            <div key={behavior} className="px-4 py-4 grid grid-cols-5 gap-4 items-center hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
              <div className="flex items-center gap-2">
                <div className={`w-2 h-2 rounded-full ${settings.enabled ? 'bg-green-500' : 'bg-gray-300'}`} />
                <span className={`font-medium ${getColorForBehavior(behavior)}`}>{behavior}</span>
              </div>

              <div className="col-span-2">
                <div className="flex items-center gap-3">
                  <input
                    type="range"
                    min="0"
                    max="100"
                    value={settings.min}
                    onChange={(e) => {
                      setConfig({
                        ...config,
                        [behavior]: { ...settings, min: parseInt(e.target.value) }
                      });
                    }}
                    className="flex-1"
                    disabled={!settings.enabled}
                  />
                  <div className="flex items-center gap-2 min-w-[120px]">
                    <input
                      type="number"
                      value={settings.min}
                      onChange={(e) => {
                        setConfig({
                          ...config,
                          [behavior]: { ...settings, min: parseInt(e.target.value) }
                        });
                      }}
                      className="w-16 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm text-center disabled:bg-gray-100"
                      disabled={!settings.enabled}
                    />
                    <span className="text-gray-500 dark:text-gray-400">-</span>
                    <input
                      type="number"
                      value={settings.max}
                      onChange={(e) => {
                        setConfig({
                          ...config,
                          [behavior]: { ...settings, max: parseInt(e.target.value) }
                        });
                      }}
                      className="w-16 px-2 py-1 border border-gray-300 dark:border-gray-600 rounded text-sm text-center disabled:bg-gray-100"
                      disabled={!settings.enabled}
                    />
                  </div>
                </div>
              </div>

              <div>
                <select
                  value={settings.priority}
                  onChange={(e) => {
                    setConfig({
                      ...config,
                      [behavior]: { ...settings, priority: e.target.value as 'LOW' | 'MEDIUM' | 'HIGH' }
                    });
                  }}
                  className={`px-3 py-1 rounded text-xs font-medium border ${getPriorityColor(settings.priority)} focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:opacity-50 disabled:cursor-not-allowed`}
                  disabled={!settings.enabled}
                >
                  <option value="LOW">LOW</option>
                  <option value="MEDIUM">MEDIUM</option>
                  <option value="HIGH">HIGH</option>
                </select>
              </div>

              <div className="flex justify-center">
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    checked={settings.enabled}
                    onChange={(e) => {
                      setConfig({
                        ...config,
                        [behavior]: { ...settings, enabled: e.target.checked }
                      });
                    }}
                    className="sr-only peer"
                  />
                  <div className="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-blue-300 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 dark:border-gray-600 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-blue-600"></div>
                </label>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}