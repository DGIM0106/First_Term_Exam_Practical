from typing import Optional
from fastapi import APIRouter, HTTPException, status, Form, File, UploadFile
from sqlmodel import select, desc
from MyDbContext import SessionDep
from models.model_video import ModelVideo, VideoUpdate, ModelNewVideo
from models.model_comments import ModelCommentCreate, ModelComment
from services.s3_service import upload_file_to_s3, delete_file_from_s3

videos = APIRouter(prefix="/videos")

def Existencia(filtro: ModelVideo, Mensaje: str):
    if filtro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Mensaje
        )

@videos.get("/")
def catalagoPrincipal(context: SessionDep):
    filtro = context.exec(select(ModelVideo).order_by(desc(ModelVideo.created_at))).all()
    return filtro

@videos.post("/")
def publishVideo(
    context: SessionDep,
    title: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    user_id: Optional[int] = Form(None),
    video: Optional[UploadFile] = File(None),
    thumbnail: Optional[UploadFile] = File(None),
    json_data: Optional[ModelNewVideo] = None,
):
    """
    Publica un nuevo video procesando los archivos subidos (video e imagen miniatura)
    a AWS S3 mediante el servicio s3_service.
    """
    # Si viene como multipart/form-data con archivos subidos
    if video and thumbnail and title and description and user_id is not None:
        video_url = upload_file_to_s3(
            file_obj=video.file,
            filename=video.filename or "video.mp4",
            content_type=video.content_type or "video/mp4",
            is_video=True,
        )
        thumbnail_url = upload_file_to_s3(
            file_obj=thumbnail.file,
            filename=thumbnail.filename or "thumbnail.jpg",
            content_type=thumbnail.content_type or "image/jpeg",
            is_video=False,
        )

        newVideo = ModelVideo(
            title=title,
            description=description,
            video_url=video_url,
            thumbnail_url=thumbnail_url,
            user_id=user_id,
        )
    # Si se envía como JSON (ModelNewVideo)
    elif json_data:
        newVideo = ModelVideo(
            title=json_data.title,
            description=json_data.description,
            video_url=json_data.video_url,
            thumbnail_url=json_data.thumbnail_url,
            user_id=json_data.user_id,
        )
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Se requieren los archivos de video y miniatura junto con título, descripción y user_id.",
        )

    context.add(newVideo)
    context.commit()
    context.refresh(newVideo)
    return newVideo

@videos.get("/{id}")
def playVideo(context: SessionDep, id: int):
    filtro = context.exec(select(ModelVideo).where(ModelVideo.id == id)).first()
    Existencia(filtro, "Video no existe")
    filtro.views += 1

    context.add(filtro)
    context.commit()
    context.refresh(filtro)
    return filtro

@videos.put("/{id}")
def editVideo(context: SessionDep, id: int, data: VideoUpdate):
    filtro = context.exec(select(ModelVideo).where(ModelVideo.id == id)).first()
    Existencia(filtro, "Video no existe")

    if data.title is not None:
        filtro.title = data.title
    if data.description is not None:
        filtro.description = data.description

    context.add(filtro)
    context.commit()
    context.refresh(filtro)

    return filtro

@videos.delete("/{id}")
def deletedVideo(context: SessionDep, id: int):
    filtro = context.exec(select(ModelVideo).where(ModelVideo.id == id)).first()
    Existencia(filtro, "Video no encontrado")

    # Eliminar archivos asociados del bucket de AWS S3 mediante s3_service
    delete_file_from_s3(filtro.video_url, is_video=True)
    delete_file_from_s3(filtro.thumbnail_url, is_video=False)

    context.delete(filtro)
    context.commit()

    return {"message": "Video Borrado"}

@videos.post("/{id}/comments")
def addComments(id: int, data: ModelCommentCreate, context: SessionDep):
    filtro = context.exec(select(ModelVideo).where(ModelVideo.id == id)).first()
    Existencia(filtro, "Error")
    newComent = ModelComment(
        user_id=data.user_id,
        content=data.content,
        video_id=filtro.id
    )
    context.add(newComent)
    context.commit()
    context.refresh(newComent)
    return newComent

@videos.get("/{id}/comments")
def viewComments(id: int, context: SessionDep):
    filtro = context.exec(select(ModelComment).where(ModelComment.video_id == id).order_by(desc(ModelComment.created_at))).all()
    return filtro

@videos.get("/{id}/recommended")
def videosRecommendation(id: int, context: SessionDep):
    filtro = context.exec(select(ModelVideo).where(ModelVideo.id != id).limit(5)).all()
    return filtro