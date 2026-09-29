from fastapi import APIRouter
from models.model_registro_login import Login, Register, LoginRegister
from MyDbContext import SessionDep
from sqlmodel import select

auth = APIRouter (prefix="/auth")

@auth.post("/")
def Revisar(session: SessionDep):
    revisar = session.exec(select(Register)).all()
    return revisar

#crear o register
@auth.post("/register")
def RegisterNewUser(session: SessionDep, data: Register):
    estado = select(LoginRegister).where(LoginRegister.correo == data.correo)
    filtro = session.exec(estado).first()
    if filtro:
        return {"el correo ya esta vinculado a otra correo", filtro.correo}

    newRegister = LoginRegister(
        nombre=data.nombre,
        correo=data.correo,
        password=data.password
    )

    session.Add(newRegister)
    session.commit()
    session.refresh(newRegister)
    return newRegister
