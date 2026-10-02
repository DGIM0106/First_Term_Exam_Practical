import os
import uuid
from typing import BinaryIO
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_BUCKET_VIDEOS = os.getenv("AWS_BUCKET_VIDEOS", "mi-bucket-videos")
AWS_BUCKET_IMAGES = os.getenv("AWS_BUCKET_IMAGES", "mi-bucket-imagenes")


def get_s3_client():
    try:
        import boto3
        return boto3.client(
            "s3",
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
            region_name=AWS_REGION,
        )
    except Exception as e:
        print(f"Error al inicializar cliente boto3: {e}")
        return None


def upload_file_to_s3(file_obj: BinaryIO, filename: str, content_type: str, is_video: bool = True) -> str:
    """
    Sube un archivo (video o imagen) al bucket correspondiente en AWS S3.
    Retorna la URL pública del archivo subido.
    """
    bucket_name = AWS_BUCKET_VIDEOS if is_video else AWS_BUCKET_IMAGES
    ext = os.path.splitext(filename)[1]
    unique_key = f"{uuid.uuid4()}{ext}"

    s3_client = get_s3_client()
    if s3_client and AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
        try:
            s3_client.upload_fileobj(
                file_obj,
                bucket_name,
                unique_key,
                ExtraArgs={
                    "ContentType": content_type,
                },
            )
            # URL estándar de S3 público
            s3_url = f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{unique_key}"
            return s3_url
        except Exception as e:
            print(f"Error al subir a S3 ({bucket_name}): {e}")
            raise e
    else:
        # Fallback de desarrollo si aún no se han configurado credenciales reales de AWS
        print("Aviso: Credenciales de AWS no detectadas. Usando URL simulada de desarrollo.")
        fallback_url = (
            f"https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4"
            if is_video
            else f"https://images.unsplash.com/photo-1618005182384-a83a8bd57fbe?w=800&auto=format&fit=crop&q=80"
        )
        return fallback_url


def delete_file_from_s3(file_url: str, is_video: bool = True) -> bool:
    """
    Elimina un archivo del bucket de AWS S3 según su URL.
    """
    if not file_url:
        return False

    bucket_name = AWS_BUCKET_VIDEOS if is_video else AWS_BUCKET_IMAGES
    s3_client = get_s3_client()

    try:
        # Extraer el key del archivo desde la URL (https://bucket.s3.region.amazonaws.com/key)
        key = file_url.split("/")[-1]
        if s3_client and AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY:
            s3_client.delete_object(Bucket=bucket_name, Key=key)
            print(f"Archivo {key} eliminado de S3 ({bucket_name})")
            return True
    except Exception as e:
        print(f"Error al eliminar de S3 ({file_url}): {e}")

    return False
