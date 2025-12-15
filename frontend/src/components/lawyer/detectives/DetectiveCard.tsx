/**
 * DetectiveCard Component
 * 011-production-bug-fixes Feature - US2 (T051)
 *
 * Card displaying detective contact information.
 */

'use client';

import React from 'react';
import type { DetectiveContact } from '@/types/investigator';

interface DetectiveCardProps {
  detective: DetectiveContact;
  onEdit?: (detective: DetectiveContact) => void;
  onDelete?: (detectiveId: string) => void;
}

function formatDate(dateString: string): string {
  return new Date(dateString).toLocaleDateString('ko-KR', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export function DetectiveCard({ detective, onEdit, onDelete }: DetectiveCardProps) {
  const { name, phone, email, specialty, memo, created_at } = detective;

  const handleDelete = (e: React.MouseEvent) => {
    e.stopPropagation();
    if (window.confirm(`${name} 탐정을 삭제하시겠습니까?`) && onDelete) {
      onDelete(detective.id);
    }
  };

  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4 shadow-sm transition-shadow hover:shadow-md">
      {/* Header */}
      <div className="flex items-start justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-purple-100 text-purple-600">
            <span className="text-lg font-medium">{name.charAt(0)}</span>
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">{name}</h3>
            <p className="text-xs text-gray-400">등록일: {formatDate(created_at)}</p>
          </div>
        </div>
        <div className="flex gap-1">
          {onEdit && (
            <button
              type="button"
              onClick={() => onEdit(detective)}
              className="rounded p-1.5 text-gray-400 hover:bg-gray-100 hover:text-gray-600"
              aria-label="수정"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"
                />
              </svg>
            </button>
          )}
          {onDelete && (
            <button
              type="button"
              onClick={handleDelete}
              className="rounded p-1.5 text-gray-400 hover:bg-red-50 hover:text-red-600"
              aria-label="삭제"
            >
              <svg className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={2}
                  d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"
                />
              </svg>
            </button>
          )}
        </div>
      </div>

      {/* Specialty */}
      {specialty && (
        <div className="mt-3">
          <span className="inline-flex items-center rounded-full bg-purple-50 px-2.5 py-0.5 text-xs font-medium text-purple-700">
            {specialty}
          </span>
        </div>
      )}

      {/* Contact Info */}
      <div className="mt-4 space-y-2">
        {phone && (
          <div className="flex items-center gap-2 text-sm">
            <svg
              className="h-4 w-4 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"
              />
            </svg>
            <a href={`tel:${phone}`} className="text-gray-700 hover:text-purple-600">
              {phone}
            </a>
          </div>
        )}
        {email && (
          <div className="flex items-center gap-2 text-sm">
            <svg
              className="h-4 w-4 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
              />
            </svg>
            <a href={`mailto:${email}`} className="text-gray-700 hover:text-purple-600">
              {email}
            </a>
          </div>
        )}
      </div>

      {/* Memo */}
      {memo && (
        <div className="mt-3 border-t border-gray-100 pt-3">
          <p className="line-clamp-2 text-sm text-gray-500">{memo}</p>
        </div>
      )}
    </div>
  );
}

export default DetectiveCard;
