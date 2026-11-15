export type ModelPrediction = {
  prediction_id: number;
  security_id: number;
  ticker: string;
  exchange: string;
  prediction_type: "ANOMALY" | "VOLATILITY";
  prediction_date: string;
  target_date: string | null;
  predicted_value: number;
  signal: string | null;
  model_name: string;
  model_version: string;
  metrics: Record<string, unknown>;
  features: Record<string, unknown>;
  created_at: string;
};

export class ModelPredictionsApiError extends Error {
  constructor(message: string, readonly status?: number) {
    super(message);
    this.name = "ModelPredictionsApiError";
  }
}

function normalizePrediction(value: unknown): ModelPrediction | null {
  if (typeof value !== "object" || value === null) return null;
  const row = value as Record<string, unknown>;
  const numeric = typeof row.predicted_value === "number"
    ? row.predicted_value
    : typeof row.predicted_value === "string" ? Number(row.predicted_value) : NaN;
  if (
    typeof row.prediction_id !== "number" ||
    typeof row.security_id !== "number" ||
    typeof row.ticker !== "string" ||
    typeof row.exchange !== "string" ||
    (row.prediction_type !== "ANOMALY" && row.prediction_type !== "VOLATILITY") ||
    typeof row.prediction_date !== "string" ||
    !Number.isFinite(numeric) ||
    (row.target_date !== null && typeof row.target_date !== "string") ||
    (row.signal !== null && typeof row.signal !== "string") ||
    typeof row.model_name !== "string" ||
    typeof row.model_version !== "string" ||
    typeof row.created_at !== "string"
  ) return null;

  return {
    prediction_id: row.prediction_id,
    security_id: row.security_id,
    ticker: row.ticker,
    exchange: row.exchange,
    prediction_type: row.prediction_type,
    prediction_date: row.prediction_date,
    target_date: row.target_date as string | null,
    predicted_value: numeric,
    signal: row.signal as string | null,
    model_name: row.model_name,
    model_version: row.model_version,
    metrics: typeof row.metrics === "object" && row.metrics !== null
      ? row.metrics as Record<string, unknown> : {},
    features: typeof row.features === "object" && row.features !== null
      ? row.features as Record<string, unknown> : {},
    created_at: row.created_at,
  };
}

export async function getModelPredictions(
  token: string,
  companyId: number,
): Promise<ModelPrediction[]> {
  if (!process.env.NEXT_PUBLIC_API_BASE_URL?.trim()) {
    throw new ModelPredictionsApiError("The API is not configured.");
  }
  let response: Response;
  try {
    response = await fetch(
      `/api/v1/companies/${encodeURIComponent(companyId)}/predictions?limit=50`,
      { headers: { Accept: "application/json", Authorization: `Bearer ${token}` } },
    );
  } catch {
    throw new ModelPredictionsApiError("Could not reach the AEGIS API.");
  }
  if (!response.ok) {
    throw new ModelPredictionsApiError(
      response.status === 401 ? "Your session has expired." :
      response.status === 404 ? "The selected company was not found." :
      "Could not load model predictions.",
      response.status,
    );
  }
  const value: unknown = await response.json();
  if (!Array.isArray(value)) throw new ModelPredictionsApiError("Unexpected predictions response.");
  const rows = value.map(normalizePrediction);
  if (rows.some((row) => row === null)) {
    throw new ModelPredictionsApiError("The API returned malformed model predictions.");
  }
  return rows as ModelPrediction[];
}
