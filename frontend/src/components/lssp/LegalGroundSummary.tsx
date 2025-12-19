'use client';

import { useMemo } from 'react';
import {
  Scale,
  CheckCircle2,
  AlertCircle,
  TrendingUp,
  FileText,
  ChevronRight,
} from 'lucide-react';
import { Keypoint, LegalGround } from '@/lib/api/lssp';

interface LegalGroundSummaryProps {
  caseId: string;
  keypoints: Keypoint[];
  legalGrounds: LegalGround[];
}

interface GroundAnalysis {
  ground: LegalGround;
  keypointCount: number;
  verifiedCount: number;
  strength: 'strong' | 'moderate' | 'weak' | 'none';
}

export function LegalGroundSummary({
  caseId,
  keypoints,
  legalGrounds,
}: LegalGroundSummaryProps) {
  // Analyze keypoints by legal ground
  const analysis = useMemo((): GroundAnalysis[] => {
    return legalGrounds.map((ground) => {
      const linkedKeypoints = keypoints.filter(
        (kp) => kp.legal_grounds?.some((g) => g.id === ground.id)
      );
      const verifiedCount = linkedKeypoints.filter((kp) => kp.user_verified).length;

      let strength: GroundAnalysis['strength'] = 'none';
      if (verifiedCount >= 3) strength = 'strong';
      else if (verifiedCount >= 2) strength = 'moderate';
      else if (verifiedCount >= 1) strength = 'weak';

      return {
        ground,
        keypointCount: linkedKeypoints.length,
        verifiedCount,
        strength,
      };
    });
  }, [keypoints, legalGrounds]);

  const getStrengthBadge = (strength: GroundAnalysis['strength']) => {
    switch (strength) {
      case 'strong':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-green-100 text-green-700">
            <TrendingUp className="w-3 h-3 mr-1" />
            강함
          </span>
        );
      case 'moderate':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-yellow-100 text-yellow-700">
            <TrendingUp className="w-3 h-3 mr-1" />
            보통
          </span>
        );
      case 'weak':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-orange-100 text-orange-700">
            <AlertCircle className="w-3 h-3 mr-1" />
            약함
          </span>
        );
      case 'none':
        return (
          <span className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-gray-100 text-gray-500">
            미확보
          </span>
        );
    }
  };

  const getStrengthColor = (strength: GroundAnalysis['strength']) => {
    switch (strength) {
      case 'strong':
        return 'border-green-200 bg-green-50/50';
      case 'moderate':
        return 'border-yellow-200 bg-yellow-50/50';
      case 'weak':
        return 'border-orange-200 bg-orange-50/50';
      case 'none':
        return 'border-gray-200 bg-gray-50/50';
    }
  };

  // Summary stats
  const totalVerified = keypoints.filter((kp) => kp.user_verified).length;
  const groundsWithEvidence = analysis.filter((a) => a.strength !== 'none').length;

  return (
    <div className="space-y-6">
      {/* Summary cards */}
      <div className="grid grid-cols-3 gap-4">
        <div className="p-4 bg-gray-50 rounded-xl">
          <p className="text-xs text-gray-500 mb-1">적용 가능 법적 근거</p>
          <p className="text-2xl font-bold text-gray-900">
            {groundsWithEvidence}
            <span className="text-sm font-normal text-gray-400">/{legalGrounds.length}</span>
          </p>
        </div>
        <div className="p-4 bg-green-50 rounded-xl">
          <p className="text-xs text-green-600 mb-1">검증된 쟁점</p>
          <p className="text-2xl font-bold text-green-700">
            {totalVerified}
            <span className="text-sm font-normal text-green-400">/{keypoints.length}</span>
          </p>
        </div>
        <div className="p-4 bg-primary-light rounded-xl">
          <p className="text-xs text-primary mb-1">강한 근거</p>
          <p className="text-2xl font-bold text-primary">
            {analysis.filter((a) => a.strength === 'strong').length}
          </p>
        </div>
      </div>

      {/* Legal grounds list */}
      <div className="space-y-3">
        <h3 className="text-sm font-medium text-gray-700">법적 근거별 분석</h3>

        {analysis.map(({ ground, keypointCount, verifiedCount, strength }) => (
          <div
            key={ground.id}
            className={`border rounded-xl p-4 transition-colors ${getStrengthColor(strength)}`}
          >
            <div className="flex items-start justify-between">
              <div className="flex items-start space-x-3">
                <div className="p-2 bg-white rounded-lg shadow-sm">
                  <Scale className="w-5 h-5 text-primary" />
                </div>
                <div>
                  <div className="flex items-center space-x-2">
                    <h4 className="font-medium text-gray-900">
                      {ground.code}. {ground.name}
                    </h4>
                    {getStrengthBadge(strength)}
                  </div>
                  <p className="text-sm text-gray-500 mt-1">{ground.description}</p>

                  {/* Civil code reference */}
                  {ground.civil_code_ref && (
                    <p className="text-xs text-gray-400 mt-1">
                      근거 조문: {ground.civil_code_ref}
                    </p>
                  )}

                  {/* Typical evidence types */}
                  {ground.typical_evidence_types.length > 0 && (
                    <div className="mt-2 flex flex-wrap gap-1">
                      {ground.typical_evidence_types.map((type) => (
                        <span
                          key={type}
                          className="inline-flex items-center px-2 py-0.5 rounded text-xs bg-white text-gray-600 border border-gray-200"
                        >
                          <FileText className="w-3 h-3 mr-1" />
                          {type}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>

              <div className="text-right">
                <div className="flex items-center text-sm text-gray-600">
                  <span className="font-medium">{verifiedCount}</span>
                  <span className="text-gray-400 mx-1">/</span>
                  <span className="text-gray-400">{keypointCount}</span>
                  <span className="text-gray-400 ml-1">쟁점</span>
                </div>
                {keypointCount > 0 && (
                  <div className="mt-1 w-24 h-1.5 bg-gray-200 rounded-full overflow-hidden">
                    <div
                      className="h-full bg-green-500 rounded-full"
                      style={{
                        width: `${keypointCount > 0 ? (verifiedCount / keypointCount) * 100 : 0}%`,
                      }}
                    />
                  </div>
                )}
              </div>
            </div>

            {/* Action button */}
            {strength === 'none' && (
              <div className="mt-3 pt-3 border-t border-gray-200">
                <button className="flex items-center text-sm text-primary hover:text-primary-dark">
                  <span>관련 쟁점 연결하기</span>
                  <ChevronRight className="w-4 h-4 ml-1" />
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {/* Recommendation */}
      {groundsWithEvidence < legalGrounds.length && (
        <div className="p-4 bg-blue-50 border border-blue-200 rounded-xl">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-blue-500 flex-shrink-0 mt-0.5" />
            <div>
              <h4 className="font-medium text-blue-900">추가 증거 확보 권장</h4>
              <p className="text-sm text-blue-700 mt-1">
                {legalGrounds.length - groundsWithEvidence}개의 법적 근거에 대한 쟁점이 부족합니다.
                관련 증거를 추가로 업로드하거나 쟁점을 직접 추가해 보세요.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
