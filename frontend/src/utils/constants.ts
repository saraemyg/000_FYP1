// API endpoints
export const API_BASE_URL = (import.meta as any).env.VITE_API_BASE_URL || '/api/v1'
export const WS_URL = (import.meta as any).env.VITE_WS_URL || 'ws://localhost:8000/ws'

// File upload constraints
export const MAX_FILE_SIZE_MB = 500
export const MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
export const ALLOWED_VIDEO_TYPES = [
  'video/mp4',
  'video/avi',
  'video/quicktime',
  'video/x-matroska',
  'video/x-ms-wmv',
  'video/x-flv',
]
export const ALLOWED_VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv', '.wmv', '.flv']

// Color options for search filters
export const COLOR_OPTIONS = [
  'red',
  'blue',
  'black',
  'white',
  'gray',
  'green',
  'yellow',
  'brown',
  'pink',
  'orange',
]

// Gender options
export const GENDER_OPTIONS = ['male', 'female', 'unknown']

// Pagination defaults
export const DEFAULT_PAGE_SIZE = 20
export const SEARCH_RESULT_LIMIT = 50

// Refresh intervals (ms)
export const PROCESSING_STATUS_INTERVAL = 2000
export const METRICS_REFRESH_INTERVAL = 30000
