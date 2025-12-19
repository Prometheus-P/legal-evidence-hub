'use client';

import { useState } from 'react';
import {
  CheckCircle2,
  Circle,
  AlertTriangle,
  Tag,
  MoreHorizontal,
  Link2,
  Trash2,
  Edit3,
  Sparkles,
  User,
} from 'lucide-react';
import { Keypoint, LegalGround, verifyKeypoint } from '@/lib/api/lssp';
import { logger } from '@/lib/logger';

interface KeypointListProps {
  keypoints: Keypoint[];
  legalGrounds: LegalGround[];
  onVerify: (keypointId: string, verified: boolean) => void;
  caseId: string;
}

export function KeypointList({
  keypoints,
  legalGrounds,
  onVerify,
  caseId,
}: KeypointListProps) {
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [verifyingId, setVerifyingId] = useState<string | null>(null);

  const handleVerify = async (keypoint: Keypoint) => {
    const newVerified = !keypoint.user_verified;
    setVerifyingId(keypoint.id);

    try {
      const response = await verifyKeypoint(caseId, keypoint.id, newVerified);
      if (!response.error) {
        onVerify(keypoint.id, newVerified);
      }
    } catch (err) {
      logger.error('Failed to verify keypoint:', err);
    } finally {
      setVerifyingId(null);
    }
  };

  const getSourceIcon = (sourceType: Keypoint['source_type']) => {
    switch (sourceType) {
      case 'ai_extracted':
        return <Sparkles className="w-3.5 h-3.5 text-primary" />;
      case 'user_added':
        return <User className="w-3.5 h-3.5 text-blue-500" />;
      case 'merged':
        return <Link2 className="w-3.5 h-3.5 text-purple-500" />;
    }
  };

  const getSourceLabel = (sourceType: Keypoint['source_type']) => {
    switch (sourceType) {
      case 'ai_extracted':
        return 'AI 추출';
      case 'user_added':
        return '직접 추가';
      case 'merged':
        return '병합됨';
    }
  };

  const getConfidenceColor = (score: number | null) => {
    if (score === null) return 'bg-gray-100 text-gray-600';
    if (score >= 0.8) return 'bg-green-100 text-green-700';
    if (score >= 0.5) return 'bg-yellow-100 text-yellow-700';
    return 'bg-red-100 text-red-700';
  };

  if (keypoints.length === 0) {
    return (
      <div className="text-center py-12">
        <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gray-100 flex items-center justify-center">
          <Tag className="w-8 h-8 text-gray-400" />
        </div>
        <h3 className="text-gray-900 font-medium mb-1">핵심 쟁점이 없습니다</h3>
        <p className="text-sm text-gray-500">
          증거 파일을 업로드하고 AI 추출을 실행하거나,
          <br />
          직접 쟁점을 추가해 보세요.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {keypoints.map((keypoint) => {
        const isExpanded = expandedId === keypoint.id;
        const isVerifying = verifyingId === keypoint.id;
        const linkedGrounds = keypoint.legal_grounds || [];

        return (
          <div
            key={keypoint.id}
            className={`border rounded-xl transition-all ${
              keypoint.user_verified
                ? 'border-green-200 bg-green-50/30'
                : 'border-gray-200 bg-white'
            }`}
          >
            {/* Main row */}
            <div className="p-4 flex items-start space-x-3">
              {/* Verify checkbox */}
              <button
                onClick={() => handleVerify(keypoint)}
                disabled={isVerifying}
                className={`mt-0.5 flex-shrink-0 transition-colors ${
                  keypoint.user_verified
                    ? 'text-green-500 hover:text-green-600'
                    : 'text-gray-300 hover:text-gray-400'
                }`}
                title={keypoint.user_verified ? '검증 취소' : '검증하기'}
              >
                {keypoint.user_verified ? (
                  <CheckCircle2 className="w-5 h-5" />
                ) : (
                  <Circle className="w-5 h-5" />
                )}
              </button>

              {/* Content */}
              <div className="flex-1 min-w-0">
                <p className="text-gray-900 text-sm leading-relaxed">
                  {keypoint.content}
                </p>

                {/* Meta info */}
                <div className="mt-2 flex flex-wrap items-center gap-2">
                  {/* Source type */}
                  <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-600">
                    {getSourceIcon(keypoint.source_type)}
                    <span className="ml-1">{getSourceLabel(keypoint.source_type)}</span>
                  </span>

                  {/* Confidence score */}
                  {keypoint.confidence_score !== null && (
                    <span
                      className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs ${getConfidenceColor(
                        keypoint.confidence_score
                      )}`}
                    >
                      신뢰도 {Math.round(keypoint.confidence_score * 100)}%
                    </span>
                  )}

                  {/* Disputed flag */}
                  {keypoint.is_disputed && (
                    <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-orange-100 text-orange-700">
                      <AlertTriangle className="w-3 h-3 mr-1" />
                      쟁점됨
                    </span>
                  )}

                  {/* Legal grounds */}
                  {linkedGrounds.map((ground) => (
                    <span
                      key={ground.id}
                      className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-primary-light text-primary"
                    >
                      {ground.code}: {ground.name}
                    </span>
                  ))}
                </div>

                {/* Expanded content */}
                {isExpanded && (
                  <div className="mt-4 pt-4 border-t border-gray-100 space-y-3">
                    {/* Evidence extracts */}
                    {keypoint.evidence_extracts && keypoint.evidence_extracts.length > 0 && (
                      <div>
                        <h4 className="text-xs font-medium text-gray-500 mb-2">
                          관련 증거 ({keypoint.evidence_extracts.length}건)
                        </h4>
                        <div className="space-y-2">
                          {keypoint.evidence_extracts.slice(0, 3).map((extract) => (
                            <div
                              key={extract.id}
                              className="p-2 bg-gray-50 rounded-lg text-xs text-gray-600"
                            >
                              <p className="line-clamp-2">{extract.content}</p>
                              {extract.page_number && (
                                <span className="text-gray-400 mt-1 block">
                                  p.{extract.page_number}
                                </span>
                              )}
                            </div>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* Actions */}
                    <div className="flex items-center space-x-2">
                      <button className="flex items-center px-2 py-1 text-xs text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded">
                        <Edit3 className="w-3 h-3 mr-1" />
                        수정
                      </button>
                      <button className="flex items-center px-2 py-1 text-xs text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded">
                        <Link2 className="w-3 h-3 mr-1" />
                        근거 연결
                      </button>
                      <button className="flex items-center px-2 py-1 text-xs text-red-500 hover:text-red-700 hover:bg-red-50 rounded">
                        <Trash2 className="w-3 h-3 mr-1" />
                        삭제
                      </button>
                    </div>
                  </div>
                )}
              </div>

              {/* Expand/More button */}
              <button
                onClick={() => setExpandedId(isExpanded ? null : keypoint.id)}
                className="p-1 text-gray-400 hover:text-gray-600 hover:bg-gray-100 rounded"
              >
                <MoreHorizontal className="w-4 h-4" />
              </button>
            </div>
          </div>
        );
      })}
    </div>
  );
}
