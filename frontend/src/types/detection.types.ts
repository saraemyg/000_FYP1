export interface Attribute {
  attribute_id: number
  detection_id: number
  upper_color: string | null
  upper_color_confidence: number | null
  lower_color: string | null
  lower_color_confidence: number | null
  gender: 'male' | 'female' | 'unknown' | null
  gender_confidence: number | null
  aggregate_confidence: number
  created_at: string
}

export interface Detection {
  detection_id: number
  video_id: number
  frame_number: number
  timestamp_in_video: number
  bbox_x: number
  bbox_y: number
  bbox_width: number
  bbox_height: number
  detection_confidence: number
  person_crop_path: string | null
  created_at: string
  attributes: Attribute[]
}

export interface DetectionSummary {
  video_id: number
  total_detections: number
  gender_distribution: {
    male: number
    female: number
    unknown: number
  }
  upper_color_distribution: Record<string, number>
  lower_color_distribution: Record<string, number>
}
