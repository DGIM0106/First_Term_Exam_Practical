from fastapi import FastAPI, APIRouter, HTTPException, status
from sqlmodel import select, desc
from MyDbContext import SessionDep
from models.model_video import ModelVideo, VideoUpdate, ModelNewVideo
from models.model_comments import ModelCommentCreate, ModelComment


videos = APIRouter(prefix="/videos")

def Existencia(filtro: ModelVideo, Mensaje: str):
    if filtro is None:
        raise HTTPException(
            status_code= status.HTTP_404_NOT_FOUND,
            detail=Mensaje
        )

@videos.get("/")
def catalagoPrincipal(context: SessionDep):
    filtro = context.exec(select(ModelVideo).order_by(desc(ModelVideo.created_at))).all()
    return filtro

@videos.post("/")
def publishVideo(context: SessionDep, data: ModelNewVideo):
    newVideo = ModelVideo(
        title= data.title,
        description= data.description,
        video_url= data.video_url,
        thumbnail_url= data.thumbnail_url,
        user_id= data.user_id
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
    filtro =  context.exec(select(ModelVideo).where(ModelVideo.id == id)).first()
    Existencia(filtro, "Video no encontrado")
    context.delete(filtro)
    context.commit()

    return {"message":"Video Borrado"}

        
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