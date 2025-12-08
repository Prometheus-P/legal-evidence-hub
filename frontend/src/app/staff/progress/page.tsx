"use client";

export const dynamic = "force-static";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import clsx from "clsx";
import {
  CaseProgressSummary,
  FeedbackChecklistItem,
  getStaffProgress,
  updateChecklistItem,
} from "@/lib/api/staffProgress";

type LoadingState = "idle" | "loading" | "error";

const statusLabels: Record<string, string> = {
  open: "진행 중",
  in_progress: "검토 대기",
  closed: "종결",
  active: "활성",
};

const statusColors: Record<string, string> = {
  open: "bg-blue-50 text-blue-700",
  in_progress: "bg-amber-50 text-amber-700",
  closed: "bg-gray-100 text-gray-700",
  active: "bg-emerald-50 text-emerald-700",
};

function formatDate(value?: string) {
  if (!value) return "-";
  return new Date(value).toLocaleString("ko-KR", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  });
}

function getStatusLabel(status: string) {
  return statusLabels[status] ?? status;
}

export default function StaffProgressPage() {
  const [progress, setProgress] = useState<CaseProgressSummary[]>([]);
  const [state, setState] = useState<LoadingState>("idle");
  const [error, setError] = useState<string | null>(null);
  const [blockedOnly, setBlockedOnly] = useState(false);
  const [assigneeId, setAssigneeId] = useState("");
  const [updatingChecklist, setUpdatingChecklist] = useState<string | null>(null);
  const [toast, setToast] = useState<{ type: "success" | "error"; message: string } | null>(null);
  const toastTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null);

  const loadProgress = useCallback(async () => {
    setState("loading");
    setError(null);
    const response = await getStaffProgress({
      blocked_only: blockedOnly,
      assignee_id: assigneeId || undefined,
    });
    if (response.error) {
      setError(response.error);
      setState("error");
      return;
    }
    setProgress(response.data ?? []);
    setState("idle");
  }, [assigneeId, blockedOnly]);

  useEffect(() => {
    void loadProgress();
  }, [loadProgress]);

  useEffect(() => {
    return () => {
      if (toastTimeoutRef.current) {
        clearTimeout(toastTimeoutRef.current);
      }
    };
  }, []);

  const showToast = useCallback((type: "success" | "error", message: string) => {
    if (toastTimeoutRef.current) {
      clearTimeout(toastTimeoutRef.current);
    }
    setToast({ type, message });
    toastTimeoutRef.current = setTimeout(() => setToast(null), 4000);
  }, []);

  const handleChecklistToggle = useCallback(
    async (caseId: string, item: FeedbackChecklistItem) => {
      const nextStatus = item.status.toLowerCase() === "done" ? "pending" : "done";
      setUpdatingChecklist(`${caseId}:${item.item_id}`);
      try {
        const response = await updateChecklistItem(caseId, item.item_id, {
          status: nextStatus,
        });
        setUpdatingChecklist(null);
        if (response.error || !response.data) {
          const message = response.error ?? "체크리스트를 업데이트할 수 없습니다.";
          setError(message);
          showToast("error", message);
          return;
        }
        setProgress((prev) =>
          prev.map((entry) => {
            if (entry.case_id !== caseId) return entry;
            const updatedItems = entry.feedback_items.map((fi) =>
              fi.item_id === item.item_id ? response.data! : fi
            );
            return {
              ...entry,
              feedback_items: updatedItems,
              outstanding_feedback_count: updatedItems.reduce(
                (count, fi) => count + (fi.status.toLowerCase() !== "done" ? 1 : 0),
                0
              ),
            };
          })
        );
        const actionLabel = nextStatus === "done" ? "완료 처리했습니다." : "대기 상태로 전환했습니다.";
        showToast("success", `${item.title} 항목을 ${actionLabel}`);
      } catch (toggleError) {
        setUpdatingChecklist(null);
        const message = toggleError instanceof Error ? toggleError.message : "체크리스트를 업데이트할 수 없습니다.";
        showToast("error", message);
      }
    },
    [showToast]
  );

  const summary = useMemo(() => {
    if (!progress.length) {
      return {
        total: 0,
        blocked: 0,
        ready: 0,
        processing: 0,
      };
    }
    return progress.reduce(
      (acc, item) => {
        acc.total += 1;
        if (item.is_blocked) acc.blocked += 1;
        if (item.ai_status === "ready") acc.ready += 1;
        if (item.ai_status === "processing") acc.processing += 1;
        return acc;
      },
      { total: 0, blocked: 0, ready: 0, processing: 0 }
    );
  }, [progress]);

  return (
    <section className="space-y-6 p-6">
      <header className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
        <div>
          <p className="text-sm text-neutral-500">Paralegal Command Center</p>
          <h1 className="text-3xl font-bold tracking-tight">
            진행 상황 모니터링
          </h1>
          <p className="text-sm text-neutral-500 mt-1">
            케이스, 증거, AI 분석 상태와 피드백 항목을 한곳에서 확인하세요.
          </p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row sm:items-center">
          <label className="flex items-center gap-2 text-sm text-neutral-600">
            <input
              type="checkbox"
              checked={blockedOnly}
              onChange={(event) => setBlockedOnly(event.target.checked)}
              className="h-4 w-4 rounded border-neutral-300 text-primary focus:ring-primary"
            />
            블로킹 케이스만
          </label>
          <input
            type="text"
            placeholder="담당자 ID"
            value={assigneeId}
            onChange={(event) => setAssigneeId(event.target.value)}
            className="w-full sm:w-48 rounded-md border border-neutral-200 px-3 py-2 text-sm focus:border-primary focus:outline-none"
          />
          <button
            type="button"
            onClick={() => void loadProgress()}
            className="inline-flex items-center justify-center rounded-md border border-transparent bg-primary px-4 py-2 text-sm font-medium text-white hover:bg-primary/90 transition"
          >
            새로고침
          </button>
        </div>
      </header>

      {toast && (
        <div
          className={clsx(
            "rounded-md border px-4 py-2 text-sm",
            toast.type === "success"
              ? "border-emerald-200 bg-emerald-50 text-emerald-700"
              : "border-rose-200 bg-rose-50 text-rose-700"
          )}
        >
          {toast.message}
        </div>
      )}

      <section className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        <SummaryCard label="총 배정" value={summary.total} />
        <SummaryCard label="블로킹" value={summary.blocked} accent="text-rose-600" />
        <SummaryCard label="AI 완료" value={summary.ready} accent="text-emerald-600" />
        <SummaryCard
          label="AI 처리중"
          value={summary.processing}
          accent="text-amber-600"
        />
      </section>

      {state === "error" && (
        <div className="rounded-md border border-rose-200 bg-rose-50 p-4 text-sm text-rose-700">
          {error ?? "진행 상황을 불러오는 중 오류가 발생했습니다."}
        </div>
      )}

      {state === "loading" && (
        <div className="space-y-4">
          {Array.from({ length: 3 }).map((_, index) => (
            <SkeletonCard key={index} />
          ))}
        </div>
      )}

      {state !== "loading" && !progress.length && (
        <div className="rounded-md border border-dashed border-neutral-300 p-10 text-center text-neutral-500">
          표시할 케이스가 없습니다. 필터를 변경하거나 케이스를 배정해 주세요.
        </div>
      )}

      <div className="grid gap-4 md:grid-cols-2">
        {progress.map((item) => (
          <ProgressCard
            key={item.case_id}
            progress={item}
            updatingChecklist={updatingChecklist}
            onChecklistToggle={handleChecklistToggle}
          />
        ))}
      </div>
    </section>
  );
}

function SummaryCard({
  label,
  value,
  accent = "text-neutral-900",
}: {
  label: string;
  value: number;
  accent?: string;
}) {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm">
      <p className="text-sm text-neutral-500">{label}</p>
      <p className={`mt-2 text-3xl font-semibold ${accent}`}>{value}</p>
    </div>
  );
}

function SkeletonCard() {
  return (
    <div className="rounded-lg border border-neutral-200 bg-white p-4 shadow-sm animate-pulse space-y-4">
      <div className="h-4 rounded bg-neutral-200" />
      <div className="h-3 rounded bg-neutral-100" />
      <div className="h-3 rounded bg-neutral-100" />
      <div className="h-3 rounded bg-neutral-100 w-2/3" />
    </div>
  );
}

function ProgressCard({
  progress,
  updatingChecklist,
  onChecklistToggle,
}: {
  progress: CaseProgressSummary;
  updatingChecklist: string | null;
  onChecklistToggle: (caseId: string, item: FeedbackChecklistItem) => void;
}) {
  const statusClass =
    statusColors[progress.status] ?? "bg-neutral-100 text-neutral-700";
  const blockedBadge = progress.is_blocked ? (
    <span className="rounded-full bg-rose-50 px-2.5 py-1 text-xs font-medium text-rose-700">
      Blocked · {progress.blocked_reason === "evidence_failed" ? "증거 실패" : "점검 필요"}
    </span>
  ) : null;
  const feedbackComplete = progress.outstanding_feedback_count === 0;

  return (
    <article className="rounded-lg border border-neutral-200 bg-white p-6 shadow-sm hover:shadow transition">
      <div className="flex items-start justify-between gap-2">
        <div>
          <p className="text-xs uppercase tracking-wide text-neutral-400">
            {progress.case_id}
          </p>
          <h2 className="text-xl font-semibold text-neutral-900">
            {progress.title}
          </h2>
          {progress.client_name && (
            <p className="text-sm text-neutral-500">{progress.client_name}</p>
          )}
        </div>
        <span className={`rounded-full px-2.5 py-1 text-xs font-medium ${statusClass}`}>
          {getStatusLabel(progress.status)}
        </span>
      </div>

      <div className="mt-4 flex flex-wrap items-center gap-2 text-sm text-neutral-600">
        <span>담당자: {progress.assignee.name}</span>
        <span className="text-neutral-300">|</span>
        <span>AI 상태: {progress.ai_status}</span>
        <span className="text-neutral-300">|</span>
        <span>최종 업데이트: {formatDate(progress.updated_at)}</span>
      </div>

      {blockedBadge && <div className="mt-2">{blockedBadge}</div>}

      <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
        <Metric label="처리 완료" value={progress.evidence_counts.completed} />
        <Metric label="처리 중" value={progress.evidence_counts.processing} />
        <Metric label="대기" value={progress.evidence_counts.uploaded + progress.evidence_counts.pending} />
        <Metric label="실패" value={progress.evidence_counts.failed} />
      </dl>

      <div className="mt-4 rounded-lg border border-neutral-100 bg-neutral-50 p-4">
        {feedbackComplete ? (
          <div className="rounded-md border border-emerald-200 bg-emerald-50 px-3 py-2 text-sm font-medium text-emerald-700">
            모든 피드백을 완료했습니다.
          </div>
        ) : (
          <p className="text-sm font-medium text-neutral-700">
            피드백 항목 ({progress.outstanding_feedback_count} 미완료)
          </p>
        )}
        <FeedbackChecklist
          items={progress.feedback_items}
          caseId={progress.case_id}
          onToggle={onChecklistToggle}
          updatingKey={updatingChecklist}
        />
      </div>
    </article>
  );
}

function Metric({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded border border-neutral-200 bg-white px-3 py-2 text-center">
      <dt className="text-xs text-neutral-500">{label}</dt>
      <dd className="text-lg font-semibold text-neutral-900">{value}</dd>
    </div>
  );
}

function FeedbackChecklist({
  items,
  caseId,
  onToggle,
  updatingKey,
}: {
  items: CaseProgressSummary["feedback_items"];
  caseId: string;
  onToggle: (caseId: string, item: FeedbackChecklistItem) => void;
  updatingKey: string | null;
}) {
  if (!items?.length) {
    return <p className="mt-2 text-sm text-neutral-500">등록된 피드백이 없습니다.</p>;
  }

  return (
    <ul className="mt-3 space-y-2">
      {items.map((item) => {
        const done = item.status.toLowerCase() === "done";
        const itemClasses = clsx(
          "flex items-start gap-2 rounded border px-3 py-2",
          done ? "border-neutral-200 bg-white" : "border-amber-200 bg-amber-50"
        );
        const isUpdating = updatingKey === `${caseId}:${item.item_id}`;
        return (
          <li key={item.item_id} className={itemClasses}>
            <span
              className={`mt-1 h-2 w-2 rounded-full ${
                done ? "bg-emerald-500" : "bg-amber-500"
              }`}
            />
            <div className="flex-1">
              <p className="text-sm font-medium text-neutral-800">
                {item.title}
              </p>
              {item.description && (
                <p className="text-xs text-neutral-500">{item.description}</p>
              )}
              {item.owner && (
                <p className="text-xs text-neutral-500">담당: {item.owner}</p>
              )}
              {item.notes && (
                <p className="text-xs text-neutral-500">메모: {item.notes}</p>
              )}
              {item.updated_at && (
                <p className="text-xs text-neutral-400">
                  업데이트: {formatDate(item.updated_at)}
                </p>
              )}
            </div>
            <div className="flex flex-col items-end gap-1">
              <span className="text-xs text-neutral-500">
                {done ? "완료" : "대기"}
              </span>
              <button
                type="button"
                onClick={() => onToggle(caseId, item)}
                disabled={isUpdating}
                className={clsx(
                  "rounded border px-2 py-1 text-xs font-medium transition",
                  done
                    ? "border-neutral-200 text-neutral-600 hover:bg-neutral-50"
                    : "border-emerald-200 text-emerald-700 hover:bg-emerald-50",
                  isUpdating && "opacity-50"
                )}
              >
                {done ? "대기 전환" : "완료 처리"}
              </button>
            </div>
          </li>
        );
      })}
    </ul>
  );
}
