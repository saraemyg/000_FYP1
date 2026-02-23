export * from './auth.types'
export * from './video.types'
export * from './detection.types'
export * from './search.types'

export interface Camera {
  camera_id: number
  camera_name: string
  location: string | null
  resolution: string | null
  fps: number | null
  mask_file_path: string | null
  is_active: boolean
  created_at: string
}

export interface MetricsSummary {
  total_videos: number
  total_detections: number
  average_fps: number
  average_area_reduction: number
  total_processing_time: number
}

export interface VideoMetrics {
  video_id: number
  filename: string
  avg_fps: number | null
  total_detections: number
  processing_time_seconds: number | null
  area_reduction_percentage: number | null
  recorded_at: string
}

export interface GenderDistribution {
  male: number
  female: number
  unknown: number
}

export interface ColorDistribution {
  color: string
  count: number
}

export interface MetricsDetail {
  summary: MetricsSummary
  gender_distribution: GenderDistribution
  upper_color_distribution: ColorDistribution[]
  lower_color_distribution: ColorDistribution[]
}

export interface RecentActivity {
  video_id: number
  filename: string
  status: string
  timestamp: string
  detection_count: number
  processing_time: number | null
  duration: number | null
}

export interface APIResponse<T> {
  success: boolean
  message?: string
  data?: T
}

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  page: number
  page_size: number
  total_pages: number
}

// UR5: Alert types for reduced monitoring burden
export interface AlertRule {
  rule_id: number
  user_id: number
  name: string
  description: string | null
  gender: string | null
  upper_color: string | null
  lower_color: string | null
  min_confidence: number
  is_active: boolean
  notify_on_match: boolean
  created_at: string
  updated_at: string
}

export interface AlertRuleCreate {
  name: string
  description?: string
  gender?: string
  upper_color?: string
  lower_color?: string
  min_confidence?: number
  is_active?: boolean
  notify_on_match?: boolean
}

export interface TriggeredAlert {
  alert_id: number
  rule_id: number
  rule_name: string | null
  detection_id: number
  video_id: number
  video_filename: string | null
  matched_attributes: Record<string, unknown> | null
  confidence_score: number | null
  timestamp_in_video: number | null
  is_read: boolean
  is_acknowledged: boolean
  acknowledged_by: number | null
  acknowledged_at: string | null
  triggered_at: string
}

export interface AlertStats {
  total_rules: number
  active_rules: number
  total_triggered: number
  unread_alerts: number
  unacknowledged_alerts: number
}
