from sqlmodel import SQLModel, Field

class LoginRegister (SQLModel, table= True):
    id: int | None = Field (primary_key=True, default=None)
    nombre: str
    correo: str = Field(index=True, unique=True)
    password: str

class Login (SQLModel):
    correo: str
    password: str

class Register (SQLModel):
    nombre: str
    correo: str
    password: str