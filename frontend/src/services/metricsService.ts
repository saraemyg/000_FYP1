import api from './api'
import { MetricsSummary, VideoMetrics, MetricsDetail, RecentActivity } from '@/types'

export const metricsService = {
  async getSummary(): Promise<MetricsSummary> {
    const response = await api.get<MetricsSummary>('/metrics/summary')
    return response.data
  },

  async getVideoMetrics(limit: number = 20): Promise<VideoMetrics[]> {
    const response = await api.get<VideoMetrics[]>('/metrics/videos', {
      params: { limit },
    })
    return response.data
  },

  async getAttributeMetrics(): Promise<MetricsDetail> {
    const response = await api.get<MetricsDetail>('/metrics/attributes')
    return response.data
  },

  async getRecentActivity(limit: number = 10): Promise<RecentActivity[]> {
    const response = await api.get<RecentActivity[]>('/metrics/recent-activity', {
      params: { limit },
    })
    return response.data
  },

  // UR9: Performance Transparency - Real-time monitoring endpoints
  async getProcessingStatus(): Promise<ProcessingStatus> {
    const response = await api.get<ProcessingStatus>('/metrics/processing-status')
    return response.data
  },

  async getAccuracyStats(): Promise<AccuracyStats> {
    const response = await api.get<AccuracyStats>('/metrics/accuracy-stats')
    return response.data
  },

  async getSystemHealth(): Promise<SystemHealth> {
    const response = await api.get<SystemHealth>('/metrics/system-health')
    return response.data
  },
}

// Types for UR9 endpoints
export interface ProcessingQueueItem {
  video_id: number
  filename: string
  total_frames: number | null
  duration_seconds: number | null
  fps: number | null
  resolution: string | null
  current_detections: number
  upload_timestamp: string | null
}

export interface CompletedVideoItem {
  video_id: number
  filename: string
  total_detections: number
  avg_fps: number | null
  processing_time_seconds: number | null
  area_reduction_percentage: number | null
}

export interface FailedVideoItem {
  video_id: number
  filename: string
  upload_timestamp: string | null
}

export interface ProcessingStatus {
  processing_count: number
  processing_queue: ProcessingQueueItem[]
  recently_completed: CompletedVideoItem[]
  failed_videos: FailedVideoItem[]
  system_status: 'healthy' | 'busy' | 'overloaded'
}

export interface AccuracyStats {
  detection_confidence: {
    average: number
    minimum: number
    maximum: number
    total_count: number
  }
  attribute_confidence: {
    gender_average: number
    upper_color_average: number
    lower_color_average: number
  }
  confidence_distribution: {
    high: number
    medium: number
    low: number
    high_percentage: number
    medium_percentage: number
    low_percentage: number
  }
}

export interface SystemHealth {
  overall_status: 'healthy' | 'busy' | 'overloaded'
  database_connected: boolean
  processing_queue_size: number
  recent_avg_fps: number | null
  fps_status: 'good' | 'degraded' | 'unknown'
  target_fps: number
  checks: {
    database: 'pass' | 'fail'
    processing_capacity: 'pass' | 'warning'
    fps_performance: 'pass' | 'warning' | 'unknown'
  }
}
