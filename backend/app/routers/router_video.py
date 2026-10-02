from typing import Optional
from fastapi import APIRouter, HTTPException, status, Form, File, UploadFile
from sqlmodel import select, desc
from MyDbContext import SessionDep
from models.model_video import ModelVideo, VideoUpdate, ModelNewVideo
from models.model_comments import ModelCommentCreate, ModelComment
from models.model_users import ModelUser
from services.s3_service import upload_file_to_s3, delete_file_from_s3
from datetime import datetime, timezone

videos = APIRouter(prefix="/videos")

def Existencia(filtro: Optional[ModelVideo], Mensaje: str):
    if filtro is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=Mensaje
        )

@videos.get("/")
def catalagoPrincipal(context: SessionDep):
    statement = (
        select(ModelVideo, ModelUser.nombre)
        .join(ModelUser, ModelVideo.user_id == ModelUser.id, isouter=True)
        .order_by(desc(ModelVideo.created_at))
    )
    results = context.exec(statement).all()

    video_list = []
    for video, user_nombre in results:
        v_dict = video.model_dump()
        v_dict["user_nombre"] = user_nombre or f"Usuario #{video.user_id}"
        video_list.append(v_dict)
    return video_list

@videos.post("/")
def publishVideo(
    context: SessionDep,
    title: str = Form(...),
    description: str = Form(...),
    user_id: int = Form(...),
    video: UploadFile = File(...),
    thumbnail: UploadFile = File(...),
):
    try:
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
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al subir archivos a AWS S3: {str(e)}"
        )

    newVideo = ModelVideo(
        title=title,
        description=description,
        video_url=video_url,
        thumbnail_url=thumbnail_url,
        user_id=user_id,
        created_at=datetime.now(timezone.utc),
    )

    context.add(newVideo)
    context.commit()
    context.refresh(newVideo)

    user = context.exec(select(ModelUser).where(ModelUser.id == user_id)).first()
    v_dict = newVideo.model_dump()
    v_dict["user_nombre"] = user.nombre if user else f"Usuario #{user_id}"
    return v_dict

@videos.get("/{id}")
def playVideo(context: SessionDep, id: int):
    statement = (
        select(ModelVideo, ModelUser.nombre)
        .join(ModelUser, ModelVideo.user_id == ModelUser.id, isouter=True)
        .where(ModelVideo.id == id)
    )
    result = context.exec(statement).first()
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Video no existe"
        )

    filtro, user_nombre = result
    filtro.views += 1

    context.add(filtro)
    context.commit()
    context.refresh(filtro)

    v_dict = filtro.model_dump()
    v_dict["user_nombre"] = user_nombre or f"Usuario #{filtro.user_id}"
    return v_dict

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

    user = context.exec(select(ModelUser).where(ModelUser.id == filtro.user_id)).first()
    v_dict = filtro.model_dump()
    v_dict["user_nombre"] = user.nombre if user else f"Usuario #{filtro.user_id}"
    return v_dict

@videos.delete("/{id}")
def deletedVideo(context: SessionDep, id: int):
    filtro = context.exec(select(ModelVideo).where(ModelVideo.id == id)).first()
    Existencia(filtro, "Video no encontrado")

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

    user = context.exec(select(ModelUser).where(ModelUser.id == data.user_id)).first()
    c_dict = newComent.model_dump()
    c_dict["user_nombre"] = user.nombre if user else f"Usuario #{data.user_id}"
    return c_dict

@videos.get("/{id}/comments")
def viewComments(id: int, context: SessionDep):
    statement = (
        select(ModelComment, ModelUser.nombre)
        .join(ModelUser, ModelComment.user_id == ModelUser.id, isouter=True)
        .where(ModelComment.video_id == id)
        .order_by(desc(ModelComment.created_at))
    )
    results = context.exec(statement).all()

    comments_list = []
    for comment, user_nombre in results:
        c_dict = comment.model_dump()
        c_dict["user_nombre"] = user_nombre or f"Usuario #{comment.user_id}"
        comments_list.append(c_dict)
    return comments_list

@videos.get("/{id}/recommended")
def videosRecommendation(id: int, context: SessionDep):
    statement = (
        select(ModelVideo, ModelUser.nombre)
        .join(ModelUser, ModelVideo.user_id == ModelUser.id, isouter=True)
        .where(ModelVideo.id != id)
        .limit(5)
    )
    results = context.exec(statement).all()

    video_list = []
    for video, user_nombre in results:
        v_dict = video.model_dump()
        v_dict["user_nombre"] = user_nombre or f"Usuario #{video.user_id}"
        video_list.append(v_dict)
    return video_list