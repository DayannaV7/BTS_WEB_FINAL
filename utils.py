import os
from pathlib import Path
from fastapi import UploadFile, HTTPException
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL    = os.getenv("SUPABASE_URL")
SUPABASE_KEY    = os.getenv("SUPABASE_KEY")
SUPABASE_BUCKET = os.getenv("SUPABASE_BUCKET", "bts-imagenes")

TIPOS_PERMITIDOS = {"image/jpeg", "image/png", "image/webp", "image/gif"}
TAMANO_MAXIMO   = 5 * 1024 * 1024  # 5 MB


def supabase_client():
    if not SUPABASE_URL or not SUPABASE_KEY:
        raise RuntimeError("Faltan credenciales de Supabase en el .env")
    return create_client(SUPABASE_URL, SUPABASE_KEY)


def subir_imagen(file: UploadFile, carpeta: str = "integrantes") -> str:
    """
    Sube una imagen a Supabase Storage y retorna la URL pública.
    carpeta: subcarpeta dentro del bucket (ej: 'integrantes', 'albumes')
    """
    if file.content_type not in TIPOS_PERMITIDOS:
        raise HTTPException(
            status_code=400,
            detail=f"Tipo de archivo no permitido: {file.content_type}. "
                   f"Solo se aceptan: JPEG, PNG, WEBP, GIF."
        )

    contenido = file.file.read()
    if len(contenido) > TAMANO_MAXIMO:
        raise HTTPException(
            status_code=400,
            detail="La imagen supera el tamaño máximo permitido de 5 MB."
        )

    # Nombre único para evitar colisiones
    extension = Path(file.filename).suffix
    nombre_archivo = f"{carpeta}/{file.filename.replace(' ', '_')}"

    client = supabase_client()
    client.storage.from_(SUPABASE_BUCKET).upload(
        path=nombre_archivo,
        file=contenido,
        file_options={"content-type": file.content_type, "upsert": "true"}
    )

    url_publica = client.storage.from_(SUPABASE_BUCKET).get_public_url(nombre_archivo)
    return url_publica


def eliminar_imagen(url: str) -> bool:
    """Elimina una imagen de Supabase dado su URL público."""
    try:
        client = supabase_client()
        # Extraer la ruta del archivo desde la URL
        ruta = url.split(f"/storage/v1/object/public/{SUPABASE_BUCKET}/")[-1]
        client.storage.from_(SUPABASE_BUCKET).remove([ruta])
        return True
    except Exception:
        return False
