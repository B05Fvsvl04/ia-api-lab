from fastapi import FastAPI
from app.api.routes import auth, profile

app = FastAPI(title="Auth API")

app.include_router(auth.router, prefix="/api")
app.include_router(profile.router, prefix="/api")
