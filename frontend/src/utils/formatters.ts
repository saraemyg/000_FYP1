/**
 * Format seconds to HH:MM:SS or MM:SS string
 */
export function formatDuration(seconds: number | null | undefined): string {
  if (seconds === null || seconds === undefined) return '--:--'

  const hours = Math.floor(seconds / 3600)
  const minutes = Math.floor((seconds % 3600) / 60)
  const secs = Math.floor(seconds % 60)

  if (hours > 0) {
    return `${hours.toString().padStart(2, '0')}:${minutes
      .toString()
      .padStart(2, '0')}:${secs.toString().padStart(2, '0')}`
  }
  return `${minutes.toString().padStart(2, '0')}:${secs
    .toString()
    .padStart(2, '0')}`
}

/**
 * Format timestamp to readable date string
 */
export function formatDate(timestamp: string | null | undefined): string {
  if (!timestamp) return '-'
  return new Date(timestamp).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

/**
 * Format timestamp to readable date and time string
 */
export function formatDateTime(timestamp: string | null | undefined): string {
  if (!timestamp) return '-'
  return new Date(timestamp).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  })
}

/**
 * Format file size in bytes to human readable string
 */
export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'

  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB', 'TB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))

  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

/**
 * Format confidence score as percentage
 */
export function formatConfidence(confidence: number | null | undefined): string {
  if (confidence === null || confidence === undefined) return '-'
  return `${(confidence * 100).toFixed(1)}%`
}

/**
 * Get confidence level class for styling
 */
export function getConfidenceClass(confidence: number): string {
  if (confidence >= 0.8) return 'bg-green-100 text-green-800'
  if (confidence >= 0.6) return 'bg-yellow-100 text-yellow-800'
  return 'bg-red-100 text-red-800'
}

/**
 * Get status badge color class
 */
export function getStatusClass(status: string): string {
  switch (status) {
    case 'completed':
      return 'bg-green-100 text-green-800'
    case 'processing':
      return 'bg-blue-100 text-blue-800'
    case 'uploaded':
      return 'bg-gray-100 text-gray-800'
    case 'failed':
      return 'bg-red-100 text-red-800'
    default:
      return 'bg-gray-100 text-gray-800'
  }
}

/**
 * Capitalize first letter of string
 */
export function capitalize(str: string): string {
  return str.charAt(0).toUpperCase() + str.slice(1)
}

/**
 * Get color class for attribute badges
 */
export function getColorClass(color: string): string {
  const colorMap: Record<string, string> = {
    red: 'bg-red-500',
    blue: 'bg-blue-500',
    black: 'bg-gray-900',
    white: 'bg-gray-100 border border-gray-300',
    gray: 'bg-gray-500',
    grey: 'bg-gray-500',
    green: 'bg-green-500',
    yellow: 'bg-yellow-400',
    brown: 'bg-amber-700',
    pink: 'bg-pink-400',
    orange: 'bg-orange-500',
    purple: 'bg-purple-500',
  }
  return colorMap[color.toLowerCase()] || 'bg-gray-400'
}
