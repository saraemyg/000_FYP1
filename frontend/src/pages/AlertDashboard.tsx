import BehaviorDistribution from '../components/Alert/BehaviorDistribution';
import AlertPriorityChart from '../components/Alert/AlertPriorityChart';
import AlertConfiguration from '../components/Alert/AlertConfiguration';
import AlertHistory from '../components/Alert/AlertHistory';

export default function AlertDashboard() {
  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors">
      <div className="max-w-[1920px] mx-auto p-6">
        <div className="mb-6">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white">Alert Dashboard</h1>
          <p className="text-gray-600 dark:text-gray-400 mt-1">
            Real-time monitoring and analysis of all detected alerts
          </p>
        </div>

        {/* Charts Section */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          <div>
            <BehaviorDistribution />
          </div>
          <div>
            <AlertPriorityChart />
          </div>
        </div>

        {/* Alert Configuration - Full Width */}
        <div className="mb-6">
          <AlertConfiguration />
        </div>

        {/* Alert History */}
        <AlertHistory />
      </div>
    </div>
  );
}