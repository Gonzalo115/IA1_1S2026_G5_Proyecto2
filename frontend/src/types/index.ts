export interface Landmark {
  x: number;
  y: number;
}

export interface DetectionResult {
  exito: boolean;
  prediccion: string | null;
  confianza: number | null;
  confianzas_por_clase: Record<string, number>;
  mensaje: string;
  manos_detectadas: number;
  landmarks: Landmark[] | null;
}

export interface AdminConfig {
  telegram_enabled: boolean;
  telegram_message_format: string;
  confidence_threshold: number;
  available_signs: string[];
  message_history: HistoryItem[];
}

export interface HistoryItem {
  prediction: string;
  confidence: number | null;
  message: string;
  sent: boolean;
  created_at: string;
}

export interface TrainingResult {
  exito: boolean;
  accuracy?: number;
  total_muestras?: number;
  muestras_entrenamiento?: number;
  muestras_prueba?: number;
  etiquetas?: string[];
  conteo_clases?: Record<string, number>;
  reporte?: Record<string, any>;
  mensaje: string;
}

export interface ImagenInfo {
  nombre: string;
  key: string;
  url: string;
  tamanio: number;
  ultima_modificacion: string;
}
