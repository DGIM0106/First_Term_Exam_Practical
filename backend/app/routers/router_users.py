from fastapi import APIRouter, HTTPException, status
from models.model_users import ModelLogin, ModelRegister, ModelUser
from MyDbContext import SessionDep
from sqlmodel import select

auth = APIRouter(prefix="/auth")

@auth.get("/")
def test(session: SessionDep):
    revisar = session.exec(select(ModelUser)).all()
    return revisar

@auth.post("/register")
def registerNewUser(session: SessionDep, context: ModelRegister):
    estado = select(ModelUser).where(ModelUser.correo == context.correo)
    filtro = session.exec(estado).first()
    if filtro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El correo ya se encuetra registrado"
        )

    newRegister = ModelUser(
        nombre=context.nombre,
        correo=context.correo,
        password=context.password
    )

    session.add(newRegister)
    session.commit()
    session.refresh(newRegister)
    return newRegister

@auth.post("/login")
def loginUser(session: SessionDep, context: ModelLogin): 
    statement = select(ModelUser).where(ModelUser.correo == context.correo, ModelUser.password == context.password)
    filtro = session.exec(statement).first()
    if not filtro:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    return {"message": "Login exitoso", "user_id": filtro.id, "nombre": filtro.nombre}
