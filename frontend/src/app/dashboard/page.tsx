"use client";

import { useEffect, useState, useSyncExternalStore } from "react";
import { useRouter } from "next/navigation";
import AppSidebar from "@/components/app-sidebar";
import {
  clearSessionToken,
  getSessionToken,
  hasActiveSession,
  logout,
  subscribeToSession,
} from "@/lib/auth";
import { CompaniesApiError, getCompanies } from "@/lib/companies";
import type { Company } from "@/lib/companies";
import {
  FinancialRecordsApiError,
  getFinancialRecords,
} from "@/lib/financial-records";
import type { FinancialRecord } from "@/lib/financial-records";
import {
  getRiskAssessments,
  getRiskSummary,
  RiskAssessmentsApiError,
} from "@/lib/risk-assessments";
import type {
  RiskAssessmentResponse,
  RiskSummaryResponse,
} from "@/lib/risk-assessments";

export default function DashboardPage() {
  const router = useRouter();
  const hasSession = useSyncExternalStore(subscribeToSession, hasActiveSession, () => false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [isLoadingCompanies, setIsLoadingCompanies] = useState(true);
  const [companiesError, setCompaniesError] = useState("");
  const [selectedCompanyId, setSelectedCompanyId] = useState("");
  const [riskState, setRiskState] = useState<RiskViewState>({ status: "idle" });
  const [financialRecordsState, setFinancialRecordsState] =
    useState<FinancialRecordsViewState>({ status: "idle" });

  useEffect(() => {
    if (!hasSession) {
      router.replace("/");
      return;
    }

    let isCurrent = true;
    async function loadCompanies() {
      const token = getSessionToken();
      if (!token) {
        router.replace("/");
        return;
      }

      try {
        const result = await getCompanies(token);
        if (isCurrent) {
          setCompanies(result);
        }
      } catch (error) {
        if (!isCurrent) {
          return;
        }
        if (error instanceof CompaniesApiError && error.status === 401) {
          clearSessionToken();
          router.replace("/");
          return;
        }
        setCompaniesError(
          error instanceof Error ? error.message : "Could not load companies. Please try again.",
        );
      } finally {
        if (isCurrent) {
          setIsLoadingCompanies(false);
        }
      }
    }

    void loadCompanies();
    return () => {
      isCurrent = false;
    };
  }, [hasSession, router]);

  useEffect(() => {
    if (!selectedCompanyId || !hasSession) {
      return;
    }

    let isCurrent = true;
    async function loadRiskData() {
      const token = getSessionToken();
      if (!token) {
        router.replace("/");
        return;
      }

      const companyId = Number(selectedCompanyId);
      const results = await Promise.allSettled([
        getRiskSummary(token, companyId),
        getRiskAssessments(token, companyId),
      ]);
      if (!isCurrent) {
        return;
      }

      const unauthorized = results.some(
        (result) =>
          result.status === "rejected" &&
          result.reason instanceof RiskAssessmentsApiError &&
          result.reason.status === 401,
      );
      if (unauthorized) {
        clearSessionToken();
        router.replace("/");
        return;
      }

      if (results[0].status === "fulfilled" && results[1].status === "fulfilled") {
        setRiskState({
          status: "loaded",
          summary: results[0].value,
          assessments: results[1].value,
        });
      } else {
        const failure = results.find((result) => result.status === "rejected");
        const error = failure?.status === "rejected" ? failure.reason : null;
        setRiskState({
          status: "error",
          message:
            error instanceof Error
              ? error.message
              : "Could not load risk assessment data. Please try again.",
        });
      }
    }

    void loadRiskData();
    return () => {
      isCurrent = false;
    };
  }, [hasSession, router, selectedCompanyId]);

  useEffect(() => {
    if (!selectedCompanyId || !hasSession) {
      return;
    }

    let isCurrent = true;
    async function loadFinancialRecords() {
      const token = getSessionToken();
      if (!token) {
        router.replace("/");
        return;
      }

      setFinancialRecordsState({ status: "loading" });
      try {
        const records = await getFinancialRecords(token, Number(selectedCompanyId));
        if (isCurrent) {
          setFinancialRecordsState({ status: "loaded", records });
        }
      } catch (error) {
        if (!isCurrent) {
          return;
        }
        if (error instanceof FinancialRecordsApiError && error.status === 401) {
          clearSessionToken();
          router.replace("/");
          return;
        }
        setFinancialRecordsState({
          status: "error",
          message:
            error instanceof Error
              ? error.message
              : "Could not load financial records. Please try again.",
        });
      }
    }

    void loadFinancialRecords();
    return () => {
      isCurrent = false;
    };
  }, [hasSession, router, selectedCompanyId]);

  async function handleLogout() {
    const token = getSessionToken();
    setIsLoggingOut(true);

    try {
      if (token) {
        await logout(token);
      }
      clearSessionToken();
      router.replace("/");
    } catch {
      clearSessionToken();
      router.replace("/?logout=failed");
    }
  }

  if (!hasSession) {
    return (
      <main className="flex min-h-screen items-center justify-center bg-[#f5f7fb] text-sm text-slate-500">
        Checking your session...
      </main>
    );
  }

  return (
    <div className="min-h-screen bg-[#f5f7fb] md:flex">
      <AppSidebar />
      <div className="min-w-0 flex-1">
        <div className="mx-auto max-w-6xl px-5 py-8 sm:px-8 lg:px-10 lg:py-11">
          <div className="mb-8 flex flex-wrap items-start justify-between gap-4">
            <header>
              <p className="text-xs font-semibold uppercase tracking-[0.16em] text-[#5471a6]">
                Overview
              </p>
              <h1 className="mt-2 text-3xl font-semibold tracking-tight text-[#14213d]">
                Your workspace
              </h1>
              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-500">
                Your AEGIS session is active. Company information is loaded from your workspace.
              </p>
            </header>
            <button
              className="rounded-lg border border-slate-200 bg-white px-4 py-2.5 text-sm font-semibold text-slate-700 transition hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
              disabled={isLoggingOut}
              onClick={handleLogout}
              type="button"
            >
              {isLoggingOut ? "Signing out..." : "Sign out"}
            </button>
          </div>

          <section aria-labelledby="companies-heading" className="mb-8">
            <div className="mb-4 flex flex-wrap items-baseline justify-between gap-2">
              <h2 className="text-xl font-semibold tracking-tight text-[#14213d]" id="companies-heading">
                Company monitoring
              </h2>
              {!isLoadingCompanies && !companiesError && companies.length > 0 && (
                <p className="text-sm text-slate-500" aria-live="polite">
                  {companies.length} {companies.length === 1 ? "company" : "companies"}
                </p>
              )}
            </div>

            {isLoadingCompanies ? (
              <div
                aria-live="polite"
                className="rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-500 shadow-sm"
                role="status"
              >
                Loading companies...
              </div>
            ) : companiesError ? (
              <div
                aria-live="assertive"
                className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-800"
                role="alert"
              >
                {companiesError}
              </div>
            ) : companies.length === 0 ? (
              <div className="rounded-xl border border-dashed border-slate-300 bg-white/70 px-5 py-8 text-center">
                <p className="text-sm font-medium text-slate-700">No companies found.</p>
                <p className="mt-1 text-xs leading-5 text-slate-500">
                  Companies will appear here when they are available in your workspace.
                </p>
              </div>
            ) : (
              <ul className="grid list-none gap-4 p-0 sm:grid-cols-2 xl:grid-cols-3">
                {companies.map((company) => (
                  <li key={company.company_id}>
                    <CompanyCard company={company} />
                  </li>
                ))}
              </ul>
            )}
            {!isLoadingCompanies && !companiesError && companies.length > 0 && (
              <div className="mt-5 max-w-md">
                <label
                  className="mb-2 block text-sm font-medium text-slate-700"
                  htmlFor="risk-company"
                >
                  Select a company to view risk assessments
                </label>
                <select
                  className="w-full rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm text-slate-900 outline-none transition focus:border-[#5272ad] focus:ring-4 focus:ring-[#5272ad]/10"
                  id="risk-company"
                  onChange={(event) => {
                    setSelectedCompanyId(event.target.value);
                    setRiskState(
                      event.target.value ? { status: "loading" } : { status: "idle" },
                    );
                    setFinancialRecordsState(
                      event.target.value ? { status: "loading" } : { status: "idle" },
                    );
                  }}
                  value={selectedCompanyId}
                >
                  <option value="">Choose a company</option>
                  {companies.map((company) => (
                    <option key={company.company_id} value={company.company_id}>
                      {company.company_name}
                    </option>
                  ))}
                </select>
              </div>
            )}
          </section>

          {selectedCompanyId && (
            <>
              <RiskAssessmentSection state={riskState} />
              <FinancialRecordsSection state={financialRecordsState} />
            </>
          )}
        </div>
      </div>
    </div>
  );
}

function CompanyCard({ company }: { company: Company }) {
  const details = [
    { label: "Industry", value: company.industry },
    { label: "Country", value: company.country },
    {
      label: "Employees",
      value: company.employee_count === null ? null : company.employee_count.toLocaleString(),
    },
    { label: "Annual revenue", value: company.annual_revenue },
  ];

  return (
    <article className="h-full rounded-xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-200/40">
      <h3 className="text-base font-semibold text-[#14213d]">{company.company_name}</h3>
      <dl className="mt-4 grid grid-cols-2 gap-x-4 gap-y-4">
        {details.map((detail) => (
          <div key={detail.label}>
            <dt className="text-xs font-medium text-slate-400">{detail.label}</dt>
            <dd className="mt-1 break-words text-sm text-slate-700">
              {detail.value ?? "Not provided"}
            </dd>
          </div>
        ))}
      </dl>
    </article>
  );
}

type RiskViewState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "error"; message: string }
  | {
      status: "loaded";
      summary: RiskSummaryResponse;
      assessments: RiskAssessmentResponse[];
    };

type FinancialRecordsViewState =
  | { status: "idle" }
  | { status: "loading" }
  | { status: "error"; message: string }
  | { status: "loaded"; records: FinancialRecord[] };

function FinancialRecordsSection({ state }: { state: FinancialRecordsViewState }) {
  return (
    <section aria-labelledby="financial-records-heading" className="mb-8">
      <h2
        className="mb-4 text-xl font-semibold tracking-tight text-[#14213d]"
        id="financial-records-heading"
      >
        Financial records
      </h2>
      {state.status === "loading" || state.status === "idle" ? (
        <div
          aria-live="polite"
          className="rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-500 shadow-sm"
          role="status"
        >
          Loading financial records...
        </div>
      ) : state.status === "error" ? (
        <div
          aria-live="assertive"
          className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-800"
          role="alert"
        >
          {state.message}
        </div>
      ) : state.records.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white/70 px-5 py-8 text-center">
          <p className="text-sm font-medium text-slate-700">No financial records yet.</p>
        </div>
      ) : (
        <ul className="grid list-none gap-4 p-0">
          {state.records.map((record) => (
            <li key={record.financial_record_id}>
              <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-200/40">
                <h3 className="text-base font-semibold text-[#14213d]">
                  Fiscal year {record.fiscal_year}
                </h3>
                <dl className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
                  <FinancialRecordDetail label="Revenue" value={record.revenue} />
                  <FinancialRecordDetail label="Net profit" value={record.net_profit} />
                  <FinancialRecordDetail label="Total assets" value={record.total_assets} />
                  <FinancialRecordDetail
                    label="Total liabilities"
                    value={record.total_liabilities}
                  />
                  <FinancialRecordDetail label="Total debt" value={record.total_debt} />
                  <FinancialRecordDetail
                    label="Shareholders' equity"
                    value={record.shareholders_equity}
                  />
                  <FinancialRecordDetail
                    label="Operating cash flow"
                    value={record.operating_cash_flow}
                  />
                  <div>
                    <dt className="text-xs font-medium text-slate-400">Created</dt>
                    <dd className="mt-1 break-words text-sm text-slate-700">
                      {formatDate(record.created_at) ?? "—"}
                    </dd>
                  </div>
                </dl>
              </article>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

function FinancialRecordDetail({ label, value }: { label: string; value: string | null }) {
  return (
    <div>
      <dt className="text-xs font-medium text-slate-400">{label}</dt>
      <dd className="mt-1 break-words text-sm text-slate-700">{formatFinancialValue(value)}</dd>
    </div>
  );
}

function formatFinancialValue(value: string | null): string {
  if (value === null) {
    return "—";
  }

  const decimal = value.match(/^([+-]?)(\d+)(\.\d+)?$/);
  if (!decimal) {
    return value;
  }

  const [, sign, integer, fraction = ""] = decimal;
  return `${sign}${integer.replace(/\B(?=(\d{3})+(?!\d))/g, ",")}${fraction}`;
}

function RiskAssessmentSection({ state }: { state: RiskViewState }) {
  return (
    <section aria-labelledby="risk-assessments-heading" className="mb-8">
      <h2
        className="mb-4 text-xl font-semibold tracking-tight text-[#14213d]"
        id="risk-assessments-heading"
      >
        Risk assessments
      </h2>
      {state.status === "loading" || state.status === "idle" ? (
        <div
          aria-live="polite"
          className="rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-500 shadow-sm"
          role="status"
        >
          Loading risk assessments...
        </div>
      ) : state.status === "error" ? (
        <div
          aria-live="assertive"
          className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-800"
          role="alert"
        >
          {state.message}
        </div>
      ) : !state.summary.current_risk_level &&
        state.summary.current_risk_score === null &&
        state.summary.assessed_at === null &&
        state.summary.model_version === null &&
        state.assessments.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white/70 px-5 py-8 text-center">
          <p className="text-sm font-medium text-slate-700">No risk assessment yet.</p>
        </div>
      ) : (
        <div className="space-y-4">
          <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-200/40">
            <h3 className="text-base font-semibold text-[#14213d]">
              Current risk — {state.summary.company_name}
            </h3>
            <dl className="mt-4 grid grid-cols-2 gap-4 sm:grid-cols-4">
              <RiskDetail label="Risk level" value={state.summary.current_risk_level} />
              <RiskDetail label="Risk score" value={formatRiskScore(state.summary.current_risk_score)} />
              <RiskDetail label="Assessment date" value={formatDate(state.summary.assessed_at)} />
              <RiskDetail label="Model version" value={state.summary.model_version} />
            </dl>
          </article>

          <div>
            <h3 className="mb-3 text-base font-semibold text-[#14213d]">Assessment history</h3>
            {state.assessments.length === 0 ? (
              <p className="rounded-xl border border-slate-200 bg-white p-5 text-sm text-slate-500">
                No assessment history is available.
              </p>
            ) : (
              <ul className="grid list-none gap-3 p-0">
                {state.assessments.map((assessment) => (
                  <li key={assessment.risk_assessment_id}>
                    <article className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-200/40">
                      <dl className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                        <RiskDetail label="Risk level" value={assessment.risk_level} />
                        <RiskDetail label="Risk score" value={formatRiskScore(assessment.risk_score)} />
                        <RiskDetail label="Assessment date" value={formatDate(assessment.assessed_at)} />
                        <RiskDetail label="Model version" value={assessment.model_version} />
                      </dl>
                      {assessment.explanation && (
                        <p className="mt-4 border-t border-slate-100 pt-4 text-sm leading-6 text-slate-600">
                          {assessment.explanation}
                        </p>
                      )}
                    </article>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </section>
  );
}

function RiskDetail({ label, value }: { label: string; value: string | null }) {
  return (
    <div>
      <dt className="text-xs font-medium text-slate-400">{label}</dt>
      <dd className="mt-1 break-words text-sm text-slate-700">{value ?? "Not available"}</dd>
    </div>
  );
}

function formatRiskScore(score: number | null): string | null {
  return score === null ? null : score.toLocaleString(undefined, { maximumFractionDigits: 2 });
}

function formatDate(value: string | null): string | null {
  if (value === null) {
    return null;
  }
  const date = new Date(value);
  return Number.isNaN(date.getTime()) ? value : date.toLocaleString();
}
