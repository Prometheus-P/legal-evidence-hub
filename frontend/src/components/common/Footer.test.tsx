// src/components/common/Footer.test.tsx
// T060 - FR-020: Copyright footer with legal links
import { render, screen } from '@testing-library/react';
import Footer from './Footer';

describe('Footer 컴포넌트 (T060)', () => {
  it('Footer가 렌더링될 때 주요 법적 링크를 포함해야 한다.', () => {
    render(<Footer />);

    // 주요 링크 존재 여부 확인
    expect(screen.getByText('이용약관')).toBeInTheDocument();
    expect(screen.getByText('개인정보처리방침')).toBeInTheDocument();
    expect(screen.getByText('문의하기')).toBeInTheDocument();
  });

  it('Footer에 Copyright 텍스트가 포함되어야 한다.', () => {
    render(<Footer />);

    // Copyright 텍스트 확인 (연도는 동적으로 변경될 수 있으므로 정규식 사용)
    const year = new Date().getFullYear();
    expect(screen.getByText(new RegExp(`© ${year} Legal Evidence Hub`, 'i'))).toBeInTheDocument();
  });

  it('이용약관 링크가 /terms로 연결되어야 한다.', () => {
    render(<Footer />);
    const termsLink = screen.getByRole('link', { name: '이용약관' });
    expect(termsLink).toHaveAttribute('href', '/terms');
  });

  it('개인정보처리방침 링크가 /privacy로 연결되어야 한다.', () => {
    render(<Footer />);
    const privacyLink = screen.getByRole('link', { name: '개인정보처리방침' });
    expect(privacyLink).toHaveAttribute('href', '/privacy');
  });
});
