export type RiskLevel = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";

export type RiskSummaryResponse = {
  company_id: number;
  company_name: string;
  current_risk_level: RiskLevel | null;
  current_risk_score: number | null;
  assessed_at: string | null;
  model_version: string | null;
};

export type RiskAssessmentResponse = {
  risk_assessment_id: number;
  company_id: number;
  risk_score: number;
  risk_level: RiskLevel;
  assessed_at: string;
  model_version: string | null;
  explanation: string | null;
  assessed_by: number | null;
};

export class RiskAssessmentsApiError extends Error {
  constructor(
    message: string,
    readonly status?: number,
  ) {
    super(message);
    this.name = "RiskAssessmentsApiError";
  }
}

const riskLevels: RiskLevel[] = ["LOW", "MEDIUM", "HIGH", "CRITICAL"];

function isRiskLevel(value: unknown): value is RiskLevel {
  return typeof value === "string" && riskLevels.some((level) => level === value);
}

function isNullableString(value: unknown): value is string | null {
  return typeof value === "string" || value === null;
}

function parseRiskScore(value: unknown): number | null | undefined {
  if (value === null) {
    return null;
  }

  if (typeof value !== "number" && typeof value !== "string") {
    return undefined;
  }
  if (typeof value === "string" && !/^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$/.test(value)) {
    return undefined;
  }

  const score = typeof value === "number" ? value : Number(value);
  return Number.isFinite(score) && score >= 0 && score <= 100 ? score : undefined;
}

function normalizeRiskSummary(value: unknown): RiskSummaryResponse | null {
  if (typeof value !== "object" || value === null) {
    return null;
  }
  const summary = value as Record<string, unknown>;
  const score = parseRiskScore(summary.current_risk_score);
  if (
    typeof summary.company_id !== "number" ||
    typeof summary.company_name !== "string" ||
    (summary.current_risk_level !== null && !isRiskLevel(summary.current_risk_level)) ||
    score === undefined ||
    !isNullableString(summary.assessed_at) ||
    !isNullableString(summary.model_version)
  ) {
    return null;
  }

  return {
    company_id: summary.company_id,
    company_name: summary.company_name,
    current_risk_level: summary.current_risk_level,
    current_risk_score: score,
    assessed_at: summary.assessed_at,
    model_version: summary.model_version,
  };
}

function normalizeRiskAssessment(value: unknown): RiskAssessmentResponse | null {
  if (typeof value !== "object" || value === null) {
    return null;
  }
  const assessment = value as Record<string, unknown>;
  const score = parseRiskScore(assessment.risk_score);
  if (
    typeof assessment.risk_assessment_id !== "number" ||
    typeof assessment.company_id !== "number" ||
    score === null ||
    score === undefined ||
    !isRiskLevel(assessment.risk_level) ||
    typeof assessment.assessed_at !== "string" ||
    !isNullableString(assessment.model_version) ||
    !isNullableString(assessment.explanation) ||
    (typeof assessment.assessed_by !== "number" && assessment.assessed_by !== null)
  ) {
    return null;
  }

  return {
    risk_assessment_id: assessment.risk_assessment_id,
    company_id: assessment.company_id,
    risk_score: score,
    risk_level: assessment.risk_level,
    assessed_at: assessment.assessed_at,
    model_version: assessment.model_version,
    explanation: assessment.explanation,
    assessed_by: assessment.assessed_by,
  };
}

async function get<T>(
  path: string,
  token: string,
  normalizeResponse: (value: unknown) => T | null,
): Promise<T> {
  if (!process.env.NEXT_PUBLIC_API_BASE_URL?.trim()) {
    throw new RiskAssessmentsApiError(
      "The API is not configured. Set NEXT_PUBLIC_API_BASE_URL in frontend/.env.local.",
    );
  }

  let response: Response;
  try {
    response = await fetch(path, {
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
  } catch {
    throw new RiskAssessmentsApiError(
      "Could not reach the AEGIS API. Check the backend connection and API URL.",
    );
  }

  if (!response.ok) {
    switch (response.status) {
      case 401:
        throw new RiskAssessmentsApiError("Your session has expired. Please sign in again.", 401);
      case 403:
        throw new RiskAssessmentsApiError("You do not have permission to view risk assessments.", 403);
      case 404:
        throw new RiskAssessmentsApiError("The selected company could not be found.", 404);
      case 422:
        throw new RiskAssessmentsApiError("The risk assessment request was invalid.", 422);
      default:
        if (response.status >= 500) {
          throw new RiskAssessmentsApiError(
            "Risk assessment data is temporarily unavailable. Please try again later.",
            response.status,
          );
        }
        throw new RiskAssessmentsApiError(
          "Could not load risk assessment data. Please try again.",
          response.status,
        );
    }
  }

  let result: unknown;
  try {
    result = await response.json();
  } catch {
    throw new RiskAssessmentsApiError("The API returned an unreadable risk assessment response.");
  }

  const normalized = normalizeResponse(result);
  if (normalized === null) {
    throw new RiskAssessmentsApiError("The API returned risk assessment data in an unexpected format.");
  }

  return normalized;
}

export function getRiskSummary(token: string, companyId: number): Promise<RiskSummaryResponse> {
  return get(
    `/api/v1/companies/${encodeURIComponent(companyId)}/risk-summary`,
    token,
    normalizeRiskSummary,
  );
}

export function getRiskAssessments(
  token: string,
  companyId: number,
): Promise<RiskAssessmentResponse[]> {
  return get(
    `/api/v1/companies/${encodeURIComponent(companyId)}/risk-assessments`,
    token,
    (value) => {
      if (!Array.isArray(value)) {
        return null;
      }

      const assessments = value.map(normalizeRiskAssessment);
      return assessments.every((assessment) => assessment !== null)
        ? assessments
        : null;
    },
  );
}
