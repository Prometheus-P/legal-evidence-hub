import { render, screen } from '@testing-library/react';
import CaseCard from '@/components/cases/CaseCard';
import { Case } from '@/types/case';

describe('Plan 3.3 - Case List Dashboard Requirements', () => {
    const mockCase: Case = {
        id: 'case-123',
        title: '김 vs. 이 이혼 소송',
        clientName: '김철수',
        status: 'open',
        lastUpdated: '2024-05-15T10:30:00Z',
        evidenceCount: 12,
        draftStatus: 'ready',
        createdAt: '2024-01-01T00:00:00Z',
    };

    describe('케이스 카드 필수 정보 표시', () => {
        test('사건명이 표시되어야 한다', () => {
            render(<CaseCard caseData={mockCase} />);
            expect(screen.getByText('김 vs. 이 이혼 소송')).toBeInTheDocument();
        });

        test('최근 업데이트 날짜가 표시되어야 한다', () => {
            render(<CaseCard caseData={mockCase} />);
            // Check for date display (format may vary)
            expect(screen.getByText(/최근 업데이트/i)).toBeInTheDocument();
        });

        test('증거 개수가 표시되어야 한다', () => {
            render(<CaseCard caseData={mockCase} />);
            expect(screen.getByText(/증거 12건/i)).toBeInTheDocument();
        });

        test('Draft 상태가 표시되어야 한다', () => {
            render(<CaseCard caseData={mockCase} />);
            expect(screen.getByText(/draft 상태/i)).toBeInTheDocument();
        });
    });

    describe('카드 레이아웃 색상 규칙', () => {
        test('카드 배경은 Calm Grey 톤을 사용해야 한다', () => {
            const { container } = render(<CaseCard caseData={mockCase} />);
            const card = container.querySelector('.card');

            expect(card).toBeInTheDocument();
            expect(card).toHaveClass('bg-calm-grey');
        });

        test('제목은 Deep Trust Blue 색상을 사용해야 한다', () => {
            const { container } = render(<CaseCard caseData={mockCase} />);
            const title = screen.getByText('김 vs. 이 이혼 소송');

            // Title should use text-deep-trust-blue class
            expect(title).toHaveClass('text-deep-trust-blue');
        });
    });

    describe('카드 hover 효과', () => {
        test('카드는 hover 시 shadow 증가 효과를 가져야 한다', () => {
            const { container } = render(<CaseCard caseData={mockCase} />);
            const card = container.querySelector('.card');

            // Card should have hover:shadow-md or similar class
            expect(card?.className).toMatch(/hover:shadow/);
        });

        test('카드는 hover 시 accent 색상의 ring/glow 효과를 가져야 한다', () => {
            const { container } = render(<CaseCard caseData={mockCase} />);
            const card = container.querySelector('.card');

            // Card should have hover:ring-accent or similar effect
            expect(card?.className).toMatch(/hover:ring.*accent/);
        });
    });
});
