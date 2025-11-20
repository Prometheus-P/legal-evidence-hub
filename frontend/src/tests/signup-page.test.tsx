import { render, screen } from '@testing-library/react';
import SignupPage from '@/pages/signup';

// useRouter 모의(mock) 설정
jest.mock('next/router', () => ({
  useRouter() {
    return {
      route: '/signup',
      pathname: '/signup',
      query: '',
      asPath: '/signup',
    };
  },
}));

describe('plan 3.8: 회원가입 페이지', () => {
  it('"/signup" 경로에 접근했을 때, 회원가입 페이지의 주요 요소들이 렌더링되어야 한다.', () => {
    render(<SignupPage />);

    // 1. "회원가입" 제목이 표시되는지 확인
    const heading = screen.getByRole('heading', { name: /회원가입/i });
    expect(heading).toBeInTheDocument();

    // 2. 이메일, 비밀번호, 이름 입력 필드가 존재하는지 확인
    const emailInput = screen.getByLabelText(/이메일/i);
    const passwordInput = screen.getByLabelText(/^비밀번호$/i);
    const passwordConfirmInput = screen.getByLabelText(/비밀번호 확인/i);
    const nameInput = screen.getByLabelText(/이름/i);
    
    expect(emailInput).toBeInTheDocument();
    expect(passwordInput).toBeInTheDocument();
    expect(passwordConfirmInput).toBeInTheDocument();
    expect(nameInput).toBeInTheDocument();

    // 3. 이용약관 동의 체크박스와 회원가입 버튼이 존재하는지 확인
    const termsCheckbox = screen.getByRole('checkbox', { name: /이용약관에 동의합니다/i });
    const signupButton = screen.getByRole('button', { name: /회원가입/i });

    expect(termsCheckbox).toBeInTheDocument();
    expect(signupButton).toBeInTheDocument();
  });
});
