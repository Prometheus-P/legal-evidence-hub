/**
 * Terms of Service Page
 * T061 - FR-023: /terms 페이지에 이용약관 전문 표시
 */

import Link from 'next/link';

export const metadata = {
  title: '이용약관 - Legal Evidence Hub',
  description: 'Legal Evidence Hub 서비스 이용약관',
};

export default function TermsPage() {
  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-gray-900 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
            이용약관
          </h1>

          <div className="prose dark:prose-invert max-w-none">
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-8">
              최종 수정일: 2025년 1월 1일 | 시행일: 2025년 1월 1일
            </p>

            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-4">제1조 (목적)</h2>
              <p className="text-gray-700 dark:text-gray-300">
                본 약관은 Legal Evidence Hub (이하 &quot;회사&quot;)가 제공하는 AI 기반 법률 증거 분석 서비스
                (이하 &quot;서비스&quot;)의 이용과 관련하여 회사와 이용자 간의 권리, 의무 및 책임사항을
                규정함을 목적으로 합니다.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-4">제2조 (정의)</h2>
              <ol className="list-decimal pl-6 text-gray-700 dark:text-gray-300 space-y-2">
                <li>&quot;서비스&quot;란 회사가 제공하는 AI 기반 법률 증거 분석, 문서 초안 생성 및 관련 부가 서비스를 말합니다.</li>
                <li>&quot;이용자&quot;란 본 약관에 따라 회사가 제공하는 서비스를 이용하는 자를 말합니다.</li>
                <li>&quot;회원&quot;이란 회사에 개인정보를 제공하여 회원등록을 한 자로서 서비스를 이용하는 자를 말합니다.</li>
              </ol>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-4">제3조 (약관의 효력 및 변경)</h2>
              <ol className="list-decimal pl-6 text-gray-700 dark:text-gray-300 space-y-2">
                <li>본 약관은 서비스 화면에 게시하거나 기타의 방법으로 이용자에게 공지함으로써 효력이 발생합니다.</li>
                <li>회사는 필요한 경우 관련 법령을 위배하지 않는 범위에서 본 약관을 변경할 수 있습니다.</li>
                <li>약관이 변경되는 경우 회사는 변경 약관의 시행일로부터 최소 7일 전에 공지합니다.</li>
              </ol>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-4">제4조 (서비스의 제공)</h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">회사는 다음과 같은 서비스를 제공합니다:</p>
              <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
                <li>AI 기반 법률 증거 자동 분석</li>
                <li>증거 타임라인 및 관계도 시각화</li>
                <li>법률 문서 초안 자동 생성 (미리보기 전용)</li>
                <li>증거 검색 및 관리 기능</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-4">제5조 (AI 생성 콘텐츠의 성격)</h2>
              <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4">
                <p className="text-gray-700 dark:text-gray-300 font-medium">
                  ⚠️ 중요 고지사항
                </p>
                <ol className="list-decimal pl-6 text-gray-700 dark:text-gray-300 space-y-2 mt-2">
                  <li>본 서비스에서 생성되는 모든 AI 분석 결과 및 문서 초안은 <strong>&quot;미리보기(Preview)&quot;</strong>
                  용도로만 제공됩니다.</li>
                  <li>AI가 생성한 콘텐츠는 법률 자문을 대체하지 않으며, 변호사의 검토 및 승인 없이
                  법적 문서로 사용해서는 안 됩니다.</li>
                  <li>최종 법률 판단 및 문서 제출의 책임은 전적으로 이용자에게 있습니다.</li>
                </ol>
              </div>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-4">제6조 (이용자의 의무)</h2>
              <ol className="list-decimal pl-6 text-gray-700 dark:text-gray-300 space-y-2">
                <li>이용자는 서비스 이용 시 관계 법령, 본 약관의 규정, 이용안내 등을 준수하여야 합니다.</li>
                <li>이용자는 타인의 개인정보를 무단으로 수집, 저장, 공개하여서는 안 됩니다.</li>
                <li>이용자는 서비스를 통해 얻은 정보를 회사의 사전 승낙 없이 상업적 목적으로 이용하거나
                제3자에게 제공하여서는 안 됩니다.</li>
              </ol>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-4">제7조 (지적재산권)</h2>
              <ol className="list-decimal pl-6 text-gray-700 dark:text-gray-300 space-y-2">
                <li>서비스에 대한 저작권 및 지적재산권은 회사에 귀속됩니다.</li>
                <li>이용자가 업로드한 증거 자료의 소유권은 이용자에게 있으며, 회사는 서비스 제공 목적으로만
                이를 처리합니다.</li>
              </ol>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-4">제8조 (면책조항)</h2>
              <ol className="list-decimal pl-6 text-gray-700 dark:text-gray-300 space-y-2">
                <li>회사는 천재지변, 전쟁, 기간통신사업자의 서비스 중지 등 불가항력적인 사유로 서비스를
                제공할 수 없는 경우 책임이 면제됩니다.</li>
                <li>회사는 AI가 생성한 분석 결과 및 문서 초안의 정확성, 완전성, 법적 유효성을 보장하지 않습니다.</li>
                <li>이용자가 AI 생성 콘텐츠를 법적 절차에 사용함으로써 발생하는 모든 결과에 대해
                회사는 책임을 지지 않습니다.</li>
              </ol>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-4">제9조 (분쟁해결)</h2>
              <ol className="list-decimal pl-6 text-gray-700 dark:text-gray-300 space-y-2">
                <li>본 약관에 명시되지 않은 사항은 관계 법령 및 상관례에 따릅니다.</li>
                <li>서비스 이용으로 발생한 분쟁에 대해 소송이 제기될 경우, 회사 소재지 관할 법원을
                합의 관할법원으로 합니다.</li>
              </ol>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-4">부칙</h2>
              <p className="text-gray-700 dark:text-gray-300">
                본 약관은 2025년 1월 1일부터 시행됩니다.
              </p>
            </section>
          </div>

          <div className="mt-8 pt-8 border-t border-gray-200 dark:border-gray-700">
            <Link
              href="/signup"
              className="text-accent hover:underline"
            >
              ← 회원가입으로 돌아가기
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}
