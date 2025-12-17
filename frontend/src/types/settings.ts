/**
 * Settings Types for User Preferences
 * 005-lawyer-portal-pages Feature - US4
 */

export interface UserProfile {
  display_name: string;
  email: string;
  phone?: string;
  avatar_url?: string;
  timezone: string;
  language: string;
  role: string;
  created_at: string;
}

export interface ProfileUpdateRequest {
  display_name?: string;
  phone?: string;
  timezone?: string;
  language?: string;
}

export interface NotificationSettings {
  email_enabled: boolean;
  push_enabled: boolean;
  frequency: 'immediate' | 'daily' | 'weekly';
  notification_types: NotificationTypes;
}

export interface NotificationTypes {
  new_evidence: boolean;
  case_updates: boolean;
  messages: boolean;
  calendar_reminders: boolean;
  billing_alerts: boolean;
}

export interface NotificationUpdateRequest {
  email_enabled?: boolean;
  push_enabled?: boolean;
  frequency?: 'immediate' | 'daily' | 'weekly';
  notification_types?: Partial<NotificationTypes>;
}

export interface SecuritySettings {
  two_factor_enabled: boolean;
  last_password_change?: string;
  active_sessions: number;
  login_history: LoginHistoryItem[];
}

export interface LoginHistoryItem {
  timestamp: string;
  ip_address: string;
  device: string;
  location?: string;
}

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
}

export interface UserSettingsResponse {
  profile: UserProfile;
  notifications: NotificationSettings;
  security: SecuritySettings;
}
