/**
 * Alert service for managing detection alerts.
 * UR5: Reduced Monitoring Burden
 */
import api from './api'

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

export const alertService = {
  // Alert Rules
  async listRules(activeOnly: boolean = false): Promise<AlertRule[]> {
    const response = await api.get<AlertRule[]>('/alerts/rules', {
      params: { active_only: activeOnly },
    })
    return response.data
  },

  async createRule(rule: AlertRuleCreate): Promise<AlertRule> {
    const response = await api.post<AlertRule>('/alerts/rules', rule)
    return response.data
  },

  async getRule(ruleId: number): Promise<AlertRule> {
    const response = await api.get<AlertRule>(`/alerts/rules/${ruleId}`)
    return response.data
  },

  async updateRule(ruleId: number, rule: Partial<AlertRuleCreate>): Promise<AlertRule> {
    const response = await api.put<AlertRule>(`/alerts/rules/${ruleId}`, rule)
    return response.data
  },

  async deleteRule(ruleId: number): Promise<void> {
    await api.delete(`/alerts/rules/${ruleId}`)
  },

  // Triggered Alerts
  async listTriggeredAlerts(
    unreadOnly: boolean = false,
    unacknowledgedOnly: boolean = false,
    limit: number = 50,
    offset: number = 0
  ): Promise<TriggeredAlert[]> {
    const response = await api.get<TriggeredAlert[]>('/alerts/triggered', {
      params: {
        unread_only: unreadOnly,
        unacknowledged_only: unacknowledgedOnly,
        limit,
        offset,
      },
    })
    return response.data
  },

  async markAlertRead(alertId: number): Promise<void> {
    await api.post(`/alerts/triggered/${alertId}/read`)
  },

  async acknowledgeAlert(alertId: number): Promise<void> {
    await api.post(`/alerts/triggered/${alertId}/acknowledge`)
  },

  async markAllAlertsRead(): Promise<void> {
    await api.post('/alerts/triggered/mark-all-read')
  },

  // Stats
  async getStats(): Promise<AlertStats> {
    const response = await api.get<AlertStats>('/alerts/stats')
    return response.data
  },
}
