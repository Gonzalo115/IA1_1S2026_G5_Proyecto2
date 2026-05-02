import { apiFetch } from "./client";
import type { DetectionResult } from "../types";

export async function detectarMano(blob: Blob): Promise<DetectionResult> {
  const formData = new FormData();
  formData.append("imagen", blob, "frame.jpg");
  const res = await apiFetch("/analizar", {
    method: "POST",
    body: formData,
  });
  return res.json();
}
