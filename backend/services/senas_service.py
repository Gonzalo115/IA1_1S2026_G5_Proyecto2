from botocore.exceptions import ClientError
from services.s3_service import S3Service


class SenasService:
    """Logica de negocio para el CRUD de categorias e imagenes en S3."""

    def __init__(self):
        self.s3 = S3Service()

    # ------------------------------------------------------------------
    # Categorias
    # ------------------------------------------------------------------

    def listar_categorias(self):
        try:
            categorias = self.s3.listar_categorias()
            return {"exito": True, "categorias": categorias, "total": len(categorias)}
        except ClientError as e:
            return {"exito": False, "mensaje": str(e)}

    def crear_categoria(self, nombre: str):
        nombre = nombre.strip()
        if not nombre:
            return {"exito": False, "mensaje": "El nombre de la categoria no puede estar vacio."}

        try:
            existentes = self.s3.listar_categorias()
            if nombre in existentes:
                return {"exito": False, "mensaje": f"La categoria '{nombre}' ya existe."}

            self.s3.crear_categoria(nombre)
            return {"exito": True, "mensaje": f"Categoria '{nombre}' creada correctamente.", "categoria": nombre}
        except ClientError as e:
            return {"exito": False, "mensaje": str(e)}

    def eliminar_categoria(self, nombre: str):
        try:
            eliminados = self.s3.eliminar_categoria(nombre)
            return {
                "exito": True,
                "mensaje": f"Categoria '{nombre}' eliminada. Objetos borrados: {eliminados}.",
            }
        except ClientError as e:
            return {"exito": False, "mensaje": str(e)}

    # ------------------------------------------------------------------
    # Imagenes
    # ------------------------------------------------------------------

    def listar_imagenes(self, categoria: str):
        try:
            imagenes = self.s3.listar_imagenes(categoria)
            return {"exito": True, "categoria": categoria, "imagenes": imagenes, "total": len(imagenes)}
        except ClientError as e:
            return {"exito": False, "mensaje": str(e)}

    def subir_imagen(self, categoria: str, nombre_archivo: str, datos: bytes, content_type: str = "image/jpeg"):
        if not datos:
            return {"exito": False, "mensaje": "No se recibieron datos de imagen."}
        try:
            resultado = self.s3.subir_imagen(categoria, nombre_archivo, datos, content_type)
            return {"exito": True, "mensaje": "Imagen subida correctamente.", "imagen": resultado}
        except ClientError as e:
            return {"exito": False, "mensaje": str(e)}

    def eliminar_imagen(self, categoria: str, nombre_archivo: str):
        try:
            key = self.s3.eliminar_imagen(categoria, nombre_archivo)
            return {"exito": True, "mensaje": f"Imagen '{nombre_archivo}' eliminada.", "key": key}
        except ClientError as e:
            return {"exito": False, "mensaje": str(e)}
