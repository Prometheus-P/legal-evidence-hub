/**
 * DetectiveForm Component
 * 011-production-bug-fixes Feature - US2 (T052)
 *
 * Form for adding/editing detective contacts.
 */

'use client';

import React, { useState, useEffect } from 'react';
import type { DetectiveContact, DetectiveContactCreate, DetectiveContactUpdate } from '@/types/investigator';

interface DetectiveFormProps {
  detective?: DetectiveContact | null;
  onSubmit: (data: DetectiveContactCreate | DetectiveContactUpdate) => Promise<void>;
  onCancel: () => void;
  isSubmitting?: boolean;
}

const SPECIALTIES = [
  '불륜 조사',
  '자산 추적',
  '실종자 수색',
  '배경 조사',
  '보험 조사',
  '기업 조사',
  '기타',
];

export function DetectiveForm({
  detective,
  onSubmit,
  onCancel,
  isSubmitting = false,
}: DetectiveFormProps) {
  const [name, setName] = useState('');
  const [phone, setPhone] = useState('');
  const [email, setEmail] = useState('');
  const [specialty, setSpecialty] = useState('');
  const [memo, setMemo] = useState('');
  const [errors, setErrors] = useState<{ [key: string]: string }>({});

  const isEditMode = !!detective;

  useEffect(() => {
    if (detective) {
      setName(detective.name || '');
      setPhone(detective.phone || '');
      setEmail(detective.email || '');
      setSpecialty(detective.specialty || '');
      setMemo(detective.memo || '');
    }
  }, [detective]);

  const validate = (): boolean => {
    const newErrors: { [key: string]: string } = {};

    if (!name.trim()) {
      newErrors.name = '이름을 입력하세요';
    }
    if (!phone.trim() && !email.trim()) {
      newErrors.phone = '전화번호 또는 이메일 중 하나는 필수입니다';
      newErrors.email = '전화번호 또는 이메일 중 하나는 필수입니다';
    }
    if (email.trim() && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
      newErrors.email = '올바른 이메일 형식을 입력하세요';
    }
    if (phone.trim() && !/^[\d-+() ]+$/.test(phone)) {
      newErrors.phone = '올바른 전화번호 형식을 입력하세요';
    }

    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!validate()) return;

    const data: DetectiveContactCreate | DetectiveContactUpdate = {
      name: name.trim(),
      phone: phone.trim() || undefined,
      email: email.trim() || undefined,
      specialty: specialty.trim() || undefined,
      memo: memo.trim() || undefined,
    };

    await onSubmit(data);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
      <div className="w-full max-w-md rounded-lg bg-white shadow-xl">
        {/* Header */}
        <div className="flex items-center justify-between border-b border-gray-200 px-6 py-4">
          <h2 className="text-lg font-semibold text-gray-900">
            {isEditMode ? '탐정 수정' : '탐정 추가'}
          </h2>
          <button
            type="button"
            onClick={onCancel}
            className="text-gray-400 hover:text-gray-600"
            aria-label="닫기"
          >
            <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M6 18L18 6M6 6l12 12"
              />
            </svg>
          </button>
        </div>

        {/* Form */}
        <form onSubmit={handleSubmit} className="p-6">
          <div className="space-y-4">
            {/* Name */}
            <div>
              <label
                htmlFor="name"
                className="mb-1 block text-sm font-medium text-gray-700"
              >
                이름 <span className="text-red-500">*</span>
              </label>
              <input
                id="name"
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="탐정 이름"
                className={`w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-1 ${
                  errors.name
                    ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
                    : 'border-gray-300 focus:border-purple-500 focus:ring-purple-500'
                }`}
              />
              {errors.name && (
                <p className="mt-1 text-xs text-red-500">{errors.name}</p>
              )}
            </div>

            {/* Phone */}
            <div>
              <label
                htmlFor="phone"
                className="mb-1 block text-sm font-medium text-gray-700"
              >
                전화번호
              </label>
              <input
                id="phone"
                type="tel"
                value={phone}
                onChange={(e) => setPhone(e.target.value)}
                placeholder="010-1234-5678"
                className={`w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-1 ${
                  errors.phone
                    ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
                    : 'border-gray-300 focus:border-purple-500 focus:ring-purple-500'
                }`}
              />
              {errors.phone && (
                <p className="mt-1 text-xs text-red-500">{errors.phone}</p>
              )}
            </div>

            {/* Email */}
            <div>
              <label
                htmlFor="email"
                className="mb-1 block text-sm font-medium text-gray-700"
              >
                이메일
              </label>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="example@email.com"
                className={`w-full rounded-lg border px-3 py-2 text-sm focus:outline-none focus:ring-1 ${
                  errors.email
                    ? 'border-red-500 focus:border-red-500 focus:ring-red-500'
                    : 'border-gray-300 focus:border-purple-500 focus:ring-purple-500'
                }`}
              />
              {errors.email && (
                <p className="mt-1 text-xs text-red-500">{errors.email}</p>
              )}
            </div>

            {/* Specialty */}
            <div>
              <label
                htmlFor="specialty"
                className="mb-1 block text-sm font-medium text-gray-700"
              >
                전문 분야
              </label>
              <select
                id="specialty"
                value={specialty}
                onChange={(e) => setSpecialty(e.target.value)}
                className="w-full rounded-lg border border-gray-300 bg-white px-3 py-2 text-sm focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
              >
                <option value="">선택하세요</option>
                {SPECIALTIES.map((s) => (
                  <option key={s} value={s}>
                    {s}
                  </option>
                ))}
              </select>
            </div>

            {/* Memo */}
            <div>
              <label
                htmlFor="memo"
                className="mb-1 block text-sm font-medium text-gray-700"
              >
                메모
              </label>
              <textarea
                id="memo"
                value={memo}
                onChange={(e) => setMemo(e.target.value)}
                placeholder="탐정에 대한 메모 (선택사항)"
                rows={3}
                className="w-full resize-none rounded-lg border border-gray-300 px-3 py-2 text-sm focus:border-purple-500 focus:outline-none focus:ring-1 focus:ring-purple-500"
              />
            </div>
          </div>

          {/* Actions */}
          <div className="mt-6 flex justify-end gap-3">
            <button
              type="button"
              onClick={onCancel}
              disabled={isSubmitting}
              className="rounded-lg border border-gray-300 px-4 py-2 text-sm text-gray-700 hover:bg-gray-50 disabled:opacity-50"
            >
              취소
            </button>
            <button
              type="submit"
              disabled={isSubmitting}
              className="rounded-lg bg-purple-600 px-4 py-2 text-sm text-white hover:bg-purple-700 disabled:opacity-50"
            >
              {isSubmitting ? (
                <span className="flex items-center gap-2">
                  <span className="h-4 w-4 animate-spin rounded-full border-2 border-white border-t-transparent" />
                  저장 중...
                </span>
              ) : isEditMode ? (
                '수정'
              ) : (
                '추가'
              )}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}

export default DetectiveForm;
