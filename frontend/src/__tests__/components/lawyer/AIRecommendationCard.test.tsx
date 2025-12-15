/**
 * AIRecommendationCard Component Tests
 * 010-calm-control-design - TDD compliance tests
 */

import { render, screen } from '@testing-library/react';
import { AIRecommendationCard, AIRecommendation } from '@/components/lawyer/AIRecommendationCard';
import { getCaseDetailPath, getLawyerCasePath } from '@/lib/portalPaths';

// Mock next/link
jest.mock('next/link', () => {
  return function MockLink({ children, href }: { children: React.ReactNode; href: string }) {
    return <a href={href}>{children}</a>;
  };
});

describe('AIRecommendationCard', () => {
  const mockRecommendations: AIRecommendation[] = [
    {
      id: 'rec-1',
      type: 'draft_review',
      caseId: 'case-1',
      caseTitle: '김철수 vs 이영희 이혼 소송',
      description: '초안 검토가 필요합니다. 재산분할 조항을 확인해주세요.',
      priority: 'high',
      createdAt: '2025-12-09T10:00:00Z',
    },
    {
      id: 'rec-2',
      type: 'evidence_tagging',
      caseId: 'case-2',
      caseTitle: '박민수 vs 정수진 양육권 분쟁',
      description: '새로운 증거 3건에 태그가 필요합니다.',
      priority: 'medium',
      createdAt: '2025-12-09T09:00:00Z',
    },
    {
      id: 'rec-3',
      type: 'asset_incomplete',
      caseId: 'case-3',
      caseTitle: '최성호 vs 한미영 재산분할',
      description: '부동산 정보가 누락되었습니다.',
      priority: 'low',
      createdAt: '2025-12-09T08:00:00Z',
    },
  ];

  describe('렌더링', () => {
    it('제목이 "AI 추천 작업"으로 표시된다', () => {
      render(<AIRecommendationCard recommendations={mockRecommendations} />);
      expect(screen.getByText('AI 추천 작업')).toBeInTheDocument();
    });

    it('"미리보기 전용" 라벨이 표시된다 (No Auto-Submit 원칙)', () => {
      render(<AIRecommendationCard recommendations={mockRecommendations} />);
      expect(screen.getByText('미리보기 전용')).toBeInTheDocument();
    });

    it('수동 검토 안내 문구가 표시된다', () => {
      render(<AIRecommendationCard recommendations={mockRecommendations} />);
      expect(
        screen.getByText(/모든 작업은 수동 검토 후 진행됩니다/)
      ).toBeInTheDocument();
    });

    it('추천 목록이 표시된다', () => {
      render(<AIRecommendationCard recommendations={mockRecommendations} />);
      expect(screen.getByText('김철수 vs 이영희 이혼 소송')).toBeInTheDocument();
      expect(screen.getByText('박민수 vs 정수진 양육권 분쟁')).toBeInTheDocument();
    });

    it('AI 제안 배지가 표시된다', () => {
      render(<AIRecommendationCard recommendations={mockRecommendations} />);
      const badges = screen.getAllByText('AI 제안');
      expect(badges.length).toBeGreaterThan(0);
    });

    it('작업 유형 라벨이 표시된다', () => {
      render(<AIRecommendationCard recommendations={mockRecommendations} />);
      expect(screen.getByText('초안 검토')).toBeInTheDocument();
      expect(screen.getByText('증거 태깅')).toBeInTheDocument();
    });

    it('설명이 표시된다', () => {
      render(<AIRecommendationCard recommendations={mockRecommendations} />);
      expect(screen.getByText(/초안 검토가 필요합니다/)).toBeInTheDocument();
    });

    it('액션 버튼이 표시된다', () => {
      render(<AIRecommendationCard recommendations={mockRecommendations} />);
      expect(screen.getByText('검토하기')).toBeInTheDocument();
      expect(screen.getByText('태깅하기')).toBeInTheDocument();
    });
  });

  describe('빈 상태', () => {
    it('추천이 없을 때 빈 상태 메시지가 표시된다', () => {
      render(<AIRecommendationCard recommendations={[]} />);
      expect(screen.getByText('현재 추천 작업이 없습니다')).toBeInTheDocument();
    });

    it('추천이 없을 때 아이콘이 표시된다', () => {
      render(<AIRecommendationCard recommendations={[]} />);
      expect(screen.getByText('👍')).toBeInTheDocument();
    });
  });

  describe('로딩 상태', () => {
    it('로딩 중일 때 스켈레톤이 표시된다', () => {
      const { container } = render(
        <AIRecommendationCard recommendations={[]} isLoading={true} />
      );
      const skeletons = container.querySelectorAll('.animate-pulse');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe('링크', () => {
    it('draft_review 타입은 draft 탭으로 링크된다', () => {
      render(<AIRecommendationCard recommendations={[mockRecommendations[0]]} />);
      const link = screen.getByText('검토하기').closest('a');
      expect(link).toHaveAttribute('href', getCaseDetailPath('lawyer', 'case-1', { tab: 'draft' }));
    });

    it('evidence_tagging 타입은 evidence 탭으로 링크된다', () => {
      render(<AIRecommendationCard recommendations={[mockRecommendations[1]]} />);
      const link = screen.getByText('태깅하기').closest('a');
      expect(link).toHaveAttribute(
        'href',
        getCaseDetailPath('lawyer', 'case-2', { tab: 'evidence' })
      );
    });

    it('asset_incomplete 타입은 assets 페이지로 링크된다', () => {
      render(<AIRecommendationCard recommendations={[mockRecommendations[2]]} />);
      const link = screen.getByText('입력하기').closest('a');
      expect(link).toHaveAttribute('href', getLawyerCasePath('assets', 'case-3'));
    });
  });

  describe('최대 표시 개수', () => {
    it('최대 5개 추천만 표시된다', () => {
      const manyRecs: AIRecommendation[] = Array.from({ length: 10 }, (_, i) => ({
        id: `rec-${i}`,
        type: 'draft_review' as const,
        caseId: `case-${i}`,
        caseTitle: `사건 ${i}`,
        description: `설명 ${i}`,
        priority: 'medium' as const,
        createdAt: '2025-12-09T10:00:00Z',
      }));

      render(<AIRecommendationCard recommendations={manyRecs} />);
      const buttons = screen.getAllByText('검토하기');
      expect(buttons.length).toBe(5);
    });
  });
});
