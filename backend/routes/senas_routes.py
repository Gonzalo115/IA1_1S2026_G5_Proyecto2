from flask import Blueprint
from controllers.senas_controller import senas_controller

senas_bp = Blueprint("senas", __name__, url_prefix="/api/senas")


# ------------------------------------------------------------------
# Categorias
# ------------------------------------------------------------------

@senas_bp.route("/", methods=["GET"])
def listar_categorias():
    """GET /api/senas/ — Lista todas las categorias (carpetas) en S3."""
    return senas_controller.listar_categorias()


@senas_bp.route("/", methods=["POST"])
def crear_categoria():
    """POST /api/senas/ — Crea una nueva categoria. Body JSON: { "nombre": "Hola" }"""
    return senas_controller.crear_categoria()


@senas_bp.route("/<string:nombre>", methods=["DELETE"])
def eliminar_categoria(nombre):
    """DELETE /api/senas/{nombre} — Elimina la categoria y todas sus imagenes."""
    return senas_controller.eliminar_categoria(nombre)


# ------------------------------------------------------------------
# Imagenes dentro de una categoria
# ------------------------------------------------------------------

@senas_bp.route("/<string:categoria>/imagenes", methods=["GET"])
def listar_imagenes(categoria):
    """GET /api/senas/{categoria}/imagenes — Lista las imagenes de una categoria."""
    return senas_controller.listar_imagenes(categoria)


@senas_bp.route("/<string:categoria>/imagenes", methods=["POST"])
def subir_imagen(categoria):
    """POST /api/senas/{categoria}/imagenes — Sube una imagen. Form-data: imagen=<archivo>"""
    return senas_controller.subir_imagen(categoria)


@senas_bp.route("/<string:categoria>/imagenes/<string:nombre_archivo>", methods=["DELETE"])
def eliminar_imagen(categoria, nombre_archivo):
    """DELETE /api/senas/{categoria}/imagenes/{archivo} — Elimina una imagen especifica."""
    return senas_controller.eliminar_imagen(categoria, nombre_archivo)
