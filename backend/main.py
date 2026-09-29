from fastapi import FastAPI
from MyDbContext import create_all_tables
from app.routers import router_register_login

app = FastAPI(lifespan=create_all_tables)

app.include_router(router_register_login.auth)

