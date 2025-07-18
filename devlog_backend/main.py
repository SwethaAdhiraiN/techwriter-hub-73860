from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from .routers import auth, posts, comments, reactions, search, profile, realtime

load_dotenv()

app = FastAPI(
    title="DevLog API",
    description="Backend REST API for DevLog technical blogging platform, supporting auth, posts, comments, reactions, search, profiles, and real-time features.",
    version="1.0.0",
    openapi_tags=[
        {"name": "auth", "description": "User authentication"},
        {"name": "posts", "description": "Blog post CRUD"},
        {"name": "comments", "description": "Commenting and real-time"},
        {"name": "reactions", "description": "Likes, reactions"},
        {"name": "profile", "description": "User profile features"},
        {"name": "search", "description": "Search and filter"},
        {"name": "realtime", "description": "WebSocket real-time APIs"},
    ]
)

origins = [
    os.getenv("FRONTEND_URL", "http://localhost:3000"),
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.include_router(auth.router)
app.include_router(posts.router)
app.include_router(comments.router)
app.include_router(reactions.router)
app.include_router(profile.router)
app.include_router(search.router)
app.include_router(realtime.router)
