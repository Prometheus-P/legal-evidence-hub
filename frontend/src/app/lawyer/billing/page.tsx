/**
 * Lawyer Billing Page
 * 003-role-based-ui Feature - US8 (T151)
 *
 * Page for managing invoices and billing.
 */

'use client';

import { useMemo, useState, useCallback, useEffect } from 'react';
import { useBilling } from '@/hooks/useBilling';
import { getLawyerCases, type CaseListItem } from '@/lib/api/lawyer';
import { getClients } from '@/lib/api/clients';
import { getCaseMembers } from '@/lib/api/cases';
import InvoiceList from '@/components/lawyer/InvoiceList';
import InvoiceForm from '@/components/lawyer/InvoiceForm';
import type { Invoice, InvoiceStatus, InvoiceCreateRequest, InvoiceUpdateRequest } from '@/types/billing';
import type { ClientItem } from '@/types/client';

type ViewMode = 'list' | 'create' | 'edit';

interface CaseOption {
  id: string;
  title: string;
  client_name?: string;
  client_id?: string;
}

interface ClientOption {
  id: string;
  name: string;
  email?: string;
}

const CASES_PAGE_SIZE = 100;
const CLIENTS_PAGE_SIZE = 100;

export default function LawyerBillingPage() {
  const [viewMode, setViewMode] = useState<ViewMode>('list');
  const [editingInvoice, setEditingInvoice] = useState<Invoice | null>(null);
  const [formLoading, setFormLoading] = useState(false);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);
  const [caseOptions, setCaseOptions] = useState<CaseOption[]>([]);
  const [clientOptions, setClientOptions] = useState<ClientOption[]>([]);
  const [optionsLoading, setOptionsLoading] = useState(true);
  const [optionError, setOptionError] = useState<string | null>(null);

  const {
    invoices,
    total,
    totalPending,
    totalPaid,
    isLoading,
    error,
    filters,
    setFilters,
    create,
    update,
    remove,
  } = useBilling();

  useEffect(() => {
    let isMounted = true;

    const fetchAllCases = async (): Promise<CaseOption[]> => {
      const collected: CaseListItem[] = [];
      let page = 1;
      let total = Infinity;

      while (collected.length < total) {
        const response = await getLawyerCases({
          page,
          limit: CASES_PAGE_SIZE,
          sort_by: 'updated_at',
        });

        if (response.error || !response.data) {
          throw new Error(response.error || '사건 목록을 불러오지 못했습니다.');
        }

        collected.push(...response.data.cases);
        total = response.data.total;

        if (response.data.cases.length < CASES_PAGE_SIZE) {
          break;
        }

        page += 1;
      }

      return collected.map((caseItem) => ({
        id: caseItem.id,
        title: caseItem.title,
        client_name: caseItem.client_name,
      }));
    };

    const fetchAllClients = async (): Promise<ClientOption[]> => {
      const clients: ClientOption[] = [];
      let page = 1;
      let totalPages = 1;

      do {
        const response = await getClients({
          page,
          page_size: CLIENTS_PAGE_SIZE,
          status: 'active',
        });

        if (response.error || !response.data) {
          throw new Error(response.error || '의뢰인 목록을 불러오지 못했습니다.');
        }

        clients.push(
          ...response.data.items.map((client: ClientItem) => ({
            id: client.id,
            name: client.name,
            email: client.email,
          }))
        );

        totalPages = response.data.total_pages;
        page += 1;
      } while (page <= totalPages);

      return clients;
    };

    async function loadOptions() {
      setOptionsLoading(true);
      setOptionError(null);

      try {
        const [caseList, clientList] = await Promise.all([
          fetchAllCases(),
          fetchAllClients(),
        ]);

        if (!isMounted) return;

        setCaseOptions(caseList);
        setClientOptions(clientList);

        if (caseList.length === 0) {
          setOptionError('등록된 사건이 없습니다. 먼저 사건을 생성해 주세요.');
        }
      } catch (error) {
        if (!isMounted) return;
        setCaseOptions([]);
        setClientOptions([]);
        setOptionError('청구서 발행에 필요한 데이터를 불러오는 중 오류가 발생했습니다.');
      } finally {
        if (isMounted) {
          setOptionsLoading(false);
        }
      }
    }

    loadOptions();

    return () => {
      isMounted = false;
    };
  }, []);

  const handleFilterChange = useCallback(
    (status: InvoiceStatus | null) => {
      setFilters({ ...filters, status: status || undefined, page: 1 });
    },
    [filters, setFilters]
  );

  const handlePageChange = useCallback(
    (page: number) => {
      setFilters({ ...filters, page });
    },
    [filters, setFilters]
  );

  const handleCreate = useCallback(async (data: InvoiceCreateRequest) => {
    setFormLoading(true);
    try {
      const invoice = await create(data);
      if (invoice) {
        setSuccessMessage('청구서가 성공적으로 발행되었습니다.');
        setViewMode('list');
        setTimeout(() => setSuccessMessage(null), 3000);
      }
    } finally {
      setFormLoading(false);
    }
  }, [create]);

  const handleEdit = useCallback((invoice: Invoice) => {
    setEditingInvoice(invoice);
    setViewMode('edit');
  }, []);

  const handleUpdate = useCallback(
    async (data: InvoiceUpdateRequest) => {
      if (!editingInvoice) return;

      setFormLoading(true);
      try {
        const invoice = await update(editingInvoice.id, data);
        if (invoice) {
          setSuccessMessage('청구서가 성공적으로 수정되었습니다.');
          setViewMode('list');
          setEditingInvoice(null);
          setTimeout(() => setSuccessMessage(null), 3000);
        }
      } finally {
        setFormLoading(false);
      }
    },
    [editingInvoice, update]
  );

  const handleDelete = useCallback(
    async (invoice: Invoice) => {
      if (!confirm('이 청구서를 삭제하시겠습니까?')) return;

      const success = await remove(invoice.id);
      if (success) {
        setSuccessMessage('청구서가 삭제되었습니다.');
        setTimeout(() => setSuccessMessage(null), 3000);
      }
    },
    [remove]
  );

  const handleCancel = useCallback(() => {
    setViewMode('list');
    setEditingInvoice(null);
  }, []);

  const clientMap = useMemo(() => {
    const map = new Map<string, ClientOption>();
    clientOptions.forEach((client) => {
      map.set(client.id, client);
    });
    return map;
  }, [clientOptions]);

  const loadCaseClients = useCallback(
    async (caseId: string) => {
      const response = await getCaseMembers(caseId);

      if (response.error || !response.data) {
        throw new Error(response.error || '사건 구성원을 불러오지 못했습니다.');
      }

      const deduped = new Map<string, ClientOption>();

      response.data.members.forEach((member) => {
        if (member.role === 'owner') return;
        const client = clientMap.get(member.user_id);
        if (client) {
          deduped.set(client.id, client);
        }
      });

      return Array.from(deduped.values());
    },
    [clientMap]
  );

  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text-primary)]">청구/결제 관리</h1>
          <p className="text-[var(--color-text-secondary)] mt-1">
            청구서를 발행하고 결제 상태를 관리하세요.
          </p>
        </div>
        {viewMode === 'list' && (
          <button
            type="button"
            onClick={() => setViewMode('create')}
            className="px-4 py-2 bg-[var(--color-primary)] text-white rounded-lg
              font-medium hover:bg-[var(--color-primary-hover)]
              min-h-[44px] flex items-center gap-2"
          >
            <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M12 6v6m0 0v6m0-6h6m-6 0H6"
              />
            </svg>
            청구서 발행
          </button>
        )}
      </div>

      {/* Success Message */}
      {successMessage && (
        <div className="p-4 bg-green-50 text-green-700 rounded-lg flex items-center justify-between">
          <span>{successMessage}</span>
          <button
            type="button"
            onClick={() => setSuccessMessage(null)}
            className="p-1 hover:bg-green-100 rounded"
          >
            <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          </button>
        </div>
      )}

      {/* Error Message */}
      {error && (
        <div className="p-4 bg-red-50 text-[var(--color-error)] rounded-lg">
          {error}
        </div>
      )}

      {/* Content */}
      {viewMode === 'list' && (
        <InvoiceList
          invoices={invoices}
          total={total}
          totalPending={totalPending}
          totalPaid={totalPaid}
          loading={isLoading}
          onFilterChange={handleFilterChange}
          onEdit={handleEdit}
          onDelete={handleDelete}
          onPageChange={handlePageChange}
          currentPage={filters.page || 1}
          pageSize={filters.limit || 20}
        />
      )}

      {viewMode === 'create' && (
        <div className="bg-white rounded-lg border border-[var(--color-border)]">
          <div className="p-6 border-b border-[var(--color-border)]">
            <h2 className="text-xl font-semibold">새 청구서 발행</h2>
          </div>
          {optionError && (
            <div className="mx-6 mt-4 mb-2 rounded-lg bg-red-50 px-4 py-3 text-sm text-[var(--color-error)]">
              {optionError}
            </div>
          )}
          <InvoiceForm
            cases={caseOptions}
            clients={clientOptions}
            loadCaseClients={loadCaseClients}
            onSubmit={handleCreate as (data: InvoiceCreateRequest | InvoiceUpdateRequest) => Promise<void>}
            onCancel={handleCancel}
            loading={formLoading || optionsLoading}
          />
        </div>
      )}

      {viewMode === 'edit' && editingInvoice && (
        <div className="bg-white rounded-lg border border-[var(--color-border)]">
          <div className="p-6 border-b border-[var(--color-border)]">
            <h2 className="text-xl font-semibold">청구서 수정</h2>
          </div>
          <InvoiceForm
            invoice={editingInvoice}
            onSubmit={handleUpdate as (data: InvoiceCreateRequest | InvoiceUpdateRequest) => Promise<void>}
            onCancel={handleCancel}
            loading={formLoading}
          />
        </div>
      )}
    </div>
  );
}
