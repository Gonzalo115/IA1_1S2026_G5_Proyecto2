import { useRef, useCallback, useEffect, useState } from "react";
import "./UserModule.css";
import ConfidenceBar from "../../components/ConfidenceBar/ConfidenceBar";
import { detectarMano } from "../../api/detection";
import { sendTelegramMessage, getHistory, getModeloClases } from "../../api/admin";
import type { AdminConfig, DetectionResult, HistoryItem, Landmark } from "../../types";

const HAND_CONNECTIONS: [number, number][] = [
  [0, 1], [1, 2], [2, 3], [3, 4],
  [0, 5], [5, 6], [6, 7], [7, 8],
  [5, 9], [9, 10], [10, 11], [11, 12],
  [9, 13], [13, 14], [14, 15], [15, 16],
  [13, 17], [17, 18], [18, 19], [19, 20],
  [0, 17],
];

const FINGER_TIPS = new Set([4, 8, 12, 16, 20]);

interface Props {
  config: AdminConfig | null;
}

export default function UserModule({ config }: Props) {
  const videoRef = useRef<HTMLVideoElement>(null);
  const captureCanvasRef = useRef<HTMLCanvasElement>(null);
  const overlayCanvasRef = useRef<HTMLCanvasElement>(null);
  const analyzingRef = useRef(false);

  const [cameraActive, setCameraActive] = useState(false);
  const [detection, setDetection] = useState<DetectionResult | null>(null);
  const [telegramSending, setTelegramSending] = useState(false);
  const [telegramStatus, setTelegramStatus] = useState<string | null>(null);
  const [history, setHistory] = useState<HistoryItem[]>([]);
  const [clasesModelo, setClasesModelo] = useState<string[]>([]);
  const [modeloEntrenado, setModeloEntrenado] = useState(false);

  const threshold = config?.confidence_threshold ?? 0.5;

  useEffect(() => {
    getModeloClases()
      .then(({ clases, entrenado }) => {
        setClasesModelo(clases);
        setModeloEntrenado(entrenado);
      })
      .catch(() => {
        setClasesModelo([]);
        setModeloEntrenado(false);
      });
  }, []);

  const loadHistory = useCallback(async () => {
    try {
      const data = await getHistory();
      setHistory(data);
    } catch {
      /* ignore */
    }
  }, []);

  useEffect(() => {
    loadHistory();
  }, [loadHistory]);

  const clearOverlay = useCallback(() => {
    const canvas = overlayCanvasRef.current;
    if (canvas) {
      canvas.getContext("2d")?.clearRect(0, 0, canvas.width, canvas.height);
    }
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

    ctx.strokeStyle = "rgba(37, 150, 190, 0.8)";
    ctx.lineWidth = 2;
    for (const [a, b] of HAND_CONNECTIONS) {
      ctx.beginPath();
      ctx.moveTo(landmarks[a].x * w, landmarks[a].y * h);
      ctx.lineTo(landmarks[b].x * w, landmarks[b].y * h);
      ctx.stroke();
    }

    for (let i = 0; i < landmarks.length; i++) {
      const lm = landmarks[i];
      const isTip = FINGER_TIPS.has(i);
      ctx.beginPath();
      ctx.arc(lm.x * w, lm.y * h, isTip ? 6 : 4, 0, Math.PI * 2);
      ctx.fillStyle = isTip ? "#f48fb1" : "#2596be";
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
      alert("No se pudo acceder a la cámara. Verifica los permisos del navegador.");
    }
  }, []);

  const stopCamera = useCallback(() => {
    if (videoRef.current?.srcObject) {
      (videoRef.current.srcObject as MediaStream).getTracks().forEach((t) => t.stop());
      videoRef.current.srcObject = null;
    }
    setCameraActive(false);
    setDetection(null);
    clearOverlay();
  }, [clearOverlay]);

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
        try {
          const data = await detectarMano(blob);
          setDetection(data);
          if (data.exito && data.landmarks) {
            drawLandmarks(data.landmarks);
          } else {
            clearOverlay();
          }
        } catch {
          /* network error */
        } finally {
          analyzingRef.current = false;
        }
      }, "image/jpeg", 0.8);
    }, 500);

    return () => clearInterval(interval);
  }, [cameraActive, drawLandmarks, clearOverlay]);

  const handleSendTelegram = async () => {
    if (!detection?.prediccion) return;
    setTelegramSending(true);
    setTelegramStatus(null);
    try {
      const data = await sendTelegramMessage(detection.prediccion, detection.confianza);
      if (data.sent) {
        setTelegramStatus("Mensaje enviado correctamente");
      } else {
        setTelegramStatus(`No enviado: ${data.reason ?? "razón desconocida"}`);
      }
      loadHistory();
    } catch {
      setTelegramStatus("Error de conexión con el servidor");
    } finally {
      setTelegramSending(false);
    }
  };

  const aboveThreshold =
    detection?.exito === true &&
    detection.confianza !== null &&
    detection.confianza >= threshold;

  const topClases = detection?.confianzas_por_clase
    ? Object.entries(detection.confianzas_por_clase)
        .sort(([, a], [, b]) => b - a)
        .slice(0, 5)
    : [];

  return (
    <div className="user-module">
      <div className="module-header">
        <h1>Módulo de Usuario</h1>
        <p>Detección de señas en tiempo real mediante cámara web</p>
      </div>

      <div className="user-layout">
        {/* Camera panel */}
        <div className="camera-section">
          <div className="card">
            <div className="card-header">
              <h2>Cámara en tiempo real</h2>
              <button
                className={cameraActive ? "btn btn-danger" : "btn btn-primary"}
                onClick={cameraActive ? stopCamera : startCamera}
              >
                {cameraActive ? "Detener cámara" : "Iniciar cámara"}
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
                  <div className="camera-icon-shape" />
                  <p>Presiona "Iniciar cámara" para comenzar</p>
                </div>
              )}
            </div>

            <canvas ref={captureCanvasRef} style={{ display: "none" }} />

            <p className="camera-note">
              Los puntos muestran los 21 landmarks de MediaPipe extraídos de la mano.
              Se envía un frame al backend cada 500 ms para la predicción.
            </p>
          </div>
        </div>

        {/* Right column */}
        <div className="info-column">
          {/* Prediction result */}
          <div className="card">
            <div className="card-header">
              <h2>Predicción actual</h2>
              {detection?.exito && (
                <span className="badge badge-info">
                  {detection.manos_detectadas} mano(s)
                </span>
              )}
            </div>

            {detection?.exito ? (
              <div className="prediction-display">
                <div className={`prediction-word ${aboveThreshold ? "word-valid" : "word-invalid"}`}>
                  {detection.prediccion}
                </div>
                <ConfidenceBar value={detection.confianza!} />
                {!aboveThreshold && (
                  <p className="threshold-warning">
                    Confianza bajo el umbral ({Math.round(threshold * 100)}%)
                  </p>
                )}
                <button
                  className="btn btn-primary"
                  disabled={!aboveThreshold || telegramSending || !config?.telegram_enabled}
                  onClick={handleSendTelegram}
                >
                  {telegramSending ? "Enviando..." : "Enviar a Telegram"}
                </button>
                {!config?.telegram_enabled && (
                  <p className="disabled-note">Bot de Telegram desactivado por el administrador</p>
                )}
                {telegramStatus && (
                  <p
                    className={`status-msg ${
                      telegramStatus.startsWith("Mensaje") ? "status-success" : "status-error"
                    }`}
                  >
                    {telegramStatus}
                  </p>
                )}
              </div>
            ) : (
              <div className="empty-state">
                <p>
                  {detection?.mensaje ?? "Muestra una mano a la cámara para detectar una seña."}
                </p>
              </div>
            )}
          </div>

          {/* Detección y características */}
          <div className="card">
            <div className="card-header">
              <h2>Detección y características</h2>
              {detection?.exito ? (
                <span className="badge badge-success">Mano detectada</span>
              ) : (
                <span className="badge badge-neutral">Sin detección</span>
              )}
            </div>

            <div className="features-stats">
              <div className="feature-stat-item">
                <span className="feature-stat-val">
                  {detection?.exito ? (detection.landmarks?.length ?? 0) : 0}
                </span>
                <span className="feature-stat-lbl">Landmarks</span>
              </div>
              <div className="feature-stat-item">
                <span className="feature-stat-val">
                  {detection?.exito ? (detection.landmarks?.length ?? 0) * 2 : 0}
                </span>
                <span className="feature-stat-lbl">Características</span>
              </div>
              <div className="feature-stat-item">
                <span className="feature-stat-val">
                  {detection?.exito ? detection.manos_detectadas : 0}
                </span>
                <span className="feature-stat-lbl">Manos</span>
              </div>
            </div>

            {topClases.length > 0 && (
              <>
                <p className="field-label" style={{ marginBottom: "8px", marginTop: "12px" }}>
                  Probabilidades por clase (top 5)
                </p>
                <div className="class-list">
                  {topClases.map(([cls, conf]) => (
                    <div key={cls} className="class-row">
                      <span className="class-name">{cls}</span>
                      <div className="class-bar-track">
                        <div
                          className={`class-bar-fill ${
                            cls === detection?.prediccion ? "class-bar-active" : ""
                          }`}
                          style={{ width: `${Math.round(conf * 100)}%` }}
                        />
                      </div>
                      <span className="class-pct">{(conf * 100).toFixed(1)}%</span>
                    </div>
                  ))}
                </div>
              </>
            )}

            {!detection?.exito && (
              <p className="empty-note" style={{ marginTop: "8px" }}>
                Activa la cámara y muestra una mano para ver las características extraídas.
              </p>
            )}
          </div>

          {/* Historial de mensajes */}
          <div className="card">
            <div className="card-header">
              <h2>Historial de mensajes</h2>
              <button className="btn-icon" onClick={loadHistory}>
                Actualizar
              </button>
            </div>
            <div className="history-list">
              {history.length === 0 ? (
                <p className="empty-note">Sin mensajes enviados aún.</p>
              ) : (
                [...history]
                  .reverse()
                  .slice(0, 10)
                  .map((item, i) => (
                    <div key={i} className="history-item">
                      <div className="history-item-top">
                        <span className="history-sign">{item.prediction}</span>
                        <span
                          className={`history-badge ${item.sent ? "sent-badge" : "failed-badge"}`}
                        >
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

      {/* Señas disponibles - ancho completo */}
      <div className="card signs-available-card">
        <div className="card-header">
          <h2>Señas disponibles</h2>
          <span className="badge">{clasesModelo.length} señas</span>
        </div>
        <div className="signs-tiles-grid">
          {!modeloEntrenado ? (
            <p className="empty-note">
              El modelo aún no ha sido entrenado. El administrador debe iniciar el entrenamiento desde el Módulo Administrador.
            </p>
          ) : clasesModelo.length === 0 ? (
            <p className="empty-note">
              No se encontraron clases en el modelo entrenado.
            </p>
          ) : (
            clasesModelo.map((sign) => (
              <div
                key={sign}
                className={`sign-user-tile ${
                  detection?.prediccion === sign && aboveThreshold ? "sign-tile-active" : ""
                }`}
              >
                <span className="sign-tile-name">{sign}</span>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
