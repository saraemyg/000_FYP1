import api from './api'
import {
  NaturalLanguageQuery,
  AdvancedSearchQuery,
  SearchResponse,
  SearchHistoryItem,
} from '@/types'

export const searchService = {
  async naturalLanguageSearch(query: NaturalLanguageQuery): Promise<SearchResponse> {
    const response = await api.post<SearchResponse>('/search/query', query)
    return response.data
  },

  async advancedSearch(query: AdvancedSearchQuery): Promise<SearchResponse> {
    const response = await api.post<SearchResponse>('/search/advanced', query)
    return response.data
  },

  async getSearchHistory(limit: number = 20): Promise<SearchHistoryItem[]> {
    const response = await api.get<SearchHistoryItem[]>('/search/history', {
      params: { limit },
    })
    return response.data
  },

  async deleteSearchHistoryItem(searchId: number): Promise<void> {
    await api.delete(`/search/history/${searchId}`)
  },

  async clearSearchHistory(): Promise<void> {
    await api.delete('/search/history')
  },

  // UR8: Evidence Export functions
  async exportResultsJson(query: AdvancedSearchQuery): Promise<Blob> {
    const response = await api.post('/search/export/json', query, {
      responseType: 'blob',
    })
    return response.data
  },

  async exportResultsCsv(query: AdvancedSearchQuery): Promise<Blob> {
    const response = await api.post('/search/export/csv', query, {
      responseType: 'blob',
    })
    return response.data
  },

  async exportDetectionMetadata(detectionId: number): Promise<Blob> {
    const response = await api.get(`/search/export/detection/${detectionId}/metadata`, {
      responseType: 'blob',
    })
    return response.data
  },
}
