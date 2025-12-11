/**
 * T087: Signup → Login → Redirect Flow Tests
 * US9: Role Selection at Signup
 */

import { render, screen, waitFor } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import SignupPage from '@/app/signup/page';
import * as authApi from '@/lib/api/auth';

// Mock next/navigation
const mockPush = jest.fn();
jest.mock('next/navigation', () => ({
  useRouter() {
    return {
      push: mockPush,
      replace: jest.fn(),
      prefetch: jest.fn(),
    };
  },
}));

// Mock auth API
jest.mock('@/lib/api/auth', () => ({
  signup: jest.fn(),
  SignupRole: {},
}));

describe('US9: Signup Page with Role Selection', () => {
  const mockSignup = authApi.signup as jest.MockedFunction<typeof authApi.signup>;

  beforeEach(() => {
    jest.clearAllMocks();
    mockPush.mockClear();
    // Clear cookies
    document.cookie = 'user_data=; path=/; max-age=0';
    localStorage.clear();
  });

  describe('T082: Role dropdown rendering', () => {
    it('renders role dropdown with all options', () => {
      render(<SignupPage />);

      const roleSelect = screen.getByLabelText(/역할/i);
      expect(roleSelect).toBeInTheDocument();

      // Check all options exist
      expect(screen.getByRole('option', { name: '역할을 선택하세요' })).toBeInTheDocument();
      expect(screen.getByRole('option', { name: '변호사' })).toBeInTheDocument();
      expect(screen.getByRole('option', { name: '의뢰인' })).toBeInTheDocument();
      expect(screen.getByRole('option', { name: '탐정' })).toBeInTheDocument();
    });

    it('shows role description when role is selected', async () => {
      const user = userEvent.setup();
      render(<SignupPage />);

      const roleSelect = screen.getByLabelText(/역할/i);
      await user.selectOptions(roleSelect, 'lawyer');

      expect(screen.getByText('사건 관리 및 법률 서비스 제공')).toBeInTheDocument();
    });
  });

  describe('T086: Block signup without role selection', () => {
    it('role select has required attribute', () => {
      render(<SignupPage />);
      const roleSelect = screen.getByLabelText(/역할/i);
      expect(roleSelect).toBeRequired();
    });

    it('default role value is empty (placeholder selected)', () => {
      render(<SignupPage />);
      const roleSelect = screen.getByLabelText(/역할/i) as HTMLSelectElement;
      expect(roleSelect.value).toBe('');
    });

    it('signup API is not called without role selection', async () => {
      const user = userEvent.setup();
      render(<SignupPage />);

      // Fill all fields except role
      await user.type(screen.getByLabelText(/이름/i), '홍길동');
      await user.type(screen.getByLabelText(/이메일/i), 'test@example.com');
      await user.type(screen.getByLabelText(/비밀번호/i), 'password123');
      await user.click(screen.getByLabelText(/이용약관/i));
      await user.click(screen.getByLabelText(/개인정보처리방침/i));

      // Submit without selecting role - HTML5 validation should block
      await user.click(screen.getByRole('button', { name: /무료 체험 시작/i }));

      // API should not be called due to HTML5 required validation
      expect(mockSignup).not.toHaveBeenCalled();
    });
  });

  describe('T083: Signup API includes role parameter', () => {
    it('sends role in signup request', async () => {
      const user = userEvent.setup();
      mockSignup.mockResolvedValue({
        data: {
          access_token: 'test-token',
          token_type: 'bearer',
          user: { id: '1', email: 'test@example.com', name: '홍길동', role: 'lawyer' },
        },
        error: undefined,
        status: 200,
      });

      render(<SignupPage />);

      await user.type(screen.getByLabelText(/이름/i), '홍길동');
      await user.type(screen.getByLabelText(/이메일/i), 'test@example.com');
      await user.selectOptions(screen.getByLabelText(/역할/i), 'lawyer');
      await user.type(screen.getByLabelText(/비밀번호/i), 'password123');
      await user.click(screen.getByLabelText(/이용약관/i));
      await user.click(screen.getByLabelText(/개인정보처리방침/i));
      await user.click(screen.getByRole('button', { name: /무료 체험 시작/i }));

      await waitFor(() => {
        expect(mockSignup).toHaveBeenCalledWith(
          expect.objectContaining({
            name: '홍길동',
            email: 'test@example.com',
            role: 'lawyer',
            password: 'password123',
            accept_terms: true,
            accept_privacy: true,
          })
        );
      });
    });
  });

  describe('T085 & T087: Role-based redirect after signup', () => {
    it('redirects lawyer to /lawyer/dashboard', async () => {
      const user = userEvent.setup();
      mockSignup.mockResolvedValue({
        data: {
          access_token: 'test-token',
          token_type: 'bearer',
          user: { id: '1', email: 'test@example.com', name: '홍길동', role: 'lawyer' },
        },
        error: undefined,
        status: 200,
      });

      render(<SignupPage />);

      await user.type(screen.getByLabelText(/이름/i), '홍길동');
      await user.type(screen.getByLabelText(/이메일/i), 'test@example.com');
      await user.selectOptions(screen.getByLabelText(/역할/i), 'lawyer');
      await user.type(screen.getByLabelText(/비밀번호/i), 'password123');
      await user.click(screen.getByLabelText(/이용약관/i));
      await user.click(screen.getByLabelText(/개인정보처리방침/i));
      await user.click(screen.getByRole('button', { name: /무료 체험 시작/i }));

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/lawyer/dashboard');
      });
    });

    it('redirects client to /client/dashboard', async () => {
      const user = userEvent.setup();
      mockSignup.mockResolvedValue({
        data: {
          access_token: 'test-token',
          token_type: 'bearer',
          user: { id: '2', email: 'client@example.com', name: '김의뢰', role: 'client' },
        },
        error: undefined,
        status: 200,
      });

      render(<SignupPage />);

      await user.type(screen.getByLabelText(/이름/i), '김의뢰');
      await user.type(screen.getByLabelText(/이메일/i), 'client@example.com');
      await user.selectOptions(screen.getByLabelText(/역할/i), 'client');
      await user.type(screen.getByLabelText(/비밀번호/i), 'password123');
      await user.click(screen.getByLabelText(/이용약관/i));
      await user.click(screen.getByLabelText(/개인정보처리방침/i));
      await user.click(screen.getByRole('button', { name: /무료 체험 시작/i }));

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/client/dashboard');
      });
    });

    it('redirects detective to /detective/dashboard', async () => {
      const user = userEvent.setup();
      mockSignup.mockResolvedValue({
        data: {
          access_token: 'test-token',
          token_type: 'bearer',
          user: { id: '3', email: 'detective@example.com', name: '박탐정', role: 'detective' },
        },
        error: undefined,
        status: 200,
      });

      render(<SignupPage />);

      await user.type(screen.getByLabelText(/이름/i), '박탐정');
      await user.type(screen.getByLabelText(/이메일/i), 'detective@example.com');
      await user.selectOptions(screen.getByLabelText(/역할/i), 'detective');
      await user.type(screen.getByLabelText(/비밀번호/i), 'password123');
      await user.click(screen.getByLabelText(/이용약관/i));
      await user.click(screen.getByLabelText(/개인정보처리방침/i));
      await user.click(screen.getByRole('button', { name: /무료 체험 시작/i }));

      await waitFor(() => {
        expect(mockPush).toHaveBeenCalledWith('/detective/dashboard');
      });
    });
  });

  describe('Signup validation', () => {
    it('shows error for password less than 8 characters', async () => {
      const user = userEvent.setup();
      render(<SignupPage />);

      await user.type(screen.getByLabelText(/이름/i), '홍길동');
      await user.type(screen.getByLabelText(/이메일/i), 'test@example.com');
      await user.selectOptions(screen.getByLabelText(/역할/i), 'lawyer');
      await user.type(screen.getByLabelText(/비밀번호/i), 'short');
      await user.click(screen.getByLabelText(/이용약관/i));
      await user.click(screen.getByLabelText(/개인정보처리방침/i));
      await user.click(screen.getByRole('button', { name: /무료 체험 시작/i }));

      expect(screen.getByText('비밀번호는 8자 이상이어야 합니다.')).toBeInTheDocument();
    });

    it('shows error when terms not accepted', async () => {
      const user = userEvent.setup();
      render(<SignupPage />);

      await user.type(screen.getByLabelText(/이름/i), '홍길동');
      await user.type(screen.getByLabelText(/이메일/i), 'test@example.com');
      await user.selectOptions(screen.getByLabelText(/역할/i), 'lawyer');
      await user.type(screen.getByLabelText(/비밀번호/i), 'password123');
      await user.click(screen.getByLabelText(/개인정보처리방침/i));
      await user.click(screen.getByRole('button', { name: /무료 체험 시작/i }));

      expect(screen.getByText('이용약관에 동의해주세요.')).toBeInTheDocument();
    });

    it('shows error when privacy policy not accepted', async () => {
      const user = userEvent.setup();
      render(<SignupPage />);

      await user.type(screen.getByLabelText(/이름/i), '홍길동');
      await user.type(screen.getByLabelText(/이메일/i), 'test@example.com');
      await user.selectOptions(screen.getByLabelText(/역할/i), 'lawyer');
      await user.type(screen.getByLabelText(/비밀번호/i), 'password123');
      await user.click(screen.getByLabelText(/이용약관/i));
      await user.click(screen.getByRole('button', { name: /무료 체험 시작/i }));

      expect(screen.getByText('개인정보처리방침에 동의해주세요.')).toBeInTheDocument();
    });
  });
});
