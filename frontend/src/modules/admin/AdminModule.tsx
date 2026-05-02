import { useState, useEffect } from "react";
import "./AdminModule.css";
import ConfidenceBar from "../../components/ConfidenceBar/ConfidenceBar";
import SenasModule from "../senas/SenasModule";
import { updateConfig, trainModel } from "../../api/admin";
import type { AdminConfig, TrainingResult } from "../../types";

const ADMIN_USER = "admin";
const ADMIN_PASS = "admin2026";

interface Props {
  config: AdminConfig | null;
  onConfigChange: () => void;
}

export default function AdminModule({ config, onConfigChange }: Props) {
  const [loggedIn, setLoggedIn] = useState(false);
  const [loginUser, setLoginUser] = useState("");
  const [loginPass, setLoginPass] = useState("");
  const [loginError, setLoginError] = useState(false);

  const [threshold, setThreshold] = useState(config?.confidence_threshold ?? 0.5);
  const [format, setFormat] = useState(config?.telegram_message_format ?? "");
  const [telegramEnabled, setTelegramEnabled] = useState(config?.telegram_enabled ?? true);
  const [saving, setSaving] = useState(false);
  const [saveMsg, setSaveMsg] = useState<string | null>(null);
  const [training, setTraining] = useState(false);
  const [trainingResult, setTrainingResult] = useState<TrainingResult | null>(null);

  useEffect(() => {
    if (config) {
      setThreshold(config.confidence_threshold);
      setFormat(config.telegram_message_format);
      setTelegramEnabled(config.telegram_enabled);
    }
  }, [config]);

  const saveConfig = async () => {
    setSaving(true);
    setSaveMsg(null);
    try {
      await updateConfig({
        confidence_threshold: threshold,
        telegram_message_format: format,
        telegram_enabled: telegramEnabled,
        available_signs: config?.available_signs ?? [],
      });
      setSaveMsg("Configuración guardada correctamente");
      onConfigChange();
    } catch {
      setSaveMsg("Error al guardar la configuración");
    } finally {
      setSaving(false);
    }
  };

  const startTraining = async () => {
    setTraining(true);
    setTrainingResult(null);
    try {
      const data = await trainModel();
      setTrainingResult(data);
    } catch {
      setTrainingResult({ exito: false, mensaje: "Error de conexión al iniciar el entrenamiento" });
    } finally {
      setTraining(false);
    }
  };

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    if (loginUser === ADMIN_USER && loginPass === ADMIN_PASS) {
      setLoggedIn(true);
      setLoginError(false);
    } else {
      setLoginError(true);
    }
  };

  if (!loggedIn) {
    return (
      <div className="login-wrapper">
        <div className="login-card">
          <div className="login-logo">HT</div>
          <h1 className="login-title">Módulo Administrador</h1>
          <p className="login-subtitle">Ingresa tus credenciales para continuar</p>
          <form onSubmit={handleLogin} className="login-form">
            <input
              type="text"
              placeholder="Usuario"
              value={loginUser}
              onChange={(e) => setLoginUser(e.target.value)}
              className="text-input"
              autoComplete="username"
            />
            <input
              type="password"
              placeholder="Contraseña"
              value={loginPass}
              onChange={(e) => setLoginPass(e.target.value)}
              className="text-input"
              autoComplete="current-password"
            />
            {loginError && (
              <p className="login-error">Credenciales incorrectas. Intenta de nuevo.</p>
            )}
            <button type="submit" className="btn btn-primary btn-lg login-btn">
              Ingresar
            </button>
          </form>
          <p className="login-hint">
            Usuario: <strong>admin</strong> &nbsp;|&nbsp; Contraseña: <strong>admin2026</strong>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="admin-module">
      <div className="module-header">
        <h1>Módulo Administrador</h1>
        <p>Configuración del sistema y entrenamiento del modelo de clasificación</p>
      </div>

      <div className="admin-top-grid">
        {/* Umbral de confianza */}
        <div className="card">
          <div className="card-header">
            <h2>Umbral de confianza</h2>
          </div>
          <div className="field-group">
            <div className="threshold-row">
              <span className="field-label">Valor actual</span>
              <strong className="threshold-value">{Math.round(threshold * 100)}%</strong>
            </div>
            <ConfidenceBar value={threshold} />
            <input
              type="range"
              min={0}
              max={1}
              step={0.05}
              value={threshold}
              onChange={(e) => setThreshold(parseFloat(e.target.value))}
              className="slider"
            />
            <div className="slider-marks">
              <span>0%</span>
              <span>50%</span>
              <span>100%</span>
            </div>
            <p className="field-note">
              Las predicciones con confianza menor a este valor no activarán el envío a Telegram.
            </p>
          </div>
        </div>

        {/* Bot de Telegram */}
        <div className="card">
          <div className="card-header">
            <h2>Bot de Telegram</h2>
            <button
              className={`toggle-btn ${telegramEnabled ? "toggle-on" : "toggle-off"}`}
              onClick={() => setTelegramEnabled(!telegramEnabled)}
            >
              {telegramEnabled ? "Activo" : "Inactivo"}
            </button>
          </div>
          <div className="field-group">
            <label className="field-label">Formato del mensaje</label>
            <input
              type="text"
              value={format}
              onChange={(e) => setFormat(e.target.value)}
              className="text-input"
              placeholder="HandTalk AI detectó: {prediction} | confianza: {confidence}"
            />
            <p className="field-note">
              Variables dinámicas disponibles:{" "}
              <code className="inline-code">{"{prediction}"}</code> y{" "}
              <code className="inline-code">{"{confidence}"}</code>
            </p>
          </div>
        </div>
      </div>

      {/* Save button */}
      <div className="save-bar">
        <button className="btn btn-primary btn-lg" onClick={saveConfig} disabled={saving}>
          {saving ? "Guardando..." : "Guardar configuración"}
        </button>
        {saveMsg && (
          <span
            className={`status-msg ${
              saveMsg.includes("Error") ? "status-error" : "status-success"
            }`}
          >
            {saveMsg}
          </span>
        )}
      </div>

      {/* Demostración del entrenamiento */}
      <div className="card">
        <div className="card-header">
          <h2>Demostración del entrenamiento</h2>
          <button className="btn btn-primary" onClick={startTraining} disabled={training}>
            {training ? "Entrenando..." : "Iniciar entrenamiento"}
          </button>
        </div>

        {training && (
          <div className="training-progress">
            <div className="spinner" />
            <p>Procesando imágenes desde S3. Esto puede tardar varios minutos...</p>
          </div>
        )}

        {trainingResult && (
          <div
            className={`result-card ${
              trainingResult.exito ? "result-success" : "result-error"
            }`}
          >
            {trainingResult.exito ? (
              <>
                <div className="metrics-grid">
                  <div className="metric-item">
                    <span className="metric-value">
                      {Math.round((trainingResult.accuracy ?? 0) * 100)}%
                    </span>
                    <span className="metric-label">Precisión (accuracy)</span>
                  </div>
                  <div className="metric-item">
                    <span className="metric-value">{trainingResult.total_muestras}</span>
                    <span className="metric-label">Total muestras</span>
                  </div>
                  <div className="metric-item">
                    <span className="metric-value">{trainingResult.muestras_entrenamiento}</span>
                    <span className="metric-label">Entrenamiento</span>
                  </div>
                  <div className="metric-item">
                    <span className="metric-value">{trainingResult.muestras_prueba}</span>
                    <span className="metric-label">Prueba</span>
                  </div>
                </div>

                <div className="eval-section">
                  <h3>Clases entrenadas</h3>
                  <div className="signs-grid" style={{ marginTop: "8px" }}>
                    {trainingResult.etiquetas?.map((label) => (
                      <span key={label} className="sign-chip">
                        {label}
                      </span>
                    ))}
                  </div>
                </div>

                {trainingResult.reporte && (
                  <div className="eval-section">
                    <h3>Evaluación del modelo (precisión, recall, F1)</h3>
                    <div className="table-wrapper">
                      <table className="eval-table">
                        <thead>
                          <tr>
                            <th>Clase</th>
                            <th>Precisión</th>
                            <th>Recall</th>
                            <th>F1-score</th>
                            <th>Muestras</th>
                          </tr>
                        </thead>
                        <tbody>
                          {Object.entries(trainingResult.reporte)
                            .filter(
                              ([key]) =>
                                !["accuracy", "macro avg", "weighted avg"].includes(key)
                            )
                            .map(([cls, m]: [string, any]) => (
                              <tr key={cls}>
                                <td>
                                  <strong>{cls}</strong>
                                </td>
                                <td>{(m.precision * 100).toFixed(1)}%</td>
                                <td>{(m.recall * 100).toFixed(1)}%</td>
                                <td>{(m["f1-score"] * 100).toFixed(1)}%</td>
                                <td>{m.support}</td>
                              </tr>
                            ))}
                        </tbody>
                      </table>
                    </div>

                    {trainingResult.reporte["weighted avg"] && (
                      <div className="weighted-avg">
                        <span>Promedio ponderado:</span>
                        <span>
                          Precisión:{" "}
                          {(
                            trainingResult.reporte["weighted avg"].precision * 100
                          ).toFixed(1)}
                          % &nbsp;|&nbsp; Recall:{" "}
                          {(
                            trainingResult.reporte["weighted avg"].recall * 100
                          ).toFixed(1)}
                          % &nbsp;|&nbsp; F1:{" "}
                          {(
                            trainingResult.reporte["weighted avg"]["f1-score"] * 100
                          ).toFixed(1)}
                          %
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

      {/* Gestión de Señas - imágenes en S3 */}
      <div className="senas-section-wrapper">
        <div className="senas-section-header">
          <h2>Gestión de Señas</h2>
          <p>Administra las categorías e imágenes en AWS S3 para entrenar el modelo</p>
        </div>
        <SenasModule />
      </div>
    </div>
  );
}
