export default function Logo() {
  return (
    <div className="text-center">
      <div className="mx-auto h-16 w-16 bg-blue-600 rounded-full flex items-center justify-center">
        <svg className="h-10 w-10 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 10l4.553-2.276A1 1 0 0121 8.618v6.764a1 1 0 01-1.447.894L15 14M5 18h8a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z" />
        </svg>
      </div>
      <h2 className="mt-4 text-3xl font-bold text-gray-100">
        Surveillance System
      </h2>
      <p className="mt-2 text-sm text-gray-100">
        Automated Behavior Analysis Platform
      </p>
    </div>
  );
}
