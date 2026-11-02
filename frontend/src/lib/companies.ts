export type Company = {
  company_id: number;
  company_name: string;
  registration_number: string | null;
  industry: string | null;
  country: string | null;
  annual_revenue: string | null;
  employee_count: number | null;
  created_at: string;
  updated_at: string;
};

export class CompaniesApiError extends Error {
  constructor(
    message: string,
    readonly status?: number,
  ) {
    super(message);
    this.name = "CompaniesApiError";
  }
}

function isCompany(value: unknown): value is Company {
  if (typeof value !== "object" || value === null) {
    return false;
  }
  const company = value as Record<string, unknown>;
  return (
    typeof company.company_id === "number" &&
    typeof company.company_name === "string" &&
    (typeof company.registration_number === "string" || company.registration_number === null) &&
    (typeof company.industry === "string" || company.industry === null) &&
    (typeof company.country === "string" || company.country === null) &&
    (typeof company.annual_revenue === "string" || company.annual_revenue === null) &&
    (typeof company.employee_count === "number" || company.employee_count === null) &&
    typeof company.created_at === "string" &&
    typeof company.updated_at === "string"
  );
}

export async function getCompanies(token: string): Promise<Company[]> {
  if (!process.env.NEXT_PUBLIC_API_BASE_URL?.trim()) {
    throw new CompaniesApiError(
      "The API is not configured. Set NEXT_PUBLIC_API_BASE_URL in frontend/.env.local.",
    );
  }

  let response: Response;
  try {
    response = await fetch("/api/v1/companies", {
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    });
  } catch {
    throw new CompaniesApiError(
      "Could not reach the AEGIS API. Check the backend connection and API URL.",
    );
  }

  if (!response.ok) {
    if (response.status === 401) {
      throw new CompaniesApiError("Your session has expired. Please sign in again.", 401);
    }
    if (response.status === 403) {
      throw new CompaniesApiError("You do not have permission to view companies.", 403);
    }
    if (response.status >= 500) {
      throw new CompaniesApiError("Company data is temporarily unavailable. Please try again later.", response.status);
    }
    throw new CompaniesApiError("Could not load companies. Please try again.", response.status);
  }

  let result: unknown;
  try {
    result = await response.json();
  } catch {
    throw new CompaniesApiError("The API returned an unreadable company response.");
  }

  if (!Array.isArray(result) || !result.every(isCompany)) {
    throw new CompaniesApiError("The API returned company data in an unexpected format.");
  }

  return result;
}
