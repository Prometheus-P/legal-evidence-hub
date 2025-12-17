/**
 * ShareSummaryModal Component
 * US8 - 진행 상태 요약 카드 (Progress Summary Cards)
 *
 * Modal for sharing case summary via email
 */

'use client';

import { useState } from 'react';
import { X, Send, Mail } from 'lucide-react';

interface ShareSummaryModalProps {
  caseId: string;
  caseTitle: string;
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: () => void;
}

export default function ShareSummaryModal({
  caseId,
  caseTitle,
  isOpen,
  onClose,
  onSuccess,
}: ShareSummaryModalProps) {
  const [email, setEmail] = useState('');
  const [recipientName, setRecipientName] = useState('');
  const [message, setMessage] = useState('');
  const [includePdf, setIncludePdf] = useState(true);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email) {
      setError('이메일 주소를 입력해주세요.');
      return;
    }

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
      setError('올바른 이메일 주소를 입력해주세요.');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Note: Email sending functionality would be implemented on the backend
      // For MVP, we show a success message and copy the share link
      // In production, this would call a /cases/{caseId}/summary/share endpoint

      // Simulate API call delay
      await new Promise(resolve => setTimeout(resolve, 1000));

      // For MVP: Show success and provide manual sharing option
      alert(`요약 카드가 준비되었습니다.\n\n수신자: ${recipientName || email}\n이메일: ${email}\n\n현재 이메일 발송 기능은 개발 중입니다.\nPDF를 다운로드하여 직접 전송해주세요.`);

      onSuccess?.();
      handleClose();
    } catch (err) {
      setError('전송에 실패했습니다. 다시 시도해주세요.');
    } finally {
      setLoading(false);
    }
  };

  const handleClose = () => {
    setEmail('');
    setRecipientName('');
    setMessage('');
    setIncludePdf(true);
    setError(null);
    onClose();
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto">
      {/* Backdrop */}
      <div
        className="fixed inset-0 bg-black/50 transition-opacity"
        onClick={handleClose}
      />

      {/* Modal */}
      <div className="flex min-h-full items-center justify-center p-4">
        <div className="relative w-full max-w-md bg-white dark:bg-neutral-800 rounded-lg shadow-xl">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-neutral-200 dark:border-neutral-700">
            <div className="flex items-center gap-2">
              <Mail className="w-5 h-5 text-primary" />
              <h2 className="text-lg font-semibold text-neutral-900 dark:text-white">
                의뢰인에게 전송
              </h2>
            </div>
            <button
              onClick={handleClose}
              className="p-2 text-neutral-400 hover:text-neutral-600 dark:hover:text-neutral-200"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Content */}
          <form onSubmit={handleSubmit} className="p-4 space-y-4">
            <div className="text-sm text-neutral-600 dark:text-neutral-400 bg-neutral-100 dark:bg-neutral-700/50 p-3 rounded-lg">
              <strong>{caseTitle}</strong> 사건의 진행 현황 요약을 전송합니다.
            </div>

            {error && (
              <div className="text-sm text-red-500 bg-red-50 dark:bg-red-900/20 p-3 rounded-lg">
                {error}
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                수신자 이름 (선택)
              </label>
              <input
                type="text"
                value={recipientName}
                onChange={(e) => setRecipientName(e.target.value)}
                placeholder="예: 김민수"
                className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md dark:bg-neutral-700 text-neutral-900 dark:text-white text-sm focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                이메일 주소 <span className="text-red-500">*</span>
              </label>
              <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="client@example.com"
                required
                className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md dark:bg-neutral-700 text-neutral-900 dark:text-white text-sm focus:ring-2 focus:ring-primary focus:border-transparent"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-neutral-700 dark:text-neutral-300 mb-1">
                메시지 (선택)
              </label>
              <textarea
                value={message}
                onChange={(e) => setMessage(e.target.value)}
                placeholder="의뢰인에게 전달할 메시지를 입력하세요."
                rows={3}
                maxLength={500}
                className="w-full px-3 py-2 border border-neutral-300 dark:border-neutral-600 rounded-md dark:bg-neutral-700 text-neutral-900 dark:text-white text-sm resize-none focus:ring-2 focus:ring-primary focus:border-transparent"
              />
              <div className="text-right text-xs text-neutral-400 mt-1">
                {message.length}/500
              </div>
            </div>

            <div className="flex items-center gap-2">
              <input
                type="checkbox"
                id="includePdf"
                checked={includePdf}
                onChange={(e) => setIncludePdf(e.target.checked)}
                className="w-4 h-4 text-primary border-neutral-300 rounded focus:ring-primary"
              />
              <label
                htmlFor="includePdf"
                className="text-sm text-neutral-700 dark:text-neutral-300"
              >
                PDF 파일 첨부
              </label>
            </div>
          </form>

          {/* Footer */}
          <div className="flex justify-end gap-3 p-4 border-t border-neutral-200 dark:border-neutral-700">
            <button
              type="button"
              onClick={handleClose}
              className="px-4 py-2 text-sm text-neutral-600 dark:text-neutral-400 hover:bg-neutral-100 dark:hover:bg-neutral-700 rounded-md transition-colors"
            >
              취소
            </button>
            <button
              onClick={handleSubmit}
              disabled={loading || !email}
              className="flex items-center gap-2 px-4 py-2 text-sm bg-primary text-white rounded-md hover:bg-primary-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <span className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin" />
                  전송 중...
                </>
              ) : (
                <>
                  <Send className="w-4 h-4" />
                  전송
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
