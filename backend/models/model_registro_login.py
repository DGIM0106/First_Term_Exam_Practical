from sqlmodel import SQLModel, Field

class ModelLoginRegister (SQLModel, table= True):
    id: int | None = Field (primary_key=True, default=None)
    nombre: str
    correo: str = Field(index=True, unique=True)
    password: str

class ModelLogin (SQLModel):
    correo: str
    password: str

class ModelRegister (SQLModel):
    nombre: str
    correo: str
    password: str