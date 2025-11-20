import { render, screen, fireEvent } from '@testing-library/react';
import '@testing-library/jest-dom';
import CaseDetailPage from '@/pages/cases/[id]';

// Case detail page relies on the router query param to know which case is open.
jest.mock('next/router', () => ({
    useRouter: () => ({
        query: { id: 'case-draft-tab' },
    }),
}));

describe('Plan 3.6 - Draft Tab requirements on the case detail page', () => {
    const renderCaseDetail = () => render(<CaseDetailPage />);

    describe('AI disclaimer visibility', () => {
        test('shows the explicit disclaimer that AI generated the draft and lawyers are responsible', () => {
            renderCaseDetail();

            expect(
                screen.getByText(/이 문서는 AI가 생성한 초안이며, 최종 책임은 변호사에게 있습니다\./i),
            ).toBeInTheDocument();
        });
    });

    describe('Zen mode editor shell', () => {
        test('exposes a zen-mode editor surface with no more than one toolbar/panel', () => {
            const { container } = renderCaseDetail();

            const editorSurface = screen.getByTestId('draft-editor-surface');
            expect(editorSurface).toHaveAttribute('data-zen-mode', 'true');

            const toolbarPanels = container.querySelectorAll('[data-testid="draft-toolbar-panel"]');
            expect(toolbarPanels.length).toBeLessThanOrEqual(1);
        });
    });

    describe('Primary generation control', () => {
        test('primary button opens the generation modal', async () => {
            renderCaseDetail();

            const generateButton = screen.getByRole('button', { name: /초안 (재)?생성/i });
            expect(generateButton).toHaveClass('btn-primary');
            expect(generateButton).not.toBeDisabled();

            fireEvent.click(generateButton);

            // 모달이 열려야 함
            expect(await screen.findByText(/Draft 생성 옵션/i)).toBeInTheDocument();
        });
    });

    describe('Plan 3.12 - Draft 생성 옵션 모달', () => {
        test('초안 생성 버튼 클릭 시 증거 선택 모달이 표시되어야 한다', async () => {
            renderCaseDetail();

            const generateButton = screen.getByRole('button', { name: /초안 (재)?생성/i });
            fireEvent.click(generateButton);

            // 모달이 열리고 증거 선택 옵션이 표시되는지 확인
            expect(await screen.findByText(/Draft 생성 옵션/i)).toBeInTheDocument();
            expect(screen.getByText(/초안 작성에 참고할 증거를 선택해주세요/i)).toBeInTheDocument();

            // 증거 목록이 표시되는지 확인
            const evidenceItems = screen.getAllByText(/녹취록_20240501.mp3/i);
            expect(evidenceItems.length).toBeGreaterThan(0);
        });
    });
});
