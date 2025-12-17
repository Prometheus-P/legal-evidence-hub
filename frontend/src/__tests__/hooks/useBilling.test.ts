/**
 * useBilling Hook Tests
 * 003-role-based-ui Feature - US8
 *
 * Tests for billing and invoice management hook.
 */

import { renderHook, waitFor, act } from '@testing-library/react';
import { useBilling, formatCurrency, getStatusBadgeStyle, getStatusLabel } from '@/hooks/useBilling';
import * as billingApi from '@/lib/api/billing';

// Mock the billing API
jest.mock('@/lib/api/billing', () => ({
  getInvoices: jest.fn(),
  createInvoice: jest.fn(),
  updateInvoice: jest.fn(),
  deleteInvoice: jest.fn(),
  getClientInvoices: jest.fn(),
  payInvoice: jest.fn(),
}));

const mockInvoice = {
  id: 'inv-1',
  case_id: 'case-1',
  case_title: '이혼 소송',
  client_id: 'client-1',
  client_name: '홍길동',
  lawyer_id: 'lawyer-1',
  lawyer_name: '김변호사',
  amount: '1000000',
  description: '착수금',
  status: 'pending' as const,
  due_date: '2024-02-01',
  paid_at: null,
  created_at: '2024-01-01T00:00:00Z',
};

const mockInvoiceList = {
  invoices: [mockInvoice],
  total: 1,
  total_pending: '1000000',
  total_paid: '0',
};

describe('useBilling', () => {
  beforeEach(() => {
    jest.clearAllMocks();
  });

  describe('Initial Loading', () => {
    it('should start in loading state', () => {
      (billingApi.getInvoices as jest.Mock).mockReturnValue(new Promise(() => {}));

      const { result } = renderHook(() => useBilling());

      expect(result.current.isLoading).toBe(true);
      expect(result.current.invoices).toEqual([]);
    });

    it('should load invoices successfully', async () => {
      (billingApi.getInvoices as jest.Mock).mockResolvedValue({
        data: mockInvoiceList,
        error: null,
      });

      const { result } = renderHook(() => useBilling());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.invoices).toEqual([mockInvoice]);
      expect(result.current.total).toBe(1);
      expect(result.current.totalPending).toBe('1000000');
      expect(result.current.totalPaid).toBe('0');
      expect(result.current.error).toBeNull();
    });

    it('should handle load error', async () => {
      (billingApi.getInvoices as jest.Mock).mockResolvedValue({
        data: null,
        error: '청구서를 불러올 수 없습니다.',
      });

      const { result } = renderHook(() => useBilling());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.invoices).toEqual([]);
      expect(result.current.error).toBe('청구서를 불러올 수 없습니다.');
    });

    it('should not auto-fetch when autoFetch is false', () => {
      const { result } = renderHook(() => useBilling({ autoFetch: false }));

      expect(billingApi.getInvoices).not.toHaveBeenCalled();
      expect(result.current.isLoading).toBe(true);
    });
  });

  describe('Client Mode', () => {
    it('should use client API when isClient is true', async () => {
      (billingApi.getClientInvoices as jest.Mock).mockResolvedValue({
        data: mockInvoiceList,
        error: null,
      });

      renderHook(() => useBilling({ isClient: true }));

      await waitFor(() => {
        expect(billingApi.getClientInvoices).toHaveBeenCalled();
      });

      expect(billingApi.getInvoices).not.toHaveBeenCalled();
    });
  });

  describe('Create Invoice', () => {
    it('should create invoice successfully', async () => {
      (billingApi.getInvoices as jest.Mock).mockResolvedValue({
        data: mockInvoiceList,
        error: null,
      });
      (billingApi.createInvoice as jest.Mock).mockResolvedValue({
        data: mockInvoice,
        error: null,
      });

      const { result } = renderHook(() => useBilling());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      let createdInvoice;
      await act(async () => {
        createdInvoice = await result.current.create({
          case_id: 'case-1',
          client_id: 'client-1',
          amount: '1000000',
        });
      });

      expect(createdInvoice).toEqual(mockInvoice);
      expect(billingApi.createInvoice).toHaveBeenCalled();
    });

    it('should handle create error', async () => {
      (billingApi.getInvoices as jest.Mock).mockResolvedValue({
        data: mockInvoiceList,
        error: null,
      });
      (billingApi.createInvoice as jest.Mock).mockResolvedValue({
        data: null,
        error: '청구서 생성 실패',
      });

      const { result } = renderHook(() => useBilling());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      let createdInvoice;
      await act(async () => {
        createdInvoice = await result.current.create({
          case_id: 'case-1',
          client_id: 'client-1',
          amount: '1000000',
        });
      });

      expect(createdInvoice).toBeNull();
      expect(result.current.error).toBe('청구서 생성 실패');
    });
  });

  describe('Update Invoice', () => {
    it('should update invoice successfully', async () => {
      const updatedInvoice = { ...mockInvoice, amount: '2000000' };
      (billingApi.getInvoices as jest.Mock).mockResolvedValue({
        data: mockInvoiceList,
        error: null,
      });
      (billingApi.updateInvoice as jest.Mock).mockResolvedValue({
        data: updatedInvoice,
        error: null,
      });

      const { result } = renderHook(() => useBilling());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      let updated;
      await act(async () => {
        updated = await result.current.update('inv-1', { amount: '2000000' });
      });

      expect(updated).toEqual(updatedInvoice);
      expect(result.current.invoices[0].amount).toBe('2000000');
    });
  });

  describe('Delete Invoice', () => {
    it('should delete invoice successfully', async () => {
      (billingApi.getInvoices as jest.Mock).mockResolvedValue({
        data: mockInvoiceList,
        error: null,
      });
      (billingApi.deleteInvoice as jest.Mock).mockResolvedValue({
        data: { message: 'deleted' },
        error: null,
      });

      const { result } = renderHook(() => useBilling());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      expect(result.current.invoices).toHaveLength(1);

      let success;
      await act(async () => {
        success = await result.current.remove('inv-1');
      });

      expect(success).toBe(true);
      expect(result.current.invoices).toHaveLength(0);
      expect(result.current.total).toBe(0);
    });
  });

  describe('Pay Invoice', () => {
    it('should pay invoice successfully', async () => {
      const paidInvoice = { ...mockInvoice, status: 'paid' as const, paid_at: '2024-01-15T00:00:00Z' };
      (billingApi.getInvoices as jest.Mock).mockResolvedValue({
        data: mockInvoiceList,
        error: null,
      });
      (billingApi.payInvoice as jest.Mock).mockResolvedValue({
        data: paidInvoice,
        error: null,
      });

      const { result } = renderHook(() => useBilling());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      let paid;
      await act(async () => {
        paid = await result.current.pay('inv-1', { payment_method: 'card' });
      });

      expect(paid).toEqual(paidInvoice);
      expect(result.current.invoices[0].status).toBe('paid');
    });
  });

  describe('Filters', () => {
    it('should update filters and refetch', async () => {
      (billingApi.getInvoices as jest.Mock).mockResolvedValue({
        data: mockInvoiceList,
        error: null,
      });

      const { result } = renderHook(() => useBilling());

      await waitFor(() => {
        expect(result.current.isLoading).toBe(false);
      });

      act(() => {
        result.current.setFilters({ status: 'paid' });
      });

      await waitFor(() => {
        expect(billingApi.getInvoices).toHaveBeenCalledTimes(2);
      });

      expect(result.current.filters.status).toBe('paid');
    });
  });
});

describe('Helper Functions', () => {
  describe('formatCurrency', () => {
    it('should format number as Korean Won', () => {
      expect(formatCurrency(1000000)).toBe('₩1,000,000');
      expect(formatCurrency('500000')).toBe('₩500,000');
    });
  });

  describe('getStatusBadgeStyle', () => {
    it('should return correct styles for each status', () => {
      expect(getStatusBadgeStyle('pending')).toContain('yellow');
      expect(getStatusBadgeStyle('paid')).toContain('green');
      expect(getStatusBadgeStyle('overdue')).toContain('red');
      expect(getStatusBadgeStyle('cancelled')).toContain('gray');
    });
  });

  describe('getStatusLabel', () => {
    it('should return Korean labels for each status', () => {
      expect(getStatusLabel('pending')).toBe('대기중');
      expect(getStatusLabel('paid')).toBe('결제완료');
      expect(getStatusLabel('overdue')).toBe('연체');
      expect(getStatusLabel('cancelled')).toBe('취소');
    });
  });
});
