/**
 * ConsultationHistoryTab Component
 * Case Detail - Consultation History Tab
 *
 * Issue #399: 백엔드 API 연동
 * Manages consultation records with clients for a case.
 */

'use client';

import { useState, useCallback, useEffect } from 'react';
import { MessageSquare, Phone, Video, Users, Calendar, Clock, Edit2, Trash2, Plus, X, Loader2 } from 'lucide-react';
import toast from 'react-hot-toast';
import type { Consultation, ConsultationType } from '@/types/consultation';
import {
  getConsultations,
  createConsultation,
  updateConsultation,
  deleteConsultation,
} from '@/lib/api/consultation';

interface ConsultationHistoryTabProps {
  caseId: string;
  /** External control to open the modal directly */
  externalOpenModal?: boolean;
  /** Callback when modal is closed externally */
  onExternalModalClose?: () => void;
}

const CONSULTATION_TYPES: Record<ConsultationType, { label: string; icon: typeof Phone; color: string }> = {
  phone: { label: '전화 상담', icon: Phone, color: 'text-blue-600 bg-blue-100 dark:bg-blue-900/30' },
  in_person: { label: '대면 상담', icon: Users, color: 'text-green-600 bg-green-100 dark:bg-green-900/30' },
  online: { label: '화상 상담', icon: Video, color: 'text-purple-600 bg-purple-100 dark:bg-purple-900/30' },
};

export function ConsultationHistoryTab({ caseId, externalOpenModal, onExternalModalClose }: ConsultationHistoryTabProps) {
  const [consultations, setConsultations] = useState<Consultation[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingConsultation, setEditingConsultation] = useState<Consultation | null>(null);
  const [formData, setFormData] = useState({
    date: '',
    time: '',
    type: 'phone' as ConsultationType,
    participants: '',
    summary: '',
    notes: '',
  });

  const resetForm = useCallback(() => {
    setFormData({
      date: '',
      time: '',
      type: 'phone',
      participants: '',
      summary: '',
      notes: '',
    });
    setEditingConsultation(null);
  }, []);

  const handleOpenModal = useCallback((consultation?: Consultation) => {
    if (consultation) {
      setEditingConsultation(consultation);
      setFormData({
        date: consultation.date,
        time: consultation.time ? consultation.time.substring(0, 5) : '',
        type: consultation.type,
        participants: consultation.participants.join(', '),
        summary: consultation.summary,
        notes: consultation.notes || '',
      });
    } else {
      resetForm();
    }
    setIsModalOpen(true);
  }, [resetForm]);

  // Fetch consultations on mount
  const fetchConsultations = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await getConsultations(caseId);
      if (response.data) {
        setConsultations(response.data.consultations);
      } else if (response.error) {
        toast.error(response.error);
      }
    } catch {
      toast.error('상담내역을 불러오는데 실패했습니다.');
    } finally {
      setIsLoading(false);
    }
  }, [caseId]);

  useEffect(() => {
    fetchConsultations();
  }, [fetchConsultations]);

  // Handle external modal open
  useEffect(() => {
    if (externalOpenModal) {
      handleOpenModal();
    }
  }, [externalOpenModal, handleOpenModal]);

  const handleCloseModal = useCallback(() => {
    setIsModalOpen(false);
    resetForm();
    // Notify parent when modal closes (for external control)
    onExternalModalClose?.();
  }, [resetForm, onExternalModalClose]);

  const handleSubmit = useCallback(async (e: React.FormEvent) => {
    e.preventDefault();

    if (!formData.date || !formData.summary) {
      toast.error('날짜와 요약은 필수입니다.');
      return;
    }

    const participantsList = formData.participants
      .split(',')
      .map(p => p.trim())
      .filter(p => p.length > 0);

    setIsSubmitting(true);

    try {
      if (editingConsultation) {
        const response = await updateConsultation(caseId, editingConsultation.id, {
          date: formData.date,
          time: formData.time || undefined,
          type: formData.type,
          participants: participantsList,
          summary: formData.summary,
          notes: formData.notes || undefined,
        });

        if (response.data) {
          setConsultations(prev => prev.map(c =>
            c.id === editingConsultation.id ? response.data! : c
          ));
          toast.success('상담내역이 수정되었습니다.');
          handleCloseModal();
        } else if (response.error) {
          toast.error(response.error);
        }
      } else {
        const response = await createConsultation(caseId, {
          date: formData.date,
          time: formData.time || undefined,
          type: formData.type,
          participants: participantsList,
          summary: formData.summary,
          notes: formData.notes || undefined,
        });

        if (response.data) {
          setConsultations(prev => [response.data!, ...prev]);
          toast.success('상담내역이 추가되었습니다.');
          handleCloseModal();
        } else if (response.error) {
          toast.error(response.error);
        }
      }
    } catch {
      toast.error('저장에 실패했습니다.');
    } finally {
      setIsSubmitting(false);
    }
  }, [caseId, formData, editingConsultation, handleCloseModal]);

  const handleDelete = useCallback(async (id: string) => {
    if (!confirm('이 상담내역을 삭제하시겠습니까?')) {
      return;
    }

    try {
      const response = await deleteConsultation(caseId, id);
      if (response.status === 204 || !response.error) {
        setConsultations(prev => prev.filter(c => c.id !== id));
        toast.success('상담내역이 삭제되었습니다.');
      } else if (response.error) {
        toast.error(response.error);
      }
    } catch {
      toast.error('삭제에 실패했습니다.');
    }
  }, [caseId]);

  const formatTime = (time: string | null): string => {
    if (!time) return '';
    return time.substring(0, 5);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center py-12">
        <Loader2 className="w-8 h-8 animate-spin text-[var(--color-primary)]" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-bold text-[var(--color-text-primary)]">상담내역</h3>
          <p className="text-sm text-[var(--color-text-secondary)]">의뢰인과의 상담 기록을 관리합니다.</p>
        </div>
        <button
          onClick={() => handleOpenModal()}
          className="inline-flex items-center px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] transition-colors text-sm"
        >
          <Plus className="w-4 h-4 mr-2" />
          상담 추가
        </button>
      </div>

      {/* Consultation List */}
      {consultations.length > 0 ? (
        <div className="space-y-4">
          {consultations.map((consultation) => {
            const typeConfig = CONSULTATION_TYPES[consultation.type];
            const TypeIcon = typeConfig.icon;

            return (
              <div
                key={consultation.id}
                className="bg-white dark:bg-neutral-800 border border-gray-200 dark:border-neutral-700 rounded-lg p-4 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start justify-between">
                  <div className="flex items-start space-x-4">
                    <div className={`p-2 rounded-lg ${typeConfig.color}`}>
                      <TypeIcon className="w-5 h-5" />
                    </div>
                    <div className="flex-1">
                      <div className="flex items-center space-x-2 mb-1">
                        <span className="font-medium text-[var(--color-text-primary)]">
                          {typeConfig.label}
                        </span>
                        <span className="text-sm text-[var(--color-text-secondary)]">
                          <Calendar className="w-3 h-3 inline mr-1" />
                          {consultation.date}
                          {consultation.time && (
                            <>
                              <Clock className="w-3 h-3 inline ml-2 mr-1" />
                              {formatTime(consultation.time)}
                            </>
                          )}
                        </span>
                      </div>
                      {consultation.participants.length > 0 && (
                        <p className="text-sm text-[var(--color-text-secondary)] mb-2">
                          <Users className="w-3 h-3 inline mr-1" />
                          참석자: {consultation.participants.join(', ')}
                        </p>
                      )}
                      <p className="text-[var(--color-text-primary)]">{consultation.summary}</p>
                      {consultation.notes && (
                        <p className="text-sm text-[var(--color-text-secondary)] mt-2 p-2 bg-gray-50 dark:bg-neutral-900/50 rounded">
                          {consultation.notes}
                        </p>
                      )}
                      {consultation.created_by_name && (
                        <p className="text-xs text-[var(--color-text-secondary)] mt-2">
                          작성자: {consultation.created_by_name}
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="flex items-center space-x-2">
                    <button
                      onClick={() => handleOpenModal(consultation)}
                      className="p-2 text-[var(--color-text-secondary)] hover:text-[var(--color-primary)] rounded-lg hover:bg-gray-100 dark:hover:bg-neutral-700"
                      title="수정"
                    >
                      <Edit2 className="w-4 h-4" />
                    </button>
                    <button
                      onClick={() => handleDelete(consultation.id)}
                      className="p-2 text-[var(--color-text-secondary)] hover:text-red-500 rounded-lg hover:bg-gray-100 dark:hover:bg-neutral-700"
                      title="삭제"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </div>
            );
          })}
        </div>
      ) : (
        <div className="text-center py-12 bg-gray-50 dark:bg-neutral-900/50 rounded-lg">
          <MessageSquare className="w-12 h-12 mx-auto mb-4 text-gray-400 dark:text-neutral-500" />
          <p className="text-[var(--color-text-secondary)]">
            아직 상담내역이 없습니다.
          </p>
          <p className="text-sm text-[var(--color-text-secondary)] mt-1">
            상담 추가 버튼을 눌러 첫 상담을 기록하세요.
          </p>
        </div>
      )}

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50">
          <div className="bg-white dark:bg-neutral-800 rounded-xl shadow-xl w-full max-w-lg mx-4">
            <div className="flex items-center justify-between p-4 border-b border-gray-200 dark:border-neutral-700">
              <h4 className="text-lg font-semibold text-[var(--color-text-primary)]">
                {editingConsultation ? '상담내역 수정' : '상담 추가'}
              </h4>
              <button
                onClick={handleCloseModal}
                className="p-2 text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] rounded-lg hover:bg-gray-100 dark:hover:bg-neutral-700"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            <form onSubmit={handleSubmit} className="p-4 space-y-4">
              {/* Date and Time */}
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
                    날짜 <span className="text-red-500">*</span>
                  </label>
                  <input
                    type="date"
                    value={formData.date}
                    onChange={(e) => setFormData(prev => ({ ...prev, date: e.target.value }))}
                    className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                    required
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
                    시간
                  </label>
                  <input
                    type="time"
                    value={formData.time}
                    onChange={(e) => setFormData(prev => ({ ...prev, time: e.target.value }))}
                    className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                  />
                </div>
              </div>

              {/* Type */}
              <div>
                <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
                  상담 유형
                </label>
                <select
                  value={formData.type}
                  onChange={(e) => setFormData(prev => ({ ...prev, type: e.target.value as ConsultationType }))}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                >
                  <option value="phone">전화 상담</option>
                  <option value="in_person">대면 상담</option>
                  <option value="online">화상 상담</option>
                </select>
              </div>

              {/* Participants */}
              <div>
                <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
                  참석자 (쉼표로 구분)
                </label>
                <input
                  type="text"
                  value={formData.participants}
                  onChange={(e) => setFormData(prev => ({ ...prev, participants: e.target.value }))}
                  placeholder="홍길동, 김변호사"
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)]"
                />
              </div>

              {/* Summary */}
              <div>
                <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
                  요약 <span className="text-red-500">*</span>
                </label>
                <textarea
                  value={formData.summary}
                  onChange={(e) => setFormData(prev => ({ ...prev, summary: e.target.value }))}
                  placeholder="상담 내용 요약을 입력하세요"
                  rows={3}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] resize-none"
                  required
                />
              </div>

              {/* Notes */}
              <div>
                <label className="block text-sm font-medium text-[var(--color-text-primary)] mb-1">
                  메모
                </label>
                <textarea
                  value={formData.notes}
                  onChange={(e) => setFormData(prev => ({ ...prev, notes: e.target.value }))}
                  placeholder="추가 메모 (선택)"
                  rows={2}
                  className="w-full px-3 py-2 rounded-lg border border-gray-300 dark:border-neutral-600 bg-white dark:bg-neutral-700 text-[var(--color-text-primary)] focus:outline-none focus:ring-2 focus:ring-[var(--color-primary)] resize-none"
                />
              </div>

              {/* Actions */}
              <div className="flex justify-end space-x-3 pt-4">
                <button
                  type="button"
                  onClick={handleCloseModal}
                  disabled={isSubmitting}
                  className="px-4 py-2 text-[var(--color-text-secondary)] hover:text-[var(--color-text-primary)] rounded-lg border border-gray-300 dark:border-neutral-600 hover:bg-gray-100 dark:hover:bg-neutral-700 transition-colors disabled:opacity-50"
                >
                  취소
                </button>
                <button
                  type="submit"
                  disabled={isSubmitting}
                  className="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg hover:bg-[var(--color-primary-hover)] transition-colors disabled:opacity-50 flex items-center"
                >
                  {isSubmitting && <Loader2 className="w-4 h-4 mr-2 animate-spin" />}
                  {editingConsultation ? '수정' : '추가'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}

export default ConsultationHistoryTab;
