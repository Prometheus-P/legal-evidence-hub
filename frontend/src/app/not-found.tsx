/**
 * Custom 404 Page for App Router
 *
 * When a route is not found, Next.js App Router serves this page.
 * For S3/CloudFront deployment, this handles SPA-style 404 fallback.
 */

import Link from 'next/link';

export default function NotFound() {
  return (
    <div className="min-h-screen flex items-center justify-center bg-neutral-50">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-300 mb-4">404</h1>
        <p className="text-xl text-gray-600 mb-8">페이지를 찾을 수 없습니다</p>
        <Link
          href="/login"
          className="px-6 py-3 bg-blue-500 text-white rounded-lg hover:bg-blue-600 transition-colors inline-block"
        >
          로그인 화면으로 이동
        </Link>
      </div>
    </div>
  );
}
