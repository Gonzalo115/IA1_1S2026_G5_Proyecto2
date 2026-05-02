import os
import boto3
from botocore.exceptions import ClientError
from dotenv import load_dotenv

load_dotenv()


class S3Service:
    """Servicio para operaciones sobre el bucket S3 que contiene el dataset de señas."""

    def __init__(self):
        self.bucket = os.getenv("S3_BUCKET_NAME", "img-entramiento-ia1-grupo5")
        self.prefix = os.getenv("S3_DATA_PREFIX", "Data/")
        self.region = os.getenv("AWS_REGION", "us-east-2")

        self.client = boto3.client(
            "s3",
            region_name=self.region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
        )

    # ------------------------------------------------------------------
    # Categorias (carpetas)
    # ------------------------------------------------------------------

    def listar_categorias(self):
        """Devuelve la lista de nombres de categorias (subcarpetas bajo Data/)."""
        response = self.client.list_objects_v2(
            Bucket=self.bucket,
            Prefix=self.prefix,
            Delimiter="/",
        )
        carpetas = response.get("CommonPrefixes", [])
        return [c["Prefix"].replace(self.prefix, "").rstrip("/") for c in carpetas]

    def crear_categoria(self, nombre: str):
        """Crea una carpeta vacia en S3 colocando un objeto placeholder."""
        key = f"{self.prefix}{nombre}/.keep"
        self.client.put_object(Bucket=self.bucket, Key=key, Body=b"")
        return nombre

    def eliminar_categoria(self, nombre: str):
        """Elimina todos los objetos bajo Data/{nombre}/."""
        prefix = f"{self.prefix}{nombre}/"
        paginator = self.client.get_paginator("list_objects_v2")
        objetos_a_borrar = []

        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                objetos_a_borrar.append({"Key": obj["Key"]})

        if not objetos_a_borrar:
            return 0

        self.client.delete_objects(
            Bucket=self.bucket,
            Delete={"Objects": objetos_a_borrar},
        )
        return len(objetos_a_borrar)

    # ------------------------------------------------------------------
    # Imagenes dentro de una categoria
    # ------------------------------------------------------------------

    def listar_imagenes(self, categoria: str):
        """Devuelve la lista de nombres de archivos en Data/{categoria}/."""
        prefix = f"{self.prefix}{categoria}/"
        extensiones = (".jpg", ".jpeg", ".png")

        paginator = self.client.get_paginator("list_objects_v2")
        archivos = []

        for page in paginator.paginate(Bucket=self.bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                nombre = obj["Key"].replace(prefix, "")
                if nombre and nombre.lower().endswith(extensiones):
                    archivos.append({
                        "nombre": nombre,
                        "key": obj["Key"],
                        "url": self._url_publica(obj["Key"]),
                        "tamanio": obj["Size"],
                        "ultima_modificacion": obj["LastModified"].isoformat(),
                    })

        return archivos

    def subir_imagen(self, categoria: str, nombre_archivo: str, datos: bytes, content_type: str = "image/jpeg"):
        """Sube una imagen a Data/{categoria}/{nombre_archivo}."""
        key = f"{self.prefix}{categoria}/{nombre_archivo}"
        self.client.put_object(
            Bucket=self.bucket,
            Key=key,
            Body=datos,
            ContentType=content_type,
        )
        return {"nombre": nombre_archivo, "key": key, "url": self._url_publica(key)}

    def eliminar_imagen(self, categoria: str, nombre_archivo: str):
        """Elimina Data/{categoria}/{nombre_archivo} del bucket."""
        key = f"{self.prefix}{categoria}/{nombre_archivo}"
        self.client.delete_object(Bucket=self.bucket, Key=key)
        return key

    def descargar_imagen_bytes(self, key: str) -> bytes:
        """Descarga un objeto S3 y devuelve sus bytes."""
        response = self.client.get_object(Bucket=self.bucket, Key=key)
        return response["Body"].read()

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    def _url_publica(self, key: str) -> str:
        return f"https://{self.bucket}.s3.{self.region}.amazonaws.com/{key}"
