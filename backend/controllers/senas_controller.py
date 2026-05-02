import io
import os
from flask import request, jsonify
from PIL import Image
import pillow_heif
from services.senas_service import SenasService

pillow_heif.register_heif_opener()

EXTENSIONES_VALIDAS = {"jpg", "jpeg", "png", "heic", "heif"}


def convertir_a_jpg(datos: bytes, nombre_original: str):
    """
    Si el archivo es HEIC/HEIF lo convierte a JPG en memoria.
    Para jpg/png devuelve los datos sin modificar.
    Retorna (datos_bytes, nombre_final, content_type).
    """
    extension = nombre_original.rsplit(".", 1)[-1].lower() if "." in nombre_original else ""

    if extension in ("heic", "heif"):
        imagen = Image.open(io.BytesIO(datos)).convert("RGB")
        buffer = io.BytesIO()
        imagen.save(buffer, format="JPEG", quality=90)
        nombre_final = nombre_original.rsplit(".", 1)[0] + ".jpg"
        return buffer.getvalue(), nombre_final, "image/jpeg"

    return datos, nombre_original, "image/jpeg"


class SenasController:
    """Controller para el CRUD de categorias e imagenes de señas."""

    def __init__(self):
        self.senas_service = SenasService()

    # ------------------------------------------------------------------
    # Categorias
    # ------------------------------------------------------------------

    def listar_categorias(self):
        resultado = self.senas_service.listar_categorias()
        status = 200 if resultado["exito"] else 500
        return jsonify(resultado), status

    def crear_categoria(self):
        data = request.get_json()
        if not data or "nombre" not in data:
            return jsonify({"exito": False, "mensaje": "Se requiere el campo 'nombre'."}), 400

        resultado = self.senas_service.crear_categoria(data["nombre"])
        status = 201 if resultado["exito"] else 400
        return jsonify(resultado), status

    def eliminar_categoria(self, nombre):
        resultado = self.senas_service.eliminar_categoria(nombre)
        status = 200 if resultado["exito"] else 500
        return jsonify(resultado), status

    # ------------------------------------------------------------------
    # Imagenes
    # ------------------------------------------------------------------

    def listar_imagenes(self, categoria):
        resultado = self.senas_service.listar_imagenes(categoria)
        status = 200 if resultado["exito"] else 500
        return jsonify(resultado), status

    def subir_imagen(self, categoria):
        if "imagen" not in request.files:
            return jsonify({"exito": False, "mensaje": "No se envio ningun archivo en el campo 'imagen'."}), 400

        archivo = request.files["imagen"]

        if archivo.filename == "":
            return jsonify({"exito": False, "mensaje": "El archivo no tiene nombre."}), 400

        extension = archivo.filename.rsplit(".", 1)[-1].lower() if "." in archivo.filename else ""
        if extension not in EXTENSIONES_VALIDAS:
            return jsonify({"exito": False, "mensaje": f"Extension no permitida. Usa: {EXTENSIONES_VALIDAS}"}), 400

        datos_originales = archivo.read()
        datos, nombre_final, content_type = convertir_a_jpg(datos_originales, archivo.filename)

        convertido = extension in ("heic", "heif")

        resultado = self.senas_service.subir_imagen(categoria, nombre_final, datos, content_type)

        if resultado["exito"] and convertido:
            resultado["mensaje"] = f"Imagen HEIC convertida a JPG y subida correctamente como '{nombre_final}'."

        status = 201 if resultado["exito"] else 500
        return jsonify(resultado), status

    def eliminar_imagen(self, categoria, nombre_archivo):
        resultado = self.senas_service.eliminar_imagen(categoria, nombre_archivo)
        status = 200 if resultado["exito"] else 500
        return jsonify(resultado), status


senas_controller = SenasController()
