export interface Video {
  video_id: number
  filename: string
  file_path: string
  upload_timestamp: string
  duration_seconds: number | null
  fps: number | null
  resolution: string | null
  total_frames: number | null
  processing_status: 'uploaded' | 'processing' | 'completed' | 'failed'
  uploaded_by: number | null
}

export interface VideoProcessingStatus {
  video_id: number
  status: string
  progress: number
  current_frame: number | null
  total_frames: number | null
  detections_count: number
  message?: string
}

export interface VideoUploadProgress {
  loaded: number
  total: number
  percentage: number
}
