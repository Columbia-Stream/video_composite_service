from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from resources.video_resource import router as video_router
from dotenv import load_dotenv
import os

# Load env
env_path = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(dotenv_path=env_path)

app = FastAPI(title="Videos Composite Microservice", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # internal services only; okay for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(video_router)

@app.get("/")
def root():
    return {"message": "Videos Composite Microservice running"}

@app.get("/healthz")
def health():
    return {"ok": True}
