import { apiFetch } from "./client";
import type { AdminConfig, HistoryItem } from "../types";

export async function getConfig(): Promise<AdminConfig> {
  const res = await apiFetch("/api/admin/config");
  return res.json();
}

export async function updateConfig(data: Partial<AdminConfig>): Promise<void> {
  await apiFetch("/api/admin/config", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(data),
  });
}

export async function getHistory(): Promise<HistoryItem[]> {
  const res = await apiFetch("/api/admin/history");
  const data = await res.json();
  return data.message_history || [];
}

export async function sendTelegramMessage(
  prediction: string,
  confidence: number | null
): Promise<{ sent: boolean; reason?: string }> {
  const res = await apiFetch("/api/admin/telegram/test", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prediction, confidence }),
  });
  return res.json();
}

export async function getModeloClases(): Promise<{ clases: string[]; entrenado: boolean }> {
  const res = await apiFetch("/api/admin/modelo/clases");
  return res.json();
}

export async function trainModel(): Promise<any> {
  const formData = new FormData();
  formData.append("ruta_dataset", "data");
  const res = await apiFetch("/api/entreanar/", {
    method: "POST",
    body: formData,
  });
  return res.json();
}
