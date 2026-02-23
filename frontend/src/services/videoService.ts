import api from './api'
import { Video, VideoProcessingStatus } from '@/types'

export const videoService = {
  async uploadVideo(
    file: File,
    onProgress?: (progress: number) => void
  ): Promise<Video> {
    const formData = new FormData()
    formData.append('file', file)

    const response = await api.post<Video>('/videos/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress: (progressEvent) => {
        if (progressEvent.total && onProgress) {
          const progress = Math.round(
            (progressEvent.loaded * 100) / progressEvent.total
          )
          onProgress(progress)
        }
      },
    })
    return response.data
  },

  async processVideo(videoId: number): Promise<{ message: string; video_id: number; status: string }> {
    const response = await api.post(`/videos/${videoId}/process`)
    return response.data
  },

  async getProcessingStatus(videoId: number): Promise<VideoProcessingStatus> {
    const response = await api.get<VideoProcessingStatus>(
      `/videos/${videoId}/status`
    )
    return response.data
  },

  async getVideo(videoId: number): Promise<Video> {
    const response = await api.get<Video>(`/videos/${videoId}`)
    return response.data
  },

  async listVideos(params?: {
    skip?: number
    limit?: number
    status_filter?: string
  }): Promise<Video[]> {
    const response = await api.get<Video[]>('/videos', { params })
    return response.data
  },

  async deleteVideo(videoId: number): Promise<void> {
    await api.delete(`/videos/${videoId}`)
  },

  // FR11: Video Clip Extraction
  async extractClipForDetection(
    videoId: number,
    detectionId: number,
    bufferBefore: number = 3.0,
    bufferAfter: number = 3.0
  ): Promise<Blob> {
    const response = await api.get(`/videos/${videoId}/clip/${detectionId}`, {
      params: { buffer_before: bufferBefore, buffer_after: bufferAfter },
      responseType: 'blob',
    })
    return response.data
  },

  async extractClipByTimeRange(
    videoId: number,
    startTime: number,
    endTime: number
  ): Promise<Blob> {
    const response = await api.get(`/videos/${videoId}/clip-by-time`, {
      params: { start_time: startTime, end_time: endTime },
      responseType: 'blob',
    })
    return response.data
  },

  // FR4: Detection Visualization
  getAnnotatedFrameUrl(detectionId: number, showAllDetections: boolean = false): string {
    const baseUrl = api.defaults.baseURL || ''
    return `${baseUrl}/detections/${detectionId}/annotated-frame?show_all_detections=${showAllDetections}`
  },

  getFrameWithDetectionsUrl(videoId: number, frameNumber: number): string {
    const baseUrl = api.defaults.baseURL || ''
    return `${baseUrl}/detections/frame/${videoId}/${frameNumber}/annotated`
  },
}
