// src/pages/signup.tsx
import type { NextPage } from 'next';
import Head from 'next/head';

const SignupPage: NextPage = () => {
  return (
    <div className="container mx-auto px-4 py-8">
      <Head>
        <title>회원가입 - Legal Evidence Hub</title>
      </Head>

      <div className="max-w-md mx-auto">
        <h1 className="text-3xl font-bold text-center mb-8">회원가입</h1>
        <form>
          <div className="mb-4">
            <label htmlFor="name" className="block text-sm font-medium text-gray-700 mb-1">
              이름
            </label>
            <input type="text" id="name" name="name" className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" />
          </div>
          <div className="mb-4">
            <label htmlFor="email" className="block text-sm font-medium text-gray-700 mb-1">
              이메일
            </label>
            <input type="email" id="email" name="email" className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" />
          </div>
          <div className="mb-4">
            <label
              htmlFor="password"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              비밀번호
            </label>
            <input type="password" id="password" name="password" className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" />
          </div>
          <div className="mb-6">
            <label
              htmlFor="password-confirm"
              className="block text-sm font-medium text-gray-700 mb-1"
            >
              비밀번호 확인
            </label>
            <input type="password" id="password-confirm" name="password-confirm" className="w-full px-3 py-2 border border-gray-300 rounded-md shadow-sm focus:outline-none focus:ring-blue-500 focus:border-blue-500" />
          </div>
          <div className="mb-6 flex items-center">
            <input type="checkbox" id="terms" name="terms" className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded" />
            <label htmlFor="terms" className="ml-2 block text-sm text-gray-900">
              이용약관에 동의합니다.
            </label>
          </div>
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 px-4 rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            회원가입
          </button>
        </form>
      </div>
    </div>
  );
};

export default SignupPage;
