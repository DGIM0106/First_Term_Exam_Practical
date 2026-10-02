import os
import uuid
import boto3
from typing import BinaryIO
from dotenv import load_dotenv

load_dotenv()

AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID", "")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY", "")
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_BUCKET_VIDEOS = os.getenv("AWS_BUCKET_VIDEOS", "fasttube-videos")
AWS_BUCKET_IMAGES = os.getenv("AWS_BUCKET_IMAGES", "fasttube-images")


def get_s3_client():
    return boto3.client(
        "s3",
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
        region_name=AWS_REGION,
    )


def upload_file_to_s3(file_obj: BinaryIO, filename: str, content_type: str, is_video: bool = True) -> str:
    bucket_name = AWS_BUCKET_VIDEOS if is_video else AWS_BUCKET_IMAGES
    ext = os.path.splitext(filename)[1]
    if not ext:
        ext = ".mp4" if is_video else ".jpg"
    unique_key = f"{uuid.uuid4()}{ext}"

    s3_client = get_s3_client()
    file_obj.seek(0)

    s3_client.upload_fileobj(
        file_obj,
        bucket_name,
        unique_key,
        ExtraArgs={
            "ContentType": content_type,
        },
    )

    s3_url = f"https://{bucket_name}.s3.{AWS_REGION}.amazonaws.com/{unique_key}"
    return s3_url


def delete_file_from_s3(file_url: str, is_video: bool = True) -> bool:
    if not file_url:
        return False

    bucket_name = AWS_BUCKET_VIDEOS if is_video else AWS_BUCKET_IMAGES
    try:
        key = file_url.split("/")[-1]
        s3_client = get_s3_client()
        s3_client.delete_object(Bucket=bucket_name, Key=key)
        return True
    except Exception as e:
        print(f"Error al eliminar de AWS S3 ({file_url}): {e}")
        return False
