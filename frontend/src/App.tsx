import { useState, useRef, useEffect, useCallback } from "react";
import "./App.css";

const API_BASE = "http://localhost:8000";

// Conexiones de MediaPipe entre los 21 landmarks de la mano
const HAND_CONNECTIONS: [number, number][] = [
  [0, 1], [1, 2], [2, 3], [3, 4],
  [0, 5], [5, 6], [6, 7], [7, 8],
  [5, 9], [9, 10], [10, 11], [11, 12],
  [9, 13], [13, 14], [14, 15], [15, 16],
  [13, 17], [17, 18], [18, 19], [19, 20],
  [0, 17],
];

interface Landmark {
  x: number;
  y: number;
}

interface DetectionResult {
  exito: boolean;
  prediccion: string | null;
  confianza: number | null;
  confianzas_por_clase: Record<string, number>;
  mensaje: string;
  manos_detectadas: number;
  landmarks: Landmark[] | null;
}

interface AdminConfig {
  telegram_enabled: boolean;
  telegram_message_format: string;
  confidence_threshold: number;
  available_signs: string[];
  message_history: HistoryItem[];
}

interface HistoryItem {
  prediction: string;
  confidence: number | null;
  message: string;
  sent: boolean;
  created_at: string;
}

interface TrainingResult {
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

// ---------- Shared component: confidence bar ----------
function ConfidenceBar({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const color = pct >= 80 ? "#22c55e" : pct >= 50 ? "#f59e0b" : "#ef4444";
  return (
    <div className="conf-bar-wrap">
      <div className="conf-bar-bg">
        <div className="conf-bar-fill" style={{ width: `${pct}%`, backgroundColor: color }} />
      </div>
      <span className="conf-bar-label" style={{ color }}>{pct}%</span>
    </div>
  );
}

// ============================================================
// USER MODULE
// ============================================================
function UserModule({ config }: { config: AdminConfig | null }) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const captureCanvasRef = useRef<HTMLCanvasElement>(null);
  const overlayCanvasRef = useRef<HTMLCanvasElement>(null);
  const analyzingRef = useRef(false);

  const [cameraActive, setCameraActive] = useState(false);
  const [detection, setDetection] = useState<DetectionResult | null>(null);
  const [telegramSending, setTelegramSending] = useState(false);
  const [telegramStatus, setTelegramStatus] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);

  const threshold = config?.confidence_threshold ?? 0.5;

  const loadHistory = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/admin/history`);
      const data = await res.json();
      setHistory(data.message_history || []);
    } catch { /* ignore */ }
  }, []);

  useEffect(() => { loadHistory(); }, [loadHistory]);

  const clearOverlay = useCallback(() => {
    const canvas = overlayCanvasRef.current;
    if (!canvas) return;
    canvas.getContext("2d")?.clearRect(0, 0, canvas.width, canvas.height);
  }, []);

  const drawLandmarks = useCallback((landmarks: Landmark[]) => {
    const canvas = overlayCanvasRef.current;
    const video = videoRef.current;
    if (!canvas || !video) return;

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const w = canvas.width;
    const h = canvas.height;

    ctx.strokeStyle = "rgba(0, 217, 255, 0.75)";
    ctx.lineWidth = 2;
    for (const [a, b] of HAND_CONNECTIONS) {
      ctx.beginPath();
      ctx.moveTo(landmarks[a].x * w, landmarks[a].y * h);
      ctx.lineTo(landmarks[b].x * w, landmarks[b].y * h);
      ctx.stroke();
    }

    const fingerTips = new Set([4, 8, 12, 16, 20]);
    for (let i = 0; i < landmarks.length; i++) {
      const lm = landmarks[i];
      ctx.beginPath();
      ctx.arc(lm.x * w, lm.y * h, fingerTips.has(i) ? 6 : 4, 0, Math.PI * 2);
      ctx.fillStyle = fingerTips.has(i) ? "#ff6b35" : "#00d9ff";
      ctx.fill();
    }
  }, []);

  const startCamera = useCallback(async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { width: { ideal: 640 }, height: { ideal: 480 } },
      });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setCameraActive(true);
      }
    } catch {
      alert("No se pudo acceder a la camara. Verifica los permisos del navegador.");
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (videoRef.current?.srcObject) {
      (videoRef.current.srcObject as MediaStream).getTracks().forEach(t => t.stop());
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
    setDetection(null);
    clearOverlay();
  }, [clearOverlay]);

  // Detection loop: captures a frame every 500ms and sends to backend
  useEffect(() => {
    if (!cameraActive) return;

    const interval = setInterval(async () => {
      const video = videoRef.current;
      const canvas = captureCanvasRef.current;
      if (!video || !canvas || analyzingRef.current) return;

      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.drawImage(video, 0, 0);

      canvas.toBlob(async (blob) => {
        if (!blob) return;
        analyzingRef.current = true;
        const formData = new FormData();
        formData.append("imagen", blob, "frame.jpg");
        try {
          const res = await fetch(`${API_BASE}/analizar`, {
            method: "POST",
            body: formData,
          });
          if (res.ok) {
            const data: DetectionResult = await res.json();
            setDetection(data);
            if (data.exito && data.landmarks) {
              drawLandmarks(data.landmarks);
            } else {
              clearOverlay();
            }
          }
        } catch { /* network error */ } finally {
          analyzingRef.current = false;
        }
      }, "image/jpeg", 0.8);
    }, 500);

    return () => clearInterval(interval);
  }, [cameraActive, drawLandmarks, clearOverlay]);

  const sendTelegram = async () => {
    if (!detection?.prediccion) return;
    setTelegramSending(true);
    setTelegramStatus(null);
    try {
      const res = await fetch(`${API_BASE}/api/admin/telegram/test`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prediction: detection.prediccion,
          confidence: detection.confianza,
        }),
      });
      const data = await res.json();
      setTelegramStatus(data.sent ? "Mensaje enviado correctamente" : `No enviado: ${data.reason ?? ""}`);
      loadHistory();
    } catch {
      setTelegramStatus("Error de conexion con el servidor");
    } finally {
      setTelegramSending(false);
    }
  };

  const aboveThreshold =
    detection?.exito === true &&
    detection.confianza !== null &&
    detection.confianza >= threshold;

  return (
    <div className="user-module">
      {/* ---- Camera panel ---- */}
      <div className="panel camera-panel">
        <div className="panel-header">
          <h2>Camara en tiempo real</h2>
          <button
            className={cameraActive ? "btn btn-danger" : "btn btn-primary"}
            onClick={cameraActive ? stopCamera : startCamera}
          >
            {cameraActive ? "Detener camara" : "Iniciar camara"}
          </button>
        </div>

        <div className="camera-wrapper">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="camera-video"
            onLoadedMetadata={() => {
              if (captureCanvasRef.current && videoRef.current) {
                captureCanvasRef.current.width = videoRef.current.videoWidth;
                captureCanvasRef.current.height = videoRef.current.videoHeight;
              }
            }}
          />
          <canvas ref={overlayCanvasRef} className="camera-overlay" />
          {!cameraActive && (
            <div className="camera-placeholder">
              <span className="camera-icon">📷</span>
              <p>Camara inactiva</p>
            </div>
          )}
          {analyzingRef.current && <div className="analyzing-badge">Analizando...</div>}
        </div>
        <canvas ref={captureCanvasRef} style={{ display: "none" }} />

        <p className="camera-note">
          Los puntos azules y naranjas son los 21 landmarks extraidos por MediaPipe.
          Cada frame se envia al backend cada 500ms para prediccion.
        </p>
      </div>

      {/* ---- Info column ---- */}
      <div className="info-column">
        {/* Prediction */}
        <div className="panel">
          <div className="panel-header">
            <h2>Prediccion actual</h2>
            {detection?.exito && (
              <span className="manos-badge">
                {detection.manos_detectadas} mano(s)
              </span>
            )}
          </div>

          {detection?.exito ? (
            <div className="prediction-display">
              <div className={`prediction-word ${aboveThreshold ? "above-threshold" : "below-threshold"}`}>
                {detection.prediccion}
              </div>
              <ConfidenceBar value={detection.confianza!} />
              {!aboveThreshold && (
                <p className="threshold-warning">
                  Confianza bajo el umbral configurado ({Math.round(threshold * 100)}%)
                </p>
              )}
              <button
                className="btn btn-telegram"
                disabled={!aboveThreshold || telegramSending || !config?.telegram_enabled}
                onClick={sendTelegram}
              >
                {telegramSending ? "Enviando..." : "Enviar a Telegram"}
              </button>
              {!config?.telegram_enabled && (
                <p className="disabled-note">Bot de Telegram desactivado en administracion</p>
              )}
              {telegramStatus && (
                <p className={`telegram-status ${telegramStatus.startsWith("Mensaje") ? "success" : "error"}`}>
                  {telegramStatus}
                </p>
              )}
            </div>
          ) : (
            <div className="no-detection">
              <p>{detection?.mensaje ?? "Muestra una mano a la camara para detectar una sena."}</p>
            </div>
          )}
        </div>

        {/* Available signs */}
        <div className="panel">
          <div className="panel-header">
            <h2>Senas disponibles</h2>
          </div>
          <div className="signs-grid">
            {(config?.available_signs ?? []).map(sign => (
              <span
                key={sign}
                className={`sign-badge ${detection?.prediccion === sign && aboveThreshold ? "sign-active" : ""}`}
              >
                {sign}
              </span>
            ))}
            {(config?.available_signs ?? []).length === 0 && (
              <p className="empty-note">Sin senas configuradas. Configura en el modulo administrador.</p>
            )}
          </div>
        </div>

        {/* Message history */}
        <div className="panel">
          <div className="panel-header">
            <h2>Historial de mensajes</h2>
            <button className="btn-icon" onClick={loadHistory} title="Actualizar">
              ↻
            </button>
          </div>
          <div className="history-list">
            {history.length === 0 ? (
              <p className="empty-note">Sin mensajes enviados aun.</p>
            ) : (
              [...history].reverse().slice(0, 10).map((item, i) => (
                <div key={i} className="history-item">
                  <div className="history-item-top">
                    <span className="history-sign">{item.prediction}</span>
                    <span className={`history-status ${item.sent ? "sent" : "failed"}`}>
                      {item.sent ? "Enviado" : "Fallido"}
                    </span>
                  </div>
                  <p className="history-message">{item.message}</p>
                  <p className="history-date">
                    {new Date(item.created_at).toLocaleString("es-GT")}
                  </p>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}

// ============================================================
// ADMIN MODULE
// ============================================================
function AdminModule({ config, onConfigChange }: {
  config: AdminConfig | null;
  onConfigChange: () => void;
}) {
  const [threshold, setThreshold] = useState(config?.confidence_threshold ?? 0.5);
  const [format, setFormat] = useState(config?.telegram_message_format ?? "");
  const [telegramEnabled, setTelegramEnabled] = useState(config?.telegram_enabled ?? true);
  const [signs, setSigns] = useState<string[]>(config?.available_signs ?? []);
  const [newSign, setNewSign] = useState("");
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState<string | null>(null);
  const [training, setTraining] = useState(false);
  const [trainingResult, setTrainingResult] = useState<TrainingResult | null>(null);

  useEffect(() => {
    if (config) {
      setThreshold(config.confidence_threshold);
      setFormat(config.telegram_message_format);
      setTelegramEnabled(config.telegram_enabled);
      setSigns(config.available_signs ?? []);
    }
  }, [config]);

  const saveConfig = async () => {
    setSaving(true);
    setSaveMsg(null);
    try {
      const res = await fetch(`${API_BASE}/api/admin/config`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          confidence_threshold: threshold,
          telegram_message_format: format,
          telegram_enabled: telegramEnabled,
          available_signs: signs,
        }),
      });
      if (res.ok) {
        setSaveMsg("Configuracion guardada correctamente");
        onConfigChange();
      } else {
        setSaveMsg("Error al guardar la configuracion");
      }
    } catch {
      setSaveMsg("Error de conexion con el servidor");
    } finally {
      setSaving(false);
    }
  };

  const addSign = () => {
    const s = newSign.trim().toLowerCase();
    if (s && !signs.includes(s)) {
      setSigns([...signs, s]);
      setNewSign("");
    }
  };

  const removeSign = (sign: string) => {
    setSigns(signs.filter(s => s !== sign));
  };

  const trainModel = async () => {
    setTraining(true);
    setTrainingResult(null);
    try {
      const formData = new FormData();
      formData.append("ruta_dataset", "data");
      const res = await fetch(`${API_BASE}/api/entreanar/`, {
        method: "POST",
        body: formData,
      });
      const data: TrainingResult = await res.json();
      setTrainingResult(data);
    } catch {
      setTrainingResult({ exito: false, mensaje: "Error de conexion al iniciar entrenamiento" });
    } finally {
      setTraining(false);
    }
  };

  return (
    <div className="admin-module">
      <div className="admin-grid">
        {/* Confidence threshold */}
        <div className="panel">
          <div className="panel-header">
            <h2>Umbral de confianza</h2>
          </div>
          <div className="admin-field">
            <label>
              Valor actual: <strong className="accent-text">{Math.round(threshold * 100)}%</strong>
            </label>
            <input
              type="range"
              min={0} max={1} step={0.05}
              value={threshold}
              onChange={e => setThreshold(parseFloat(e.target.value))}
              className="slider"
            />
            <div className="slider-marks">
              <span>0%</span><span>50%</span><span>100%</span>
            </div>
            <p className="field-note">
              Predicciones con confianza menor a este valor seran marcadas como no validas
              y el boton de Telegram se desactivara.
            </p>
          </div>
        </div>

        {/* Telegram config */}
        <div className="panel">
          <div className="panel-header">
            <h2>Bot de Telegram</h2>
            <button
              className={`toggle-btn ${telegramEnabled ? "active" : ""}`}
              onClick={() => setTelegramEnabled(!telegramEnabled)}
            >
              {telegramEnabled ? "Activo" : "Inactivo"}
            </button>
          </div>
          <div className="admin-field">
            <label>Formato del mensaje</label>
            <input
              type="text"
              value={format}
              onChange={e => setFormat(e.target.value)}
              className="text-input"
              placeholder="HandTalk AI detecto: {prediction} | confianza: {confidence}"
            />
            <p className="field-note">
              Usa <code>{"{prediction}"}</code> y <code>{"{confidence}"}</code> como variables dinamicas.
            </p>
          </div>
        </div>
      </div>

      {/* Signs CRUD */}
      <div className="panel">
        <div className="panel-header">
          <h2>Gestion de senas disponibles</h2>
          <span className="badge">{signs.length} senas</span>
        </div>
        <div className="signs-crud">
          <div className="signs-add-row">
            <input
              type="text"
              value={newSign}
              onChange={e => setNewSign(e.target.value)}
              onKeyDown={e => e.key === "Enter" && addSign()}
              className="text-input"
              placeholder="Nombre de la nueva sena (ej: gracias)"
            />
            <button className="btn btn-primary" onClick={addSign}>Agregar</button>
          </div>
          <div className="signs-list-crud">
            {signs.length === 0 ? (
              <p className="empty-note">Sin senas configuradas.</p>
            ) : (
              signs.map(sign => (
                <div key={sign} className="sign-crud-item">
                  <span>{sign}</span>
                  <button className="btn-remove" onClick={() => removeSign(sign)}>×</button>
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Save */}
      <div className="save-row">
        <button className="btn btn-primary btn-large" onClick={saveConfig} disabled={saving}>
          {saving ? "Guardando..." : "Guardar configuracion"}
        </button>
        {saveMsg && (
          <span className={`save-msg ${saveMsg.includes("Error") ? "error" : "success"}`}>
            {saveMsg}
          </span>
        )}
      </div>

      {/* Training */}
      <div className="panel">
        <div className="panel-header">
          <h2>Entrenamiento del modelo</h2>
          <button
            className="btn btn-primary"
            onClick={trainModel}
            disabled={training}
          >
            {training ? "Entrenando..." : "Iniciar entrenamiento"}
          </button>
        </div>

        {training && (
          <div className="training-progress">
            <div className="spinner" />
            <p>Procesando imagenes del dataset. Esto puede tardar varios minutos...</p>
          </div>
        )}

        {trainingResult && (
          <div className={`training-result ${trainingResult.exito ? "success-card" : "error-card"}`}>
            {trainingResult.exito ? (
              <>
                <div className="metrics-grid">
                  <div className="metric-card">
                    <span className="metric-value">
                      {Math.round((trainingResult.accuracy ?? 0) * 100)}%
                    </span>
                    <span className="metric-label">Accuracy</span>
                  </div>
                  <div className="metric-card">
                    <span className="metric-value">{trainingResult.total_muestras}</span>
                    <span className="metric-label">Total muestras</span>
                  </div>
                  <div className="metric-card">
                    <span className="metric-value">{trainingResult.muestras_entrenamiento}</span>
                    <span className="metric-label">Entrenamiento (70%)</span>
                  </div>
                  <div className="metric-card">
                    <span className="metric-value">{trainingResult.muestras_prueba}</span>
                    <span className="metric-label">Prueba (30%)</span>
                  </div>
                </div>

                <div className="eval-section">
                  <h3>Clases entrenadas</h3>
                  <div className="signs-grid" style={{ marginTop: "8px" }}>
                    {trainingResult.etiquetas?.map(label => (
                      <span key={label} className="sign-badge">{label}</span>
                    ))}
                  </div>
                </div>

                {trainingResult.reporte && (
                  <div className="eval-section">
                    <h3>Evaluacion por clase (precision, recall, F1)</h3>
                    <table className="eval-table">
                      <thead>
                        <tr>
                          <th>Clase</th>
                          <th>Precision</th>
                          <th>Recall</th>
                          <th>F1-score</th>
                          <th>Muestras</th>
                        </tr>
                      </thead>
                      <tbody>
                        {Object.entries(trainingResult.reporte)
                          .filter(([key]) => !["accuracy", "macro avg", "weighted avg"].includes(key))
                          .map(([cls, metrics]: [string, any]) => (
                            <tr key={cls}>
                              <td><strong>{cls}</strong></td>
                              <td>{(metrics.precision * 100).toFixed(1)}%</td>
                              <td>{(metrics.recall * 100).toFixed(1)}%</td>
                              <td>{(metrics["f1-score"] * 100).toFixed(1)}%</td>
                              <td>{metrics.support}</td>
                            </tr>
                          ))}
                      </tbody>
                    </table>

                    {trainingResult.reporte["weighted avg"] && (
                      <div className="weighted-avg">
                        <span>Promedio ponderado (weighted avg):</span>
                        <span>
                          P: {(trainingResult.reporte["weighted avg"].precision * 100).toFixed(1)}% |
                          R: {(trainingResult.reporte["weighted avg"].recall * 100).toFixed(1)}% |
                          F1: {(trainingResult.reporte["weighted avg"]["f1-score"] * 100).toFixed(1)}%
                        </span>
                      </div>
                    )}
                  </div>
                )}
              </>
            ) : (
              <p className="error-text">{trainingResult.mensaje}</p>
            )}
          </div>
        )}
      </div>
    </div>
  );
}

// ============================================================
// ROOT
// ============================================================
export default function App() {
  const [activeTab, setActiveTab] = useState<"usuario" | "admin">("usuario");
  const [config, setConfig] = useState<AdminConfig | null>(null);

  const loadConfig = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/api/admin/config`);
      if (res.ok) setConfig(await res.json());
    } catch { /* backend not yet running */ }
  }, []);

  useEffect(() => { loadConfig(); }, [loadConfig]);

  return (
    <div className="app-shell">
      <nav className="navbar">
        <div className="navbar-brand">
          <span className="brand-name">HandTalk AI</span>
        </div>
        <div className="navbar-tabs">
          <button
            className={`tab-btn ${activeTab === "usuario" ? "active" : ""}`}
            onClick={() => setActiveTab("usuario")}
          >
            Modulo Usuario
          </button>
          <button
            className={`tab-btn ${activeTab === "admin" ? "active" : ""}`}
            onClick={() => setActiveTab("admin")}
          >
            Modulo Administrador
          </button>
        </div>
      </nav>

      <main className="main-content">
        {activeTab === "usuario" ? (
          <UserModule config={config} />
        ) : (
          <AdminModule config={config} onConfigChange={loadConfig} />
        )}
      </main>
    </div>
  );
}

