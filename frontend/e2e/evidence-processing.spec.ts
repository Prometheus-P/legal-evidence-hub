import { test, expect } from '@playwright/test';
import { loginAsLawyer, navigateToCaseDetail } from './helpers/auth';
import { TEST_CASE_ID } from './fixtures/test-data';

/**
 * E2E Tests for Evidence Processing Status
 * AI 분석 상태 진단 테스트
 *
 * 문제: 증거물 업로드 후 "처리중" 상태에서 영구 대기
 * 원인 조사: Lambda 호출 실패 시 상태 처리 확인
 */

const CASE_URL = `/lawyer/cases/${TEST_CASE_ID}`;

test.describe('증거물 AI 분석 상태 테스트', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsLawyer(page);
  });

  test('케이스 상세 페이지에서 증거물 목록 확인', async ({ page }) => {
    await page.goto(CASE_URL);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // 페이지 로드 확인
    const caseTitle = page.locator('h1');
    await expect(caseTitle).toBeVisible({ timeout: 10000 });

    // 증거물 탭 찾기
    const evidenceTab = page.getByRole('tab', { name: /Evidence|증거물|증거/i });
    if (await evidenceTab.isVisible()) {
      await evidenceTab.click();
      await page.waitForTimeout(1000);
    }

    await page.screenshot({ path: 'test-results/evidence-list.png' });

    // 증거물 목록이 있는지 확인
    const evidenceItems = page.locator('[data-testid="evidence-card"]')
      .or(page.locator('.evidence-card'))
      .or(page.locator('[class*="evidence"]').filter({ hasText: /파일|분석|처리/ }));

    const itemCount = await evidenceItems.count();
    console.log(`Found ${itemCount} evidence items`);
  });

  test('처리중 상태인 증거물 확인', async ({ page }) => {
    await page.goto(CASE_URL);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // 증거물 탭으로 이동
    const evidenceTab = page.getByRole('tab', { name: /Evidence|증거물|증거/i });
    if (await evidenceTab.isVisible()) {
      await evidenceTab.click();
      await page.waitForTimeout(1000);
    }

    // "처리중" 또는 "분석 중" 상태 찾기
    const processingItems = page.locator('text=/처리중|분석 중|processing|queued/i')
      .or(page.locator('[class*="animate-spin"]'));

    const processingCount = await processingItems.count();
    console.log(`Found ${processingCount} items in processing state`);

    if (processingCount > 0) {
      console.log('WARNING: Found evidence stuck in processing state!');
      await page.screenshot({ path: 'test-results/evidence-processing-stuck.png' });
    }
  });

  test('API를 통해 증거물 상태 직접 확인', async ({ page, request }) => {
    // 먼저 로그인하여 쿠키 획득
    await loginAsLawyer(page);

    // 케이스의 증거물 목록 API 호출
    const response = await page.evaluate(async (caseId) => {
      const res = await fetch(`http://localhost:8000/api/v1/cases/${caseId}/evidence`, {
        credentials: 'include',
      });
      if (!res.ok) {
        return { error: res.status, statusText: res.statusText };
      }
      return await res.json();
    }, TEST_CASE_ID);

    console.log('Evidence API Response:', JSON.stringify(response, null, 2));

    if (response.evidence && Array.isArray(response.evidence)) {
      const processingItems = response.evidence.filter(
        (e: { status: string }) => e.status === 'processing' || e.status === 'pending' || e.status === 'queued'
      );

      if (processingItems.length > 0) {
        console.log('\n=== STUCK EVIDENCE ITEMS ===');
        processingItems.forEach((item: { id: string; status: string; filename: string; created_at: string }) => {
          console.log(`- ID: ${item.id}`);
          console.log(`  Status: ${item.status}`);
          console.log(`  Filename: ${item.filename}`);
          console.log(`  Created: ${item.created_at}`);
        });
        console.log('===========================\n');
      }

      // 완료된 항목 vs 미완료 항목 통계
      const stats = {
        total: response.evidence.length,
        completed: response.evidence.filter((e: { status: string }) => e.status === 'completed' || e.status === 'processed').length,
        processing: response.evidence.filter((e: { status: string }) => e.status === 'processing').length,
        pending: response.evidence.filter((e: { status: string }) => e.status === 'pending').length,
        failed: response.evidence.filter((e: { status: string }) => e.status === 'failed').length,
      };

      console.log('\n=== EVIDENCE STATUS STATS ===');
      console.log(`Total: ${stats.total}`);
      console.log(`Completed: ${stats.completed}`);
      console.log(`Processing: ${stats.processing}`);
      console.log(`Pending: ${stats.pending}`);
      console.log(`Failed: ${stats.failed}`);
      console.log('============================\n');
    }
  });

  test('특정 증거물 상태 API 호출 테스트', async ({ page }) => {
    await loginAsLawyer(page);

    // 먼저 증거물 목록 가져오기
    const listResponse = await page.evaluate(async (caseId) => {
      const res = await fetch(`http://localhost:8000/api/v1/cases/${caseId}/evidence`, {
        credentials: 'include',
      });
      if (!res.ok) return null;
      return await res.json();
    }, TEST_CASE_ID);

    if (!listResponse?.evidence?.length) {
      console.log('No evidence found in this case');
      return;
    }

    // 첫 번째 증거물의 상태 API 호출
    const firstEvidence = listResponse.evidence[0];
    console.log(`Testing status API for evidence: ${firstEvidence.id}`);

    const statusResponse = await page.evaluate(async (evidenceId) => {
      const res = await fetch(`http://localhost:8000/api/v1/evidence/${evidenceId}/status`, {
        credentials: 'include',
      });
      if (!res.ok) {
        return { error: res.status, statusText: res.statusText };
      }
      return await res.json();
    }, firstEvidence.id);

    console.log('Evidence Status API Response:', JSON.stringify(statusResponse, null, 2));
  });

  test('UI에서 "AI 분석 진행 중" 표시 확인', async ({ page }) => {
    await page.goto(CASE_URL);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // "AI 분석 진행 중" 텍스트 찾기
    const aiProcessingText = page.getByText(/AI 분석 진행 중|분석 중|Processing/i);
    const spinners = page.locator('.animate-spin');

    const processingTextCount = await aiProcessingText.count();
    const spinnerCount = await spinners.count();

    console.log(`Found ${processingTextCount} "AI Processing" text elements`);
    console.log(`Found ${spinnerCount} spinning indicators`);

    if (processingTextCount > 0 || spinnerCount > 0) {
      console.log('UI is showing processing state - this may indicate stuck evidence');
      await page.screenshot({ path: 'test-results/evidence-ai-processing-ui.png' });
    }
  });
});

test.describe('증거물 재처리 테스트', () => {
  test.beforeEach(async ({ page }) => {
    await loginAsLawyer(page);
  });

  test('실패한 증거물 재처리 버튼 확인', async ({ page }) => {
    await page.goto(CASE_URL);
    await page.waitForLoadState('domcontentloaded');
    await page.waitForTimeout(2000);

    // 증거물 탭으로 이동
    const evidenceTab = page.getByRole('tab', { name: /Evidence|증거물|증거/i });
    if (await evidenceTab.isVisible()) {
      await evidenceTab.click();
      await page.waitForTimeout(1000);
    }

    // 재시도 버튼 찾기
    const retryButton = page.getByRole('button', { name: /다시 시도|재시도|Retry/i })
      .or(page.locator('button').filter({ hasText: /retry|다시/i }));

    const retryButtonCount = await retryButton.count();
    console.log(`Found ${retryButtonCount} retry buttons`);

    if (retryButtonCount > 0) {
      console.log('Retry buttons are available for failed evidence');
    }

    await page.screenshot({ path: 'test-results/evidence-retry-buttons.png' });
  });

  test('재처리 API 직접 테스트 (dry run)', async ({ page }) => {
    await loginAsLawyer(page);

    // 실패한 증거물 찾기
    const listResponse = await page.evaluate(async (caseId) => {
      const res = await fetch(`http://localhost:8000/api/v1/cases/${caseId}/evidence`, {
        credentials: 'include',
      });
      if (!res.ok) return null;
      return await res.json();
    }, TEST_CASE_ID);

    if (!listResponse?.evidence?.length) {
      console.log('No evidence found');
      return;
    }

    const failedEvidence = listResponse.evidence.filter(
      (e: { status: string }) => e.status === 'failed' || e.status === 'pending'
    );

    if (failedEvidence.length === 0) {
      console.log('No failed or pending evidence to retry');
      return;
    }

    console.log(`Found ${failedEvidence.length} evidence items that can be retried`);
    console.log('Evidence IDs:', failedEvidence.map((e: { id: string }) => e.id).join(', '));

    // NOTE: 실제 재처리는 하지 않음 (dry run)
    // 재처리하려면 아래 코드를 주석 해제
    /*
    const evidenceId = failedEvidence[0].id;
    const retryResponse = await page.evaluate(async (id) => {
      const res = await fetch(`http://localhost:8000/api/v1/evidence/${id}/retry`, {
        method: 'POST',
        credentials: 'include',
      });
      return await res.json();
    }, evidenceId);
    console.log('Retry Response:', retryResponse);
    */
  });
});
