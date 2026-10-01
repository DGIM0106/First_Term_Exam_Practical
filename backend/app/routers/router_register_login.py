from fastapi import APIRouter, HTTPException, status
from models.model_registro_login import ModelLogin, ModelRegister, ModelLoginRegister
from MyDbContext import SessionDep
from sqlmodel import select

auth = APIRouter (prefix="/auth")

@auth.get("/")
def test(session: SessionDep):
    revisar = session.exec(select(ModelLoginRegister)).all()
    return revisar

#crear o register
@auth.post("/register")
def registerNewUser(session: SessionDep, context: ModelRegister):
    estado = select(ModelLoginRegister).where(ModelLoginRegister.correo == context.correo)
    filtro = session.exec(estado).first()
    if filtro:
        raise HTTPException(
          status_code=status.HTTP_400_BAD_REQUEST,
          detail="El correo ya se encuetra registrado"  
        )

    newRegister = ModelLoginRegister(
        nombre=context.nombre,
        correo=context.correo,
        password=context.password
    )

    session.add(newRegister)
    session.commit()
    session.refresh(newRegister)
    return newRegister

#login 
@auth.post("/login")
def loginUser(session: SessionDep, context: ModelLogin): 
    statement = select(ModelLoginRegister).where(ModelLoginRegister.correo == context.correo, ModelLoginRegister.password == context.password)
    filtro= session.exec(statement).first()
    if not filtro:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales incorrectas"
        )
    
    return {"message": "Login exitoso", "user_id": filtro.id, "nombre": filtro.nombre}

