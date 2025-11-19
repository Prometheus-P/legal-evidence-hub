import { useState } from 'react';
import Head from 'next/head';
import { useRouter } from 'next/router';
import { ArrowLeft, Filter } from 'lucide-react';
import Link from 'next/link';
import EvidenceUpload from '@/components/evidence/EvidenceUpload';
import EvidenceTable from '@/components/evidence/EvidenceTable';
import { Evidence } from '@/types/evidence';

// Mock Data
const MOCK_EVIDENCE: Evidence[] = [
    {
        id: '1',
        caseId: '1',
        filename: '녹취록_20240501.mp3',
        type: 'audio',
        status: 'completed',
        uploadDate: '2024-05-01T10:00:00Z',
        summary: '피고의 폭언이 담긴 통화 녹음',
        size: 15 * 1024 * 1024,
    },
    {
        id: '2',
        caseId: '1',
        filename: '카카오톡_대화내역.txt',
        type: 'text',
        status: 'processing',
        uploadDate: '2024-05-02T09:30:00Z',
        size: 50 * 1024,
    },
    {
        id: '3',
        caseId: '1',
        filename: '폭행_상해_진단서.pdf',
        type: 'pdf',
        status: 'queued',
        uploadDate: '2024-05-03T14:20:00Z',
        size: 2 * 1024 * 1024,
    },
];

export default function CaseDetailPage() {
    const router = useRouter();
    const { id } = router.query;
    const [evidenceList, setEvidenceList] = useState<Evidence[]>(MOCK_EVIDENCE);

    const handleUpload = (files: File[]) => {
        console.log('Uploading files:', files);
        // TODO: Implement actual upload logic
        alert(`${files.length}개의 파일이 업로드 대기열에 추가되었습니다.`);
    };

    return (
        <div className="min-h-screen bg-calm-grey">
            <Head>
                <title>사건 상세 | Legal Evidence Hub</title>
            </Head>

            {/* Header */}
            <header className="bg-white border-b border-gray-200 px-6 py-4 sticky top-0 z-10">
                <div className="max-w-7xl mx-auto flex items-center justify-between">
                    <div className="flex items-center">
                        <Link href="/cases" className="mr-4 text-gray-500 hover:text-gray-800 transition-colors">
                            <ArrowLeft className="w-6 h-6" />
                        </Link>
                        <div>
                            <h1 className="text-xl font-bold text-deep-trust-blue">김철수 이혼 소송</h1>
                            <p className="text-xs text-gray-500">Case ID: {id}</p>
                        </div>
                    </div>
                    <div className="flex space-x-3">
                        <button className="btn-primary bg-deep-trust-blue hover:bg-slate-700">
                            Draft 작성
                        </button>
                    </div>
                </div>
            </header>

            <main className="max-w-7xl mx-auto px-6 py-8 space-y-8">
                {/* Upload Section */}
                <section className="bg-white rounded-lg shadow-sm p-6">
                    <h2 className="text-lg font-bold text-gray-900 mb-4">증거 업로드</h2>
                    <EvidenceUpload onUpload={handleUpload} />
                </section>

                {/* Evidence List Section */}
                <section>
                    <div className="flex justify-between items-center mb-4">
                        <h2 className="text-lg font-bold text-gray-900">
                            증거 목록 <span className="text-gray-500 text-sm font-normal">({evidenceList.length})</span>
                        </h2>
                        <button className="flex items-center text-sm text-gray-600 hover:text-gray-900 bg-white border border-gray-300 px-3 py-1.5 rounded-md shadow-sm">
                            <Filter className="w-4 h-4 mr-2" />
                            필터
                        </button>
                    </div>

                    <EvidenceTable items={evidenceList} />
                </section>
            </main>
        </div>
    );
}
