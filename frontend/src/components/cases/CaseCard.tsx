import Link from 'next/link';
import { Case } from '@/types/case';
import { FileText, Clock, AlertCircle, CheckCircle2 } from 'lucide-react';

interface CaseCardProps {
    caseData: Case;
}

export default function CaseCard({ caseData }: CaseCardProps) {
    const getStatusColor = (status: string) => {
        switch (status) {
            case 'ready': return 'text-success-green';
            case 'generating': return 'text-accent';
            default: return 'text-gray-400';
        }
    };

    return (
        <Link href={`/cases/${caseData.id}`}>
            <div className="card p-6 h-full flex flex-col justify-between group cursor-pointer hover:ring-2 hover:ring-accent/50 hover:shadow-md transition-all duration-300 bg-calm-grey">
                <div>
                    <div className="flex justify-between items-start mb-4">
                        <div>
                            <h3 className="text-xl font-bold text-deep-trust-blue group-hover:text-accent transition-colors">
                                {caseData.title}
                            </h3>
                            <p className="text-sm text-gray-500 mt-1">{caseData.clientName}</p>
                        </div>
                        <span className={`px-2 py-1 rounded-full text-xs font-medium ${caseData.status === 'open' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-800'
                            }`}>
                            {caseData.status.toUpperCase()}
                        </span>
                    </div>

                    <div className="space-y-3">
                        <div className="flex items-center text-sm text-gray-600">
                            <FileText className="w-4 h-4 mr-2" />
                            <span>증거 {caseData.evidenceCount}건</span>
                        </div>
                        <div className="flex items-center text-sm text-gray-600">
                            <Clock className="w-4 h-4 mr-2" />
                            <span>최근 업데이트: {new Date(caseData.lastUpdated).toLocaleDateString()}</span>
                        </div>
                    </div>
                </div>

                <div className="mt-6 pt-4 border-t border-gray-100 flex items-center justify-between">
                    <div className="flex items-center space-x-2">
                        <span className="text-sm font-medium text-gray-500">Draft 상태:</span>
                        {caseData.draftStatus === 'ready' ? (
                            <div className="flex items-center text-success-green text-sm font-bold">
                                <CheckCircle2 className="w-4 h-4 mr-1" />
                                <span>준비됨</span>
                            </div>
                        ) : caseData.draftStatus === 'generating' ? (
                            <div className="flex items-center text-accent text-sm font-bold animate-pulse">
                                <Clock className="w-4 h-4 mr-1" />
                                <span>생성 중...</span>
                            </div>
                        ) : (
                            <div className="flex items-center text-gray-400 text-sm">
                                <AlertCircle className="w-4 h-4 mr-1" />
                                <span>미생성</span>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </Link>
    );
}
