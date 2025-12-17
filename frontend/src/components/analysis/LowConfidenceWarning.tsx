/**
 * LowConfidenceWarning Component
 * 011-production-bug-fixes Feature - #133
 *
 * Displays a warning banner when AI analysis confidence is below threshold.
 * Follows calm-control principle: alerts user to review AI suggestions manually.
 */

'use client';

import { AlertTriangle, X, Info } from 'lucide-react';
import { useState } from 'react';

interface LowConfidenceWarningProps {
  /** Confidence score from 0.0 to 1.0 */
  confidence: number;
  /** Threshold below which warning is shown (default: 0.6) */
  threshold?: number;
  /** Context about what the confidence refers to */
  context?: string;
  /** Whether the warning can be dismissed */
  dismissible?: boolean;
  /** Callback when dismissed */
  onDismiss?: () => void;
  /** Variant style */
  variant?: 'banner' | 'inline' | 'toast';
}

const THRESHOLD_LABELS = {
  veryLow: { max: 0.4, label: '매우 낮음', severity: 'critical' },
  low: { max: 0.6, label: '낮음', severity: 'warning' },
};

function getConfidenceLevel(score: number): {
  label: string;
  severity: 'critical' | 'warning';
} {
  if (score < THRESHOLD_LABELS.veryLow.max) {
    return { label: THRESHOLD_LABELS.veryLow.label, severity: 'critical' };
  }
  return { label: THRESHOLD_LABELS.low.label, severity: 'warning' };
}

export function LowConfidenceWarning({
  confidence,
  threshold = 0.6,
  context = 'AI 분석',
  dismissible = true,
  onDismiss,
  variant = 'banner',
}: LowConfidenceWarningProps) {
  const [isDismissed, setIsDismissed] = useState(false);

  // Don't show if confidence is above threshold or dismissed
  if (confidence >= threshold || isDismissed) {
    return null;
  }

  const { label, severity } = getConfidenceLevel(confidence);
  const percentage = Math.round(confidence * 100);

  const handleDismiss = () => {
    setIsDismissed(true);
    onDismiss?.();
  };

  const severityStyles = {
    critical: {
      bg: 'bg-red-50',
      border: 'border-red-200',
      text: 'text-red-800',
      icon: 'text-red-600',
    },
    warning: {
      bg: 'bg-amber-50',
      border: 'border-amber-200',
      text: 'text-amber-800',
      icon: 'text-amber-600',
    },
  };

  const styles = severityStyles[severity];

  if (variant === 'inline') {
    return (
      <div
        className={`flex items-center gap-2 px-3 py-2 rounded-lg ${styles.bg} ${styles.border} border`}
        role="alert"
        aria-live="polite"
      >
        <AlertTriangle className={`w-4 h-4 flex-shrink-0 ${styles.icon}`} />
        <span className={`text-sm ${styles.text}`}>
          신뢰도 {label} ({percentage}%)
        </span>
      </div>
    );
  }

  if (variant === 'toast') {
    return (
      <div
        className={`fixed bottom-6 right-6 z-50 flex items-center gap-3 rounded-xl px-4 py-3 shadow-lg ${styles.bg} ${styles.border} border`}
        role="alert"
        aria-live="assertive"
      >
        <AlertTriangle className={`w-5 h-5 ${styles.icon}`} />
        <div className="flex flex-col">
          <span className={`text-sm font-medium ${styles.text}`}>
            {context} 신뢰도가 {label}입니다
          </span>
          <span className={`text-xs ${styles.text} opacity-75`}>
            수동 검토를 권장합니다
          </span>
        </div>
        {dismissible && (
          <button
            type="button"
            onClick={handleDismiss}
            className={`ml-2 rounded-full p-1 hover:bg-black/5 transition-colors`}
            aria-label="경고 닫기"
          >
            <X className="w-4 h-4" />
          </button>
        )}
      </div>
    );
  }

  // Default: banner
  return (
    <div
      className={`rounded-xl ${styles.bg} ${styles.border} border p-4`}
      role="alert"
      aria-live="polite"
    >
      <div className="flex items-start gap-3">
        <AlertTriangle className={`w-5 h-5 flex-shrink-0 mt-0.5 ${styles.icon}`} />
        <div className="flex-1">
          <h4 className={`font-semibold ${styles.text}`}>
            {context} 신뢰도 주의
          </h4>
          <p className={`text-sm mt-1 ${styles.text} opacity-90`}>
            AI 분석 결과의 신뢰도가 <strong>{label} ({percentage}%)</strong>입니다.
            {severity === 'critical' ? (
              <> 이 결과를 사용하기 전에 <strong>반드시 수동으로 검토</strong>해 주세요.</>
            ) : (
              <> 결과를 참고용으로만 활용하고, 중요한 판단은 직접 확인해 주세요.</>
            )}
          </p>
          <div className="flex items-center gap-4 mt-3">
            <div className="flex items-center gap-2 text-xs">
              <Info className={`w-4 h-4 ${styles.icon}`} />
              <span className={styles.text}>
                신뢰도 60% 미만 시 수동 검토 권장
              </span>
            </div>
          </div>
        </div>
        {dismissible && (
          <button
            type="button"
            onClick={handleDismiss}
            className={`rounded-full p-1 hover:bg-black/5 transition-colors ${styles.text}`}
            aria-label="경고 닫기"
          >
            <X className="w-5 h-5" />
          </button>
        )}
      </div>
    </div>
  );
}

export default LowConfidenceWarning;
