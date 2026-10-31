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

const placeholderSections = [
  {
    title: "Risk assessments",
    description: "Assessment workflows and history will appear here.",
  },
  {
    title: "Financial records",
    description: "Financial record summaries will appear here.",
  },
];

export default function DashboardPage() {
  const router = useRouter();
  const hasSession = useSyncExternalStore(subscribeToSession, hasActiveSession, () => false);
  const [isLoggingOut, setIsLoggingOut] = useState(false);
  const [companies, setCompanies] = useState<Company[]>([]);
  const [isLoadingCompanies, setIsLoadingCompanies] = useState(true);
  const [companiesError, setCompaniesError] = useState("");

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
          </section>

          <section aria-label="Dashboard sections" className="grid gap-4 lg:grid-cols-2">
            {placeholderSections.map((section) => (
              <article
                className="rounded-xl border border-slate-200 bg-white p-5 shadow-sm shadow-slate-200/40"
                key={section.title}
              >
                <div className="mb-7 flex h-9 w-9 items-center justify-center rounded-lg bg-[#edf2fa]">
                  <span aria-hidden="true" className="h-2 w-2 rounded-full bg-[#5471a6]" />
                </div>
                <h2 className="text-base font-semibold text-[#14213d]">{section.title}</h2>
                <p className="mt-2 text-sm leading-6 text-slate-500">{section.description}</p>
                <p className="mt-5 border-t border-slate-100 pt-4 text-xs font-medium text-slate-400">
                  Not connected
                </p>
              </article>
            ))}
          </section>
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
