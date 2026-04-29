import { useState, useRef, useEffect } from "react";
import "./App.css";

interface HandDetectionResult {
  exito: boolean;
  prediccion: string | null;
  confianza: number | null;
  confianzas_por_clase: Record<string, number>;
  mensaje: string;
  manos_detectadas: number;
}

function App() {
  const [count, setCount] = useState(0);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const [cameraActive, setCameraActive] = useState(false);
  const [detectionResult, setDetectionResult] =
    useState<HandDetectionResult | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [isTraining, setIsTraining] = useState(false);

  // Inicializar cámara
  useEffect(() => {
    const initCamera = async () => {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({
          video: { width: { ideal: 640 }, height: { ideal: 480 } },
        });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          setCameraActive(true);
        }
      } catch (error) {
        console.error("Error al acceder a la cámara:", error);
      }
    };

    initCamera();

    return () => {
      // Limpiar stream cuando se desmonta
      if (videoRef.current?.srcObject) {
        const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
        tracks.forEach((track) => track.stop());
      }
    };
  }, []);

  // Enviar peticiones cada 0.5 segundos
  useEffect(() => {
    if (!cameraActive || !videoRef.current || !canvasRef.current) return;

    const interval = setInterval(async () => {
      const video = videoRef.current;
      const canvas = canvasRef.current;

      if (!video || !canvas) return;

      // Dibujar el frame actual del video en el canvas
      const ctx = canvas.getContext("2d");
      if (!ctx) return;

      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Convertir canvas a blob y enviar al backend
      canvas.toBlob(
        async (blob) => {
          if (!blob) return;

          const formData = new FormData();
          formData.append("imagen", blob, "frame.jpg");

          try {
            setIsLoading(true);
            const response = await fetch(
              "http://localhost:5000/api/manos/analizar",
              {
                method: "POST",
                body: formData,
              },
            );

            if (response.ok) {
              const result = await response.json();
              setDetectionResult(result);
              console.log("Detección:", result);
            }
          } catch (error) {
            console.error("Error al enviar imagen:", error);
          } finally {
            setIsLoading(false);
          }
        },
        "image/jpeg",
        0.8,
      );
    }, 500); // Cada 0.5 segundos

    return () => clearInterval(interval);
  }, [cameraActive]);

  // Función para entrenar el modelo
  const entrenarModelo = async () => {
    try {
      setIsTraining(true);
      const formData = new FormData();
      formData.append("ruta_dataset", "data");

      const response = await fetch("http://localhost:5000/api/manos/entrenar", {
        method: "POST",
        body: formData,
      });

      if (response.ok) {
        const result = await response.json();
        alert(
          `✅ Entrenamiento completado!\n\nAccuracy: ${(result.accuracy * 100).toFixed(2)}%\nMuestras: ${result.total_muestras}\nClasificaciones: ${result.etiquetas.join(", ")}`,
        );
        console.log("Resultado del entrenamiento:", result);
      } else {
        const error = await response.json();
        alert(`❌ Error: ${error.mensaje}`);
      }
    } catch (error) {
      console.error("Error al entrenar:", error);
      alert(`❌ Error al entrenar: ${error}`);
    } finally {
      setIsTraining(false);
    }
  };

  return (
    <>
      <section id="center">
        <div className="hero">
          <div style={{ position: "relative", textAlign: "center" }}>
            {/* Canvas oculto para capturar frames */}
            <canvas
              ref={canvasRef}
              width={640}
              height={480}
              style={{ display: "none" }}
            />

            {/* Video de la cámara */}
            <video
              ref={videoRef}
              autoPlay
              playsInline
              style={{
                width: "100%",
                maxWidth: "640px",
                height: "auto",
                border: "2px solid #00d9ff",
                borderRadius: "8px",
                marginBottom: "20px",
              }}
              onLoadedMetadata={() => {
                if (canvasRef.current && videoRef.current) {
                  canvasRef.current.width = videoRef.current.videoWidth;
                  canvasRef.current.height = videoRef.current.videoHeight;
                }
              }}
            />

            {/* Información de detección */}
            <div
              style={{
                marginTop: "20px",
                padding: "15px",
                backgroundColor: "#1a1a2e",
                borderRadius: "8px",
                border: "1px solid #00d9ff",
              }}
            >
              {cameraActive ? (
                <>
                  <p style={{ color: "#00d9ff", fontWeight: "bold" }}>
                    ✋ Cámara activa - Detectando manos
                  </p>
                  {detectionResult && (
                    <div style={{ textAlign: "left", marginTop: "10px" }}>
                      {detectionResult.exito ? (
                        <>
                          <p style={{ color: "#00ff00", margin: "5px 0" }}>
                            ✅ Seña detectada:{" "}
                            <strong>{detectionResult.prediccion}</strong>
                          </p>
                          <p style={{ color: "#ffaa00", margin: "5px 0" }}>
                            📊 Confianza:{" "}
                            {(detectionResult.confianza! * 100).toFixed(2)}%
                          </p>
                          <p
                            style={{
                              color: "#888",
                              margin: "5px 0",
                              fontSize: "12px",
                            }}
                          >
                            {detectionResult.mensaje}
                          </p>
                        </>
                      ) : (
                        <p style={{ color: "#ff6b6b", margin: "5px 0" }}>
                          ⚠️ {detectionResult.mensaje}
                        </p>
                      )}
                      {isLoading && (
                        <p style={{ color: "#ffaa00", margin: "5px 0" }}>
                          ⏳ Analizando...
                        </p>
                      )}
                    </div>
                  )}
                </>
              ) : (
                <p style={{ color: "#ff6b6b" }}>
                  ❌ Esperando permisos de cámara...
                </p>
              )}
            </div>
          </div>
        </div>

        <div>
          <h1>Detector de Señas de Mano (1-10)</h1>
          <p>
            La cámara envía frames cada <code>0.5 segundos</code> para analizar
            la seña
          </p>
        </div>

        <div
          style={{
            marginTop: "20px",
            display: "flex",
            gap: "10px",
            justifyContent: "center",
            flexWrap: "wrap",
          }}
        >
          <button
            className="counter"
            onClick={() => setCount((count) => count + 1)}
            style={{ opacity: isTraining ? 0.5 : 1 }}
          >
            Count is {count}
          </button>

          <button
            onClick={entrenarModelo}
            disabled={isTraining}
            style={{
              padding: "10px 20px",
              backgroundColor: isTraining ? "#666" : "#00d9ff",
              color: "#000",
              border: "none",
              borderRadius: "5px",
              cursor: isTraining ? "not-allowed" : "pointer",
              fontWeight: "bold",
              fontSize: "14px",
              transition: "0.3s",
            }}
          >
            {isTraining ? "⏳ Entrenando..." : "🤖 Entrenar Modelo"}
          </button>
        </div>
      </section>

      <div className="ticks"></div>

      <section id="next-steps">
        <div id="docs">
          <svg className="icon" role="presentation" aria-hidden="true">
            <use href="/icons.svg#documentation-icon"></use>
          </svg>
          <h2>📚 Información del Sistema</h2>
          <p>Detector de Señas (1-10) con MediaPipe</p>
          <ul>
            <li>
              <a href="http://localhost:5000/api/manos/saludo" target="_blank">
                ✓ Verificar Backend
              </a>
            </li>
            <li>
              <a href="http://localhost:5000/" target="_blank">
                ✓ Ver Endpoints
              </a>
            </li>
          </ul>
        </div>
      </section>

      <div className="ticks"></div>
      <section id="spacer"></section>
    </>
  );
}

export default App;
