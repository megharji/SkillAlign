from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth_routers import auth_routers
from app.routes.hr_routers import hr_routers
from app.routes.seeker_router import seeker_router
from app.common.config import Base, engine
from app.models import *
app = FastAPI(title="SkillAlign")

# ✅ Create all tables
app.on_event("startup")
def on_startup():
    Base.metadata.create_all(bind=engine)



# ✅ CORS (Vite frontend: http://localhost:5173)
origins = [
    "http://localhost:5173",
    "http://localhost:5174",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,        # ✅ specify frontend origins
    allow_credentials=True,
    allow_methods=["*"],          # ✅ allow OPTIONS/POST/GET etc
    allow_headers=["*"],          # ✅ allow Content-Type, Authorization etc
)

# Include routers for different modules
app.include_router(auth_routers, prefix="/auth_routers", tags=["Auth Routers"])
app.include_router(hr_routers, prefix="/hr_routers", tags=["HR Routers"])
app.include_router(seeker_router, prefix="/seeker_router", tags=["Seeker Routers"])

@app.get("/")
def home():
    return {"ok": True}
