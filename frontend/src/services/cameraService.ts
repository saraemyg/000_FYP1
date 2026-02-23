import api from './api'
import { Camera } from '@/types'

export interface CameraCreate {
  camera_name: string
  location?: string
  resolution?: string
  fps?: number
}

export interface CameraUpdate {
  camera_name?: string
  location?: string
  resolution?: string
  fps?: number
  is_active?: boolean
}

export interface SegmentationMask {
  mask_id: number
  camera_id: number | null
  mask_file_path: string
  reduction_percentage: number | null
  generation_timestamp: string
  sample_frame_path: string | null
}

export const cameraService = {
  async listCameras(includeInactive: boolean = false): Promise<Camera[]> {
    const response = await api.get<Camera[]>('/cameras', {
      params: { include_inactive: includeInactive },
    })
    return response.data
  },

  async getCamera(cameraId: number): Promise<Camera> {
    const response = await api.get<Camera>(`/cameras/${cameraId}`)
    return response.data
  },

  async createCamera(data: CameraCreate): Promise<Camera> {
    const response = await api.post<Camera>('/cameras', data)
    return response.data
  },

  async updateCamera(cameraId: number, data: CameraUpdate): Promise<Camera> {
    const response = await api.put<Camera>(`/cameras/${cameraId}`, data)
    return response.data
  },

  async deleteCamera(cameraId: number): Promise<void> {
    await api.delete(`/cameras/${cameraId}`)
  },

  async generateMask(cameraId: number, sampleFrame: File): Promise<SegmentationMask> {
    const formData = new FormData()
    formData.append('sample_frame', sampleFrame)

    const response = await api.post<SegmentationMask>(
      `/cameras/${cameraId}/mask/generate`,
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    )
    return response.data
  },

  async getCameraMasks(cameraId: number): Promise<SegmentationMask[]> {
    const response = await api.get<SegmentationMask[]>(`/cameras/${cameraId}/masks`)
    return response.data
  },
}
