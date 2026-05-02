import { useState, useEffect, useRef } from "react";
import "./SenasModule.css";
import {
  getCategorias,
  crearCategoria,
  eliminarCategoria,
  getImagenes,
  subirImagen,
  eliminarImagen,
} from "../../api/senas";
import type { ImagenInfo } from "../../types";

export default function SenasModule() {
  const [categorias, setCategorias] = useState<string[]>([]);
  const [loadingCat, setLoadingCat] = useState(true);
  const [nuevaCategoria, setNuevaCategoria] = useState("");
  const [creando, setCreando] = useState(false);
  const [msgCategoria, setMsgCategoria] = useState<string | null>(null);

  const [categoriaActiva, setCategoriaActiva] = useState<string | null>(null);
  const [imagenes, setImagenes] = useState<ImagenInfo[]>([]);
  const [loadingImg, setLoadingImg] = useState(false);
  const [subiendo, setSubiendo] = useState(false);
  const [msgImagen, setMsgImagen] = useState<string | null>(null);

  const fileInputRef = useRef<HTMLInputElement>(null);

  const cargarCategorias = async () => {
    setLoadingCat(true);
    setMsgCategoria(null);
    try {
      const data = await getCategorias();
      setCategorias(data);
    } catch {
      setMsgCategoria("Error al cargar las categorías desde S3");
    } finally {
      setLoadingCat(false);
    }
  };

  const cargarImagenes = async (categoria: string) => {
    setLoadingImg(true);
    setImagenes([]);
    setMsgImagen(null);
    try {
      const data = await getImagenes(categoria);
      setImagenes(data.imagenes || []);
    } catch {
      setMsgImagen("Error al cargar las imágenes");
    } finally {
      setLoadingImg(false);
    }
  };

  useEffect(() => {
    cargarCategorias();
  }, []);

  useEffect(() => {
    if (categoriaActiva) {
      cargarImagenes(categoriaActiva);
    }
  }, [categoriaActiva]);

  const handleCrear = async () => {
    const nombre = nuevaCategoria.trim();
    if (!nombre) return;
    setCreando(true);
    setMsgCategoria(null);
    try {
      const res = await crearCategoria(nombre);
      if (res.exito) {
        setNuevaCategoria("");
        setMsgCategoria(`Categoría "${nombre}" creada correctamente`);
        await cargarCategorias();
      } else {
        setMsgCategoria(res.mensaje);
      }
    } catch {
      setMsgCategoria("Error de conexión con el servidor");
    } finally {
      setCreando(false);
    }
  };

  const handleEliminarCategoria = async (nombre: string) => {
    if (!confirm(`¿Eliminar la categoría "${nombre}" y todas sus imágenes?`)) return;
    setMsgCategoria(null);
    try {
      const res = await eliminarCategoria(nombre);
      if (res.exito) {
        setMsgCategoria(`Categoría "${nombre}" eliminada`);
        if (categoriaActiva === nombre) {
          setCategoriaActiva(null);
          setImagenes([]);
        }
        await cargarCategorias();
      } else {
        setMsgCategoria(res.mensaje);
      }
    } catch {
      setMsgCategoria("Error de conexión con el servidor");
    }
  };

  const handleSubirImagenes = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const files = Array.from(e.target.files || []);
    if (!files.length || !categoriaActiva) return;

    setSubiendo(true);
    setMsgImagen(null);
    let exitosos = 0;
    let fallidos = 0;

    for (const file of files) {
      try {
        const res = await subirImagen(categoriaActiva, file);
        if (res.exito) {
          exitosos++;
        } else {
          fallidos++;
        }
      } catch {
        fallidos++;
      }
    }

    const msg =
      exitosos > 0
        ? `${exitosos} imagen(es) subida(s) correctamente.${fallidos > 0 ? ` ${fallidos} fallaron.` : ""}`
        : `Error: ${fallidos} imagen(es) no se pudieron subir.`;
    setMsgImagen(msg);
    await cargarImagenes(categoriaActiva);
    setSubiendo(false);
    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };

  const handleEliminarImagen = async (nombre: string) => {
    if (!categoriaActiva) return;
    setMsgImagen(null);
    try {
      const res = await eliminarImagen(categoriaActiva, nombre);
      if (res.exito) {
        setMsgImagen(`Imagen "${nombre}" eliminada`);
        await cargarImagenes(categoriaActiva);
      } else {
        setMsgImagen(res.mensaje);
      }
    } catch {
      setMsgImagen("Error de conexión con el servidor");
    }
  };

  return (
    <div className="senas-module">
      <div className="module-header">
        <h1>Gestión de Señas</h1>
        <p>
          Administra las categorías e imágenes almacenadas en AWS S3 para el entrenamiento del
          modelo
        </p>
      </div>

      <div className="senas-layout">
        {/* Left panel: categories */}
        <div className="categories-panel">
          <div className="card">
            <div className="card-header">
              <h2>Categorías</h2>
              <span className="badge">{categorias.length}</span>
            </div>

            <div className="add-row">
              <input
                type="text"
                value={nuevaCategoria}
                onChange={(e) => setNuevaCategoria(e.target.value)}
                onKeyDown={(e) => e.key === "Enter" && handleCrear()}
                className="text-input"
                placeholder="Nueva categoría (ej: Hola)"
              />
              <button
                className="btn btn-primary"
                onClick={handleCrear}
                disabled={creando || !nuevaCategoria.trim()}
              >
                {creando ? "..." : "Crear"}
              </button>
            </div>

            {msgCategoria && (
              <p
                className={`status-msg ${
                  msgCategoria.includes("Error") ? "status-error" : "status-success"
                }`}
              >
                {msgCategoria}
              </p>
            )}

            {loadingCat ? (
              <div className="loading-state">Cargando categorías...</div>
            ) : categorias.length === 0 ? (
              <p className="empty-note">No hay categorías en el bucket de S3.</p>
            ) : (
              <div className="category-list">
                {categorias.map((cat) => (
                  <div
                    key={cat}
                    className={`category-item ${categoriaActiva === cat ? "category-active" : ""}`}
                    onClick={() => setCategoriaActiva(cat)}
                  >
                    <span className="category-name">{cat}</span>
                    <button
                      className="btn-remove"
                      onClick={(e) => {
                        e.stopPropagation();
                        handleEliminarCategoria(cat);
                      }}
                    >
                      Eliminar
                    </button>
                  </div>
                ))}
              </div>
            )}

            <div className="refresh-row">
              <button className="btn-icon" onClick={cargarCategorias}>
                Actualizar lista
              </button>
            </div>
          </div>
        </div>

        {/* Right panel: images */}
        <div className="images-panel">
          {categoriaActiva ? (
            <div className="card">
              <div className="card-header">
                <div>
                  <h2>{categoriaActiva}</h2>
                  <p className="cat-subtitle">
                    {imagenes.length} imagen(es) en esta categoría
                  </p>
                </div>
                <label
                  className={`btn btn-primary ${subiendo ? "btn-disabled" : ""}`}
                  style={{ cursor: subiendo ? "not-allowed" : "pointer" }}
                >
                  {subiendo ? "Subiendo..." : "Subir imágenes"}
                  <input
                    ref={fileInputRef}
                    type="file"
                    multiple
                    accept=".jpg,.jpeg,.png,.heic,.heif"
                    onChange={handleSubirImagenes}
                    style={{ display: "none" }}
                    disabled={subiendo}
                  />
                </label>
              </div>

              {msgImagen && (
                <p
                  className={`status-msg ${
                    msgImagen.includes("Error") || msgImagen.includes("fallaron")
                      ? "status-error"
                      : "status-success"
                  }`}
                >
                  {msgImagen}
                </p>
              )}

              {loadingImg ? (
                <div className="loading-state">Cargando imágenes...</div>
              ) : imagenes.length === 0 ? (
                <div className="empty-images">
                  <div className="empty-images-icon" />
                  <p>No hay imágenes en esta categoría</p>
                  <p className="empty-note">
                    Usa el botón "Subir imágenes" para agregar archivos JPG, PNG o HEIC.
                  </p>
                </div>
              ) : (
                <div className="images-grid">
                  {imagenes.map((img) => (
                    <div key={img.nombre} className="image-card">
                      <div className="image-thumb-wrapper">
                        <img
                          src={img.url}
                          alt={img.nombre}
                          className="image-thumb"
                          loading="lazy"
                          onError={(e) => {
                            (e.target as HTMLImageElement).style.display = "none";
                          }}
                        />
                      </div>
                      <div className="image-info">
                        <p className="image-name" title={img.nombre}>
                          {img.nombre}
                        </p>
                        <p className="image-size">
                          {(img.tamanio / 1024).toFixed(0)} KB
                        </p>
                        <button
                          className="btn-remove"
                          onClick={() => handleEliminarImagen(img.nombre)}
                        >
                          Eliminar
                        </button>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          ) : (
            <div className="card no-selection-card">
              <div className="empty-state">
                <div className="no-selection-icon" />
                <p>Selecciona una categoría para ver y gestionar sus imágenes</p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
