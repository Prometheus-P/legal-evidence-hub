// src/components/common/Footer.tsx
// T060 - FR-020: Copyright footer with legal links
import React from 'react';
import Link from 'next/link';

const Footer = () => {
  const currentYear = new Date().getFullYear();

  return (
    <footer className="bg-gray-100 dark:bg-gray-800 text-neutral-600 dark:text-neutral-300 text-sm mt-12 py-8">
      <div className="container mx-auto px-4 text-center">
        <div className="flex flex-wrap justify-center gap-x-4 gap-y-2 mb-4">
          <Link href="/terms" className="hover:text-gray-900 dark:hover:text-white">
            이용약관
          </Link>
          <span className="hidden sm:inline">|</span>
          <Link href="/privacy" className="hover:text-gray-900 dark:hover:text-white">
            개인정보처리방침
          </Link>
          <span className="hidden sm:inline">|</span>
          <a href="mailto:contact@legalevidence.hub" className="hover:text-gray-900 dark:hover:text-white">
            문의하기
          </a>
        </div>
        <p className="text-xs text-neutral-500 dark:text-neutral-400">
          © {currentYear} Legal Evidence Hub. All Rights Reserved. 무단 활용 금지.
        </p>
      </div>
    </footer>
  );
};

export default Footer;
