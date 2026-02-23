import { ALLOWED_VIDEO_TYPES, MAX_FILE_SIZE_BYTES } from './constants'

/**
 * Validate video file type and size
 */
export function validateVideoFile(file: File): { valid: boolean; error?: string } {
  // Check file type
  if (!ALLOWED_VIDEO_TYPES.includes(file.type)) {
    return {
      valid: false,
      error: 'Invalid file type. Allowed formats: MP4, AVI, MOV, MKV, WMV, FLV',
    }
  }

  // Check file size
  if (file.size > MAX_FILE_SIZE_BYTES) {
    return {
      valid: false,
      error: `File too large. Maximum size: ${MAX_FILE_SIZE_BYTES / (1024 * 1024)}MB`,
    }
  }

  return { valid: true }
}

/**
 * Validate email format
 */
export function validateEmail(email: string): boolean {
  const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  return emailRegex.test(email)
}

/**
 * Validate username (alphanumeric, 3-50 chars)
 */
export function validateUsername(username: string): boolean {
  const usernameRegex = /^[a-zA-Z0-9_]{3,50}$/
  return usernameRegex.test(username)
}

/**
 * Validate password (minimum 6 chars)
 */
export function validatePassword(password: string): boolean {
  return password.length >= 6
}

/**
 * Validate image file type
 */
export function validateImageFile(file: File): { valid: boolean; error?: string } {
  const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/bmp']

  if (!allowedTypes.includes(file.type)) {
    return {
      valid: false,
      error: 'Invalid file type. Allowed formats: JPEG, PNG, GIF, BMP',
    }
  }

  return { valid: true }
}
