/**
 * Privacy Policy Page
 * T062 - FR-024: /privacy 페이지에 개인정보처리방침 전문 표시 (PIPA 준수)
 */

import Link from 'next/link';

export const metadata = {
  title: '개인정보처리방침 - Legal Evidence Hub',
  description: 'Legal Evidence Hub 개인정보처리방침 (개인정보보호법 준수)',
};

export default function PrivacyPage() {
  return (
    <div className="min-h-screen bg-neutral-50 dark:bg-gray-900 py-12">
      <div className="container mx-auto px-4 max-w-4xl">
        <div className="bg-white dark:bg-gray-800 rounded-xl shadow-lg p-8">
          <h1 className="text-3xl font-bold text-gray-900 dark:text-white mb-8">
            개인정보처리방침
          </h1>

          <div className="prose dark:prose-invert max-w-none">
            <p className="text-sm text-gray-500 dark:text-gray-400 mb-8">
              최종 수정일: 2025년 1월 1일 | 시행일: 2025년 1월 1일
            </p>

            <p className="text-gray-700 dark:text-gray-300 mb-8">
              Legal Evidence Hub (이하 &quot;회사&quot;)는 개인정보보호법에 따라 이용자의 개인정보 보호 및
              권익을 보호하고 개인정보와 관련한 이용자의 고충을 원활하게 처리할 수 있도록
              다음과 같은 처리방침을 두고 있습니다.
            </p>

            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-4">제1조 (개인정보의 처리 목적)</h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                회사는 다음의 목적을 위하여 개인정보를 처리합니다:
              </p>
              <ol className="list-decimal pl-6 text-gray-700 dark:text-gray-300 space-y-2">
                <li><strong>회원 가입 및 관리</strong>: 회원 가입의사 확인, 본인 식별·인증, 회원자격 유지·관리</li>
                <li><strong>서비스 제공</strong>: AI 기반 증거 분석, 문서 초안 생성, 맞춤 서비스 제공</li>
                <li><strong>민원 처리</strong>: 민원인의 신원 확인, 민원사항 확인, 처리결과 통보</li>
                <li><strong>마케팅 및 광고</strong>: 이벤트 및 광고성 정보 제공 (동의 시에만)</li>
              </ol>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-4">제2조 (처리하는 개인정보의 항목)</h2>
              <div className="overflow-x-auto">
                <table className="min-w-full border border-gray-200 dark:border-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-4 py-2 text-left border-b">구분</th>
                      <th className="px-4 py-2 text-left border-b">수집 항목</th>
                      <th className="px-4 py-2 text-left border-b">수집 방법</th>
                    </tr>
                  </thead>
                  <tbody className="text-gray-700 dark:text-gray-300">
                    <tr>
                      <td className="px-4 py-2 border-b">필수</td>
                      <td className="px-4 py-2 border-b">이름, 이메일, 비밀번호</td>
                      <td className="px-4 py-2 border-b">회원가입</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-2 border-b">선택</td>
                      <td className="px-4 py-2 border-b">소속(법무법인명)</td>
                      <td className="px-4 py-2 border-b">회원가입</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-2 border-b">자동 수집</td>
                      <td className="px-4 py-2 border-b">접속 IP, 접속 로그, 서비스 이용 기록</td>
                      <td className="px-4 py-2 border-b">서비스 이용</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-4">제3조 (개인정보의 처리 및 보유 기간)</h2>
              <ol className="list-decimal pl-6 text-gray-700 dark:text-gray-300 space-y-2">
                <li>회사는 법령에 따른 개인정보 보유·이용기간 또는 정보주체로부터 개인정보를 수집 시에
                동의 받은 개인정보 보유·이용기간 내에서 개인정보를 처리·보유합니다.</li>
                <li>각각의 개인정보 처리 및 보유 기간은 다음과 같습니다:
                  <ul className="list-disc pl-6 mt-2 space-y-1">
                    <li>회원 정보: 회원 탈퇴 시까지</li>
                    <li>증거 자료: 사건 종료 후 3년</li>
                    <li>서비스 이용 기록: 3년</li>
                    <li>결제 기록: 5년 (전자상거래법)</li>
                  </ul>
                </li>
              </ol>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-4">제4조 (개인정보의 제3자 제공)</h2>
              <p className="text-gray-700 dark:text-gray-300">
                회사는 정보주체의 개인정보를 제1조에서 명시한 범위 내에서만 처리하며,
                정보주체의 동의, 법률의 특별한 규정 등 개인정보보호법 제17조 및 제18조에 해당하는
                경우에만 개인정보를 제3자에게 제공합니다.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-4">제5조 (개인정보처리의 위탁)</h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                회사는 원활한 개인정보 업무처리를 위하여 다음과 같이 개인정보 처리업무를 위탁하고 있습니다:
              </p>
              <div className="overflow-x-auto">
                <table className="min-w-full border border-gray-200 dark:border-gray-700">
                  <thead className="bg-gray-50 dark:bg-gray-700">
                    <tr>
                      <th className="px-4 py-2 text-left border-b">수탁업체</th>
                      <th className="px-4 py-2 text-left border-b">위탁 업무</th>
                    </tr>
                  </thead>
                  <tbody className="text-gray-700 dark:text-gray-300">
                    <tr>
                      <td className="px-4 py-2 border-b">Amazon Web Services (AWS)</td>
                      <td className="px-4 py-2 border-b">클라우드 인프라 운영, 데이터 저장</td>
                    </tr>
                    <tr>
                      <td className="px-4 py-2 border-b">OpenAI</td>
                      <td className="px-4 py-2 border-b">AI 분석 처리 (데이터 익명화 후 전송)</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-4">제6조 (정보주체의 권리·의무 및 행사방법)</h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                정보주체는 회사에 대해 언제든지 다음 각 호의 개인정보 보호 관련 권리를 행사할 수 있습니다:
              </p>
              <ol className="list-decimal pl-6 text-gray-700 dark:text-gray-300 space-y-2">
                <li>개인정보 열람 요구</li>
                <li>오류 등이 있을 경우 정정 요구</li>
                <li>삭제 요구</li>
                <li>처리정지 요구</li>
              </ol>
              <p className="text-gray-700 dark:text-gray-300 mt-4">
                권리 행사는 서면, 전자우편 등을 통하여 하실 수 있으며, 회사는 이에 대해 지체 없이 조치하겠습니다.
              </p>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-4">제7조 (개인정보의 파기)</h2>
              <ol className="list-decimal pl-6 text-gray-700 dark:text-gray-300 space-y-2">
                <li>회사는 개인정보 보유기간의 경과, 처리목적 달성 등 개인정보가 불필요하게 되었을 때에는
                지체 없이 해당 개인정보를 파기합니다.</li>
                <li>전자적 파일 형태로 저장된 개인정보는 기록을 재생할 수 없는 기술적 방법을 사용하여 파기합니다.</li>
              </ol>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-4">제8조 (개인정보의 안전성 확보조치)</h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                회사는 개인정보의 안전성 확보를 위해 다음과 같은 조치를 취하고 있습니다:
              </p>
              <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
                <li><strong>관리적 조치</strong>: 내부관리계획 수립·시행, 정기적 직원 교육</li>
                <li><strong>기술적 조치</strong>: 개인정보처리시스템 접근권한 관리, 암호화, 보안프로그램 설치</li>
                <li><strong>물리적 조치</strong>: 전산실, 자료보관실 등의 접근통제</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-4">제9조 (개인정보 보호책임자)</h2>
              <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-4">
                <p className="text-gray-700 dark:text-gray-300">
                  <strong>개인정보 보호책임자</strong><br />
                  성명: 홍길동<br />
                  직책: 개인정보보호담당관<br />
                  연락처: privacy@legalevidence.hub
                </p>
              </div>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-4">제10조 (권익침해 구제방법)</h2>
              <p className="text-gray-700 dark:text-gray-300 mb-4">
                정보주체는 개인정보침해로 인한 구제를 받기 위하여 다음 기관에 분쟁해결이나 상담 등을
                신청할 수 있습니다:
              </p>
              <ul className="list-disc pl-6 text-gray-700 dark:text-gray-300 space-y-2">
                <li>개인정보분쟁조정위원회: (국번없이) 1833-6972</li>
                <li>개인정보침해신고센터: (국번없이) 118</li>
                <li>대검찰청 사이버범죄수사과: (국번없이) 1301</li>
                <li>경찰청 사이버안전국: (국번없이) 182</li>
              </ul>
            </section>

            <section className="mb-8">
              <h2 className="text-xl font-semibold mb-4">부칙</h2>
              <p className="text-gray-700 dark:text-gray-300">
                본 개인정보처리방침은 2025년 1월 1일부터 시행됩니다.
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
