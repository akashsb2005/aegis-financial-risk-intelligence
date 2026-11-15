"use client";

import { useEffect, useState } from "react";
import { getSessionToken } from "@/lib/auth";
import { getModelPredictions, ModelPredictionsApiError } from "@/lib/model-predictions";
import type { ModelPrediction } from "@/lib/model-predictions";

export default function ModelPredictionsSection({ companyId }: { companyId: number }) {
  const [rows, setRows] = useState<ModelPrediction[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let current = true;
    async function load() {
      const token = getSessionToken();
      if (!token) {
        if (current) { setError("Please sign in again."); setLoading(false); }
        return;
      }
      setLoading(true);
      setError("");
      try {
        const result = await getModelPredictions(token, companyId);
        if (current) setRows(result);
      } catch (reason) {
        if (!current) return;
        if (reason instanceof ModelPredictionsApiError && reason.status === 401) {
          setError("Your session has expired. Please sign in again.");
        } else {
          setError(reason instanceof Error ? reason.message : "Could not load predictions.");
        }
      } finally {
        if (current) setLoading(false);
      }
    }
    void load();
    return () => { current = false; };
  }, [companyId]);

  return (
    <section aria-labelledby="model-predictions-heading" className="mb-8">
      <div className="mb-4">
        <h2 id="model-predictions-heading" className="text-xl font-semibold tracking-tight text-[#14213d]">
          Machine-learning signals
        </h2>
        <p className="mt-1 text-sm text-slate-500">
          Persisted anomaly and forward-volatility outputs. These are research signals, not investment advice.
        </p>
      </div>
      {loading ? (
        <div role="status" className="rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-500">
          Loading model predictions...
        </div>
      ) : error ? (
        <div role="alert" className="rounded-xl border border-red-200 bg-red-50 p-5 text-sm text-red-800">
          {error}
        </div>
      ) : rows.length === 0 ? (
        <div className="rounded-xl border border-dashed border-slate-300 bg-white/70 px-5 py-8 text-center">
          <p className="text-sm font-medium text-slate-700">No model predictions available yet.</p>
          <p className="mt-1 text-xs leading-5 text-slate-500">
            Ingest sufficient historical market observations and run the ML training pipeline to populate this section.
          </p>
        </div>
      ) : (
        <div className="overflow-x-auto rounded-xl border border-slate-200 bg-white shadow-sm">
          <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
              <tr>
                <th className="px-4 py-3">Security</th>
                <th className="px-4 py-3">Signal</th>
                <th className="px-4 py-3">Value</th>
                <th className="px-4 py-3">Date</th>
                <th className="px-4 py-3">Model</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {rows.map((row) => (
                <tr key={row.prediction_id}>
                  <td className="whitespace-nowrap px-4 py-3 font-medium text-slate-800">
                    {row.ticker} <span className="text-xs text-slate-400">{row.exchange}</span>
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-slate-700">
                    {row.prediction_type === "ANOMALY" ? row.signal ?? "Anomaly score" : "5-session volatility"}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 tabular-nums text-slate-700">
                    {row.predicted_value.toFixed(6)}
                  </td>
                  <td className="whitespace-nowrap px-4 py-3 text-slate-600">{row.prediction_date}</td>
                  <td className="whitespace-nowrap px-4 py-3 text-xs text-slate-500">
                    {row.model_name} v{row.model_version}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}
