import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { searchService } from '@/services'
import { SearchResponse, AdvancedSearchQuery } from '@/types'

export function useNaturalLanguageSearch() {
  const [results, setResults] = useState<SearchResponse | null>(null)

  const searchMutation = useMutation({
    mutationFn: async (query: string) => {
      const response = await searchService.naturalLanguageSearch({
        query,
        min_confidence: 0.6,
        limit: 50,
      })
      return response
    },
    onSuccess: (data) => {
      setResults(data)
    },
  })

  return {
    search: searchMutation.mutate,
    results,
    isSearching: searchMutation.isPending,
    error: searchMutation.error,
    reset: () => {
      setResults(null)
      searchMutation.reset()
    },
  }
}

export function useAdvancedSearch() {
  const [results, setResults] = useState<SearchResponse | null>(null)

  const searchMutation = useMutation({
    mutationFn: async (query: AdvancedSearchQuery) => {
      const response = await searchService.advancedSearch(query)
      return response
    },
    onSuccess: (data) => {
      setResults(data)
    },
  })

  return {
    search: searchMutation.mutate,
    results,
    isSearching: searchMutation.isPending,
    error: searchMutation.error,
    reset: () => {
      setResults(null)
      searchMutation.reset()
    },
  }
}

export function useSearchHistory() {
  const query = useQuery({
    queryKey: ['searchHistory'],
    queryFn: () => searchService.getSearchHistory(20),
  })

  return query
}
