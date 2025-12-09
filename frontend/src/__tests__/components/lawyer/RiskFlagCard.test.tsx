/**
 * RiskFlagCard Component Tests
 * 010-calm-control-design - TDD compliance tests
 */

import { render, screen } from '@testing-library/react';
import { RiskFlagCard, RiskCase } from '@/components/lawyer/RiskFlagCard';

// Mock next/link
jest.mock('next/link', () => {
  return function MockLink({ children, href }: { children: React.ReactNode; href: string }) {
    return <a href={href}>{children}</a>;
  };
});

describe('RiskFlagCard', () => {
  const mockCases: RiskCase[] = [
    {
      id: 'case-1',
      title: '김철수 vs 이영희 이혼 소송',
      clientName: '김철수',
      riskType: 'violence',
      flaggedAt: '2025-12-09T10:00:00Z',
      description: '가정폭력 이력 확인됨',
    },
    {
      id: 'case-2',
      title: '박민수 vs 정수진 양육권 분쟁',
      clientName: '박민수',
      riskType: 'child',
      flaggedAt: '2025-12-09T09:00:00Z',
    },
    {
      id: 'case-3',
      title: '최성호 vs 한미영 재산분할',
      clientName: '최성호',
      riskType: 'flight',
      flaggedAt: '2025-12-09T08:00:00Z',
    },
  ];

  describe('렌더링', () => {
    it('제목이 "위험 플래그 사건"으로 표시된다', () => {
      render(<RiskFlagCard cases={mockCases} />);
      expect(screen.getByText('위험 플래그 사건')).toBeInTheDocument();
    });

    it('위험 사건 목록이 표시된다', () => {
      render(<RiskFlagCard cases={mockCases} />);
      expect(screen.getByText('김철수 vs 이영희 이혼 소송')).toBeInTheDocument();
      expect(screen.getByText('박민수 vs 정수진 양육권 분쟁')).toBeInTheDocument();
    });

    it('위험 수준 배지가 표시된다', () => {
      render(<RiskFlagCard cases={mockCases} />);
      expect(screen.getByText('폭력 위험')).toBeInTheDocument();
      expect(screen.getByText('아동 관련')).toBeInTheDocument();
    });

    it('클라이언트 이름이 표시된다', () => {
      render(<RiskFlagCard cases={mockCases} />);
      expect(screen.getByText('김철수')).toBeInTheDocument();
    });

    it('설명이 있는 경우 표시된다', () => {
      render(<RiskFlagCard cases={mockCases} />);
      expect(screen.getByText('가정폭력 이력 확인됨')).toBeInTheDocument();
    });

    it('사건 개수가 배지로 표시된다', () => {
      render(<RiskFlagCard cases={mockCases} />);
      expect(screen.getByText('3건')).toBeInTheDocument();
    });
  });

  describe('빈 상태', () => {
    it('사건이 없을 때 빈 상태 메시지가 표시된다', () => {
      render(<RiskFlagCard cases={[]} />);
      expect(screen.getByText('위험 플래그 사건이 없습니다')).toBeInTheDocument();
    });

    it('사건이 없을 때 체크 아이콘이 표시된다', () => {
      render(<RiskFlagCard cases={[]} />);
      expect(screen.getByText('✅')).toBeInTheDocument();
    });
  });

  describe('로딩 상태', () => {
    it('로딩 중일 때 스켈레톤이 표시된다', () => {
      const { container } = render(<RiskFlagCard cases={[]} isLoading={true} />);
      const skeletons = container.querySelectorAll('.animate-pulse');
      expect(skeletons.length).toBeGreaterThan(0);
    });
  });

  describe('링크', () => {
    it('각 사건이 상세 페이지로 링크된다', () => {
      render(<RiskFlagCard cases={mockCases} />);
      const links = screen.getAllByRole('link');
      expect(links[0]).toHaveAttribute('href', '/lawyer/cases/case-1');
    });
  });

  describe('최대 표시 개수', () => {
    it('최대 5개 사건만 표시된다', () => {
      const manyCases: RiskCase[] = Array.from({ length: 10 }, (_, i) => ({
        id: `case-${i}`,
        title: `사건 ${i}`,
        clientName: `의뢰인 ${i}`,
        riskType: 'violence' as const,
        flaggedAt: '2025-12-09T10:00:00Z',
      }));

      render(<RiskFlagCard cases={manyCases} />);
      const links = screen.getAllByRole('link');
      expect(links.length).toBe(5);
    });
  });
});
