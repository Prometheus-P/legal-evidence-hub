/**
 * Custom Hooks
 *
 * Reusable React hooks for common functionality
 */

// Authentication & Role
export { useAuth } from './useAuth';
export { useRole } from './useRole';

// Data fetching - Lists
export { useCaseList } from './useCaseList';
export { useClients } from './useClients';
export { useInvestigators } from './useInvestigators';

// Data fetching - Detail
export { useCaseDetail } from './useCaseDetail';

// Draft generation
export { useDraft } from './useDraft';

// Dashboard
export { useLawyerDashboard } from './useLawyerDashboard';

// Evidence management
export { useEvidenceTable } from './useEvidenceTable';
export {
  useEvidencePolling,
  useSingleEvidencePolling,
} from './useEvidencePolling';
export { useEvidenceLinks } from './useEvidenceLinks';
export { useSpeakerMapping, extractSpeakersFromContent } from './useSpeakerMapping';

// Case features
export { useCaseRelations } from './useCaseRelations';
export { usePartyGraph } from './usePartyGraph';
export { useProcedure } from './useProcedure';
export { useAssets } from './useAssets';

// Calendar & scheduling
export { useCalendar } from './useCalendar';
export { useTodayView } from './useTodayView';

// Messaging & notifications
export { useMessages } from './useMessages';
export { useDirectMessages } from './useDirectMessages';
export { useNotifications } from './useNotifications';

// AI features
export { useAIRecommendations } from './useAIRecommendations';
export { useRiskFlags } from './useRiskFlags';

// Contacts
export { useClientContacts } from './useClientContacts';
export { useDetectiveContacts } from './useDetectiveContacts';

// Settings & billing
export { useSettings } from './useSettings';
export { useBilling } from './useBilling';

// Search
export { useGlobalSearch } from './useGlobalSearch';

// UI utilities
export { useModalState } from './useModalState';
export { useBeforeUnload } from './useBeforeUnload';
export { useKeyboardShortcuts } from './useKeyboardShortcuts';

// Error handling & retry
export { useRetry, retryOperation } from './useRetry';

// URL utilities
export { useCaseIdFromUrl } from './useCaseIdFromUrl';
export { useCaseIdValidation } from './useCaseIdValidation';

// Upload utilities
export { useEvidenceUpload } from './useEvidenceUpload';
export type { UploadStatus, UploadFeedback, FeedbackTone } from './useEvidenceUpload';
