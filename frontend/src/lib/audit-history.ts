import type { RiskLevel } from "@/lib/risk-assessments";

export type AuditHistoryRecord = {
  audit_id: number;
  risk_assessment_id: number;
  company_id: number;
  risk_score: number;
  logged_at: string;
  action_type: "INSERT";
  risk_level: RiskLevel;
  model_version: string | null;
  explanation: string | null;
  assessed_by: number | null;
};

export class AuditHistoryApiError extends Error {
  constructor(
    message: string,
    readonly status?: number,
  ) {
    super(message);
    this.name = "AuditHistoryApiError";
  }
}

const riskLevels: RiskLevel[] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];

function isNullableString(value: unknown): value is string | null {
  return typeof value === "string" || value === null;
}

function isInteger(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value);
}

function isRiskLevel(value: unknown): value is RiskLevel {
  return typeof value === "string" && riskLevels.some((level) => level === value);
}

function parseRiskScore(value: unknown): number | undefined {
  if (typeof value !== "number" && typeof value !== "string") {
    return undefined;
  }
  if (typeof value === "string" && !/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$/.test(value)) {
    return undefined;
  }

  const score = typeof value === "number" ? value : Number(value);
  return Number.isFinite(score) && score >= 0 && score <= 100 ? score : undefined;
}

function normalizeAuditHistoryRecord(value: unknown): AuditHistoryRecord | null {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return null;
  }

  const record = value as Record<string, unknown>;
  const score = parseRiskScore(record.risk_score);
  if (
    !isInteger(record.audit_id) ||
    !isInteger(record.risk_assessment_id) ||
    !isInteger(record.company_id) ||
    score === undefined ||
    typeof record.logged_at !== "string" ||
    record.action_type !== "INSERT" ||
    !isRiskLevel(record.risk_level) ||
    !isNullableString(record.model_version) ||
    !isNullableString(record.explanation) ||
    (!isInteger(record.assessed_by) && record.assessed_by !== null)
  ) {
    return null;
  }

  return {
    audit_id: record.audit_id,
    risk_assessment_id: record.risk_assessment_id,
    company_id: record.company_id,
    risk_score: score,
    logged_at: record.logged_at,
    action_type: "INSERT",
    risk_level: record.risk_level,
    model_version: record.model_version,
    explanation: record.explanation,
    assessed_by: record.assessed_by,
  };
}

export async function getAuditHistory(
  token: string,
  companyId: number,
): Promise<AuditHistoryRecord[]> {
  if (!process.env.NEXT_PUBLIC_API_BASE_URL?.trim()) {
    throw new AuditHistoryApiError(
      "The API is not configured. Set NEXT_PUBLIC_API_BASE_URL in frontend/.env.local.",
    );
  }

  let response: Response;
  try {
    response = await fetch(
      `/api/v1/companies/${encodeURIComponent(companyId)}/audit-history`,
      {
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
      },
    );
  } catch {
    throw new AuditHistoryApiError(
      "Could not reach the AEGIS API. Check the backend connection and API URL.",
    );
  }

  if (!response.ok) {
    switch (response.status) {
      case 401:
        throw new AuditHistoryApiError("Your session has expired. Please sign in again.", 401);
      case 403:
        throw new AuditHistoryApiError("You do not have permission to view audit history.", 403);
      case 404:
        throw new AuditHistoryApiError("The selected company could not be found.", 404);
      default:
        if (response.status >= 500) {
          throw new AuditHistoryApiError(
            "Audit history is temporarily unavailable. Please try again later.",
            response.status,
          );
        }
        throw new AuditHistoryApiError(
          "Could not load audit history. Please try again.",
          response.status,
        );
    }
  }

  let result: unknown;
  try {
    result = await response.json();
  } catch {
    throw new AuditHistoryApiError("The API returned an unreadable audit-history response.");
  }

  if (!Array.isArray(result)) {
    throw new AuditHistoryApiError(
      "The API returned audit-history data in an unexpected format.",
    );
  }

  const records = result.map(normalizeAuditHistoryRecord);
  if (records.some((record) => record === null)) {
    throw new AuditHistoryApiError(
      "The API returned audit-history data in an unexpected format.",
    );
  }
  return records.filter((record): record is AuditHistoryRecord => record !== null);
}
