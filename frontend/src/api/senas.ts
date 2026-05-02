import { apiFetch } from "./client";
import type { ImagenInfo } from "../types";

export async function getCategorias(): Promise<string[]> {
  const res = await apiFetch("/api/senas/");
  const data = await res.json();
  return data.categorias || [];
}

export async function crearCategoria(nombre: string): Promise<{ exito: boolean; mensaje: string }> {
  const res = await apiFetch("/api/senas/", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ nombre }),
  });
  return res.json();
}

export async function eliminarCategoria(nombre: string): Promise<{ exito: boolean; mensaje: string }> {
  const res = await apiFetch(`/api/senas/${encodeURIComponent(nombre)}`, {
    method: "DELETE",
  });
  return res.json();
}

export async function getImagenes(categoria: string): Promise<{ imagenes: ImagenInfo[] }> {
  const res = await apiFetch(`/api/senas/${encodeURIComponent(categoria)}/imagenes`);
  return res.json();
}

export async function subirImagen(
  categoria: string,
  archivo: File
): Promise<{ exito: boolean; mensaje: string }> {
  const formData = new FormData();
  formData.append("imagen", archivo);
  const res = await apiFetch(
    `/api/senas/${encodeURIComponent(categoria)}/imagenes`,
    { method: "POST", body: formData }
  );
  return res.json();
}

export async function eliminarImagen(
  categoria: string,
  nombre: string
): Promise<{ exito: boolean; mensaje: string }> {
  const res = await apiFetch(
    `/api/senas/${encodeURIComponent(categoria)}/imagenes/${encodeURIComponent(nombre)}`,
    { method: "DELETE" }
  );
  return res.json();
}
