export type FinancialRecord = {
  financial_record_id: number;
  company_id: number;
  fiscal_year: number;
  revenue: string | null;
  net_profit: string | null;
  total_assets: string | null;
  total_liabilities: string | null;
  total_debt: string | null;
  shareholders_equity: string | null;
  operating_cash_flow: string | null;
  created_at: string;
};

export class FinancialRecordsApiError extends Error {
  constructor(
    message: string,
    readonly status?: number,
  ) {
    super(message);
    this.name = "FinancialRecordsApiError";
  }
}

const financialRecordFields = [
  "financial_record_id",
  "company_id",
  "fiscal_year",
  "revenue",
  "net_profit",
  "total_assets",
  "total_liabilities",
  "total_debt",
  "shareholders_equity",
  "operating_cash_flow",
  "created_at",
] as const;

const decimalPattern = /^[+-]?(?:\d+(?:\.\d*)?|\.\d+)$/;

function isInteger(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value);
}

function isDecimalString(value: unknown): value is string | null {
  return value === null || (typeof value === "string" && decimalPattern.test(value));
}

function isFinancialRecord(value: unknown): value is FinancialRecord {
  if (typeof value !== "object" || value === null || Array.isArray(value)) {
    return false;
  }

  const record = value as Record<string, unknown>;
  const keys = Object.keys(record);
  return (
    keys.length === financialRecordFields.length &&
    financialRecordFields.every((field) => Object.hasOwn(record, field)) &&
    isInteger(record.financial_record_id) &&
    isInteger(record.company_id) &&
    isInteger(record.fiscal_year) &&
    isDecimalString(record.revenue) &&
    isDecimalString(record.net_profit) &&
    isDecimalString(record.total_assets) &&
    isDecimalString(record.total_liabilities) &&
    isDecimalString(record.total_debt) &&
    isDecimalString(record.shareholders_equity) &&
    isDecimalString(record.operating_cash_flow) &&
    typeof record.created_at === "string"
  );
}

export async function getFinancialRecords(
  token: string,
  companyId: number,
): Promise<FinancialRecord[]> {
  if (!process.env.NEXT_PUBLIC_API_BASE_URL?.trim()) {
    throw new FinancialRecordsApiError(
      "The API is not configured. Set NEXT_PUBLIC_API_BASE_URL in frontend/.env.local.",
    );
  }

  let response: Response;
  try {
    response = await fetch(
      `/api/v1/companies/${encodeURIComponent(companyId)}/financial-records`,
      {
        headers: {
          Accept: "application/json",
          Authorization: `Bearer ${token}`,
        },
      },
    );
  } catch {
    throw new FinancialRecordsApiError(
      "Could not reach the AEGIS API. Check the backend connection and API URL.",
    );
  }

  if (!response.ok) {
    switch (response.status) {
      case 401:
        throw new FinancialRecordsApiError("Your session has expired. Please sign in again.", 401);
      case 404:
        throw new FinancialRecordsApiError("The selected company could not be found.", 404);
      case 422:
        throw new FinancialRecordsApiError("The financial records request was invalid.", 422);
      default:
        if (response.status >= 500) {
          throw new FinancialRecordsApiError(
            "Financial records are temporarily unavailable. Please try again later.",
            response.status,
          );
        }
        throw new FinancialRecordsApiError(
          "Could not load financial records. Please try again.",
          response.status,
        );
    }
  }

  let result: unknown;
  try {
    result = await response.json();
  } catch {
    throw new FinancialRecordsApiError("The API returned an unreadable financial records response.");
  }

  if (!Array.isArray(result) || !result.every(isFinancialRecord)) {
    throw new FinancialRecordsApiError(
      "The API returned financial records in an unexpected format.",
    );
  }

  return result;
}
