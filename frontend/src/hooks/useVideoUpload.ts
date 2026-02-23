import { useState, useCallback } from 'react'
import { useMutation, useQueryClient } from '@tanstack/react-query'
import { videoService } from '@/services'
import { Video } from '@/types'

interface UploadState {
  isUploading: boolean
  progress: number
  error: string | null
}

export function useVideoUpload() {
  const queryClient = useQueryClient()
  const [uploadState, setUploadState] = useState<UploadState>({
    isUploading: false,
    progress: 0,
    error: null,
  })

  const uploadMutation = useMutation({
    mutationFn: async (file: File): Promise<Video> => {
      setUploadState({ isUploading: true, progress: 0, error: null })

      const video = await videoService.uploadVideo(file, (progress) => {
        setUploadState((prev) => ({ ...prev, progress }))
      })

      return video
    },
    onSuccess: () => {
      setUploadState({ isUploading: false, progress: 100, error: null })
      queryClient.invalidateQueries({ queryKey: ['videos'] })
    },
    onError: (error: Error) => {
      setUploadState({ isUploading: false, progress: 0, error: error.message })
    },
  })

  const upload = useCallback(
    (file: File) => {
      uploadMutation.mutate(file)
    },
    [uploadMutation]
  )

  const reset = useCallback(() => {
    setUploadState({ isUploading: false, progress: 0, error: null })
    uploadMutation.reset()
  }, [uploadMutation])

  return {
    upload,
    reset,
    uploadedVideo: uploadMutation.data,
    ...uploadState,
  }
}
