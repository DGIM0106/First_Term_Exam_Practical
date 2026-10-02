from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from MyDbContext import create_all_tables
from app.routers import router_video
from app.routers import router_users

app = FastAPI(lifespan=create_all_tables)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(router_users.auth)
app.include_router(router_video.videos)