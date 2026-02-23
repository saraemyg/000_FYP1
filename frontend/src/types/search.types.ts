export interface ParsedQuery {
  gender: string | null
  upper_color: string | null
  lower_color: string | null
  raw_query: string
}

export interface NaturalLanguageQuery {
  query: string
  min_confidence?: number
  limit?: number
  offset?: number
}

export interface AdvancedSearchQuery {
  gender?: string | null
  upper_color?: string | null
  lower_color?: string | null
  min_confidence?: number
  video_id?: number | null
  start_timestamp?: number | null
  end_timestamp?: number | null
  limit?: number
  offset?: number
  sort_by?: 'confidence' | 'timestamp'
  sort_order?: 'asc' | 'desc'
}

export interface SearchResultItem {
  detection_id: number
  video_id: number
  video_filename: string
  frame_number: number
  timestamp_in_video: number
  bbox_x: number
  bbox_y: number
  bbox_width: number
  bbox_height: number
  detection_confidence: number
  person_crop_path: string | null
  upper_color: string | null
  upper_color_confidence: number | null
  lower_color: string | null
  lower_color_confidence: number | null
  gender: string | null
  gender_confidence: number | null
  aggregate_confidence: number
}

export interface SearchResponse {
  query: string
  parsed_attributes: ParsedQuery
  total_count: number
  results: SearchResultItem[]
}

export interface SearchHistoryItem {
  search_id: number
  query_text: string
  parsed_attributes: Record<string, unknown> | null
  result_count: number | null
  search_timestamp: string
}
