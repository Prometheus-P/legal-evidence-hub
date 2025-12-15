/**
 * Summary API Client
 * US8 - 진행 상태 요약 카드 (Progress Summary Cards)
 */

import { apiRequest, ApiResponse } from './client';
import type { CaseSummaryResponse } from '@/types/summary';

/**
 * Get case summary card data
 */
export async function getCaseSummary(
  caseId: string
): Promise<ApiResponse<CaseSummaryResponse>> {
  return apiRequest<CaseSummaryResponse>(`/cases/${caseId}/summary`, {
    method: 'GET',
  });
}

/**
 * Download case summary as PDF (HTML)
 * Opens in new window for printing/saving
 *
 * Security: Uses HTTP-only cookies for authentication (credentials: 'include')
 */
export async function downloadCaseSummaryPdf(caseId: string): Promise<void> {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  const url = `${baseUrl}/api/cases/${caseId}/summary/pdf`;

  // Fetch with HTTP-only cookie authentication
  const response = await fetch(url, {
    credentials: 'include',
  });

  if (!response.ok) {
    throw new Error('PDF 다운로드에 실패했습니다.');
  }

  // Get HTML content
  const htmlContent = await response.text();

  // Open in new window for printing
  const printWindow = window.open('', '_blank');
  if (printWindow) {
    printWindow.document.write(htmlContent);
    printWindow.document.close();

    // Trigger print dialog after content loads
    printWindow.onload = () => {
      printWindow.print();
    };
  }
}

/**
 * Download case summary as file (triggers download)
 *
 * Security: Uses HTTP-only cookies for authentication (credentials: 'include')
 */
export async function downloadCaseSummaryFile(caseId: string): Promise<void> {
  const baseUrl = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000';

  const url = `${baseUrl}/api/cases/${caseId}/summary/pdf`;

  const response = await fetch(url, {
    credentials: 'include',
  });

  if (!response.ok) {
    throw new Error('파일 다운로드에 실패했습니다.');
  }

  // Create blob and download
  const blob = await response.blob();
  const downloadUrl = window.URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = downloadUrl;
  link.download = `case_summary_${caseId}.html`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  window.URL.revokeObjectURL(downloadUrl);
}
